import wsgiserver
from flask import Flask, jsonify, request
import json
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, LineString
from matplotlib import pyplot as plt

from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.sharedobject import SharedObject

class GCom_Server():
    def __init__(self, so):
        self._so = so

        print("GCom_Server Initialized")

    def serve_forever(self, production=True, HOST="localhost", PORT=9000):
        app = Flask(__name__)

        production_server = wsgiserver.WSGIServer(app, host=HOST, port=PORT)

        #GET endpoints

        @app.route("/queue", methods=["GET"])
        def get_queue():
            ret = self._so.gcom_currentmission_get() # this is a dict of wpq (hopefully)
            formatted = []
            for wp in ret:
                formatted.append(wp.get_asdict())
            retJSON = json.dumps(formatted) # this should convert the dict to JSON

            print("Queue sent to GCom")

            return retJSON

        @app.route("/status", methods=["GET"])
        def get_status():
            ret = self._so.gcom_status_get() # this should be a dict of status (hopefully)
            retJSON = json.dumps(ret) # this should convert the dict to JSON

            print("Status sent to GCom")

            return retJSON

        @app.route("/lock", methods=["GET"])
        def lock():
            status = self._so.gcom_locked_set(True)
            if status:
                print("Locked by GCom")
                return "Mission Queue Locked"

            else:
                print("Lock failed")

                return "Mission Queue Lock Error: Already Locked", 400


        @app.route("/unlock", methods=["GET"])
        def unlock():
            status = self._so.gcom_locked_set(False)
            if status:
                print("unlocked by GCom")

                return "Mission Queue unlocked"
            else:
                print("Unlock failed")

                return "Mission Queue Unlock Error: Already Unlocked", 400


        @app.route("/rtl", methods=["GET"])
        def rtl():
            print("RTL")
            self._so.gcom_rtl_set(True)

            return "Returning to Land"

        @app.route("/land", methods=["GET"])
        def land():
            print("Landing")
            self._so.gcom_landing_set(True)

            return "Landing in Place"


        #VTOL LAND ENDPOINT

        @app.route("/land", methods=["POST"])
        def vtol_land():
            land = request.get_json()
            if not 'latitude' in land or not 'longitude' in land:
                return "Latitude and Longitude cannot be null", 400
            
            self._so.gcom_vtol_land_set(land)

            return "Landing at specified location"

        #POST endpoints

        @app.route("/queue", methods=["POST"])
        def post_queue():
            payload = request.get_json()

            ret = self._so.gcom_status_get()
            last_altitude = ret['altitude'] if ret != () else 50

            wpq = []
            for wpdict in payload:
                if wpdict['altitude'] != None:
                    wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], wpdict['altitude'])
                    wpq.append(wp)
                    last_altitude = wpdict['altitude']
                else:
                    wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude)
                    wpq.append(wp)
            
            self._so.gcom_newmission_set(WaypointQueue(wpq.copy()))

            wpq.clear()

            return "ok"
    
        @app.route("/takeoff", methods=["POST"])
        def takeoff():
            payload = request.get_json()

            if not('altitude' in payload):
                return "Altitude cannot be null", 400

            altitude = int(payload['altitude'])
            print(f"Taking off to altitude {altitude}")
            self._so.gcom_takeoffalt_set(altitude)

            return "Takeoff command received"

        @app.route("/home", methods=["POST"])
        def home():
            home = request.get_json()

            if 'longitude' not in home or 'latitude' not in home or 'altitude' not in home:
                return "Long/lat/alt cannot be null", 400

            self._so.gcom_newhome_set(home)

            return "Setting New Home"
        
        #VTOL endpoints
        @app.route("/vtol/transition", methods=["GET", "POST"])
        def vtol_transition():
            if request.method == "GET":
                return json.dumps({'mode': self._so.mps_vtol_get()})
            
            elif request.method == "POST":
                payload = request.get_json(silent=True)
                mode = int(payload['mode'])
                if mode == 3 or mode == 4:
                    self._so.gcom_vtol_set(mode)
                    return "Changing flight mode"
                else:
                    return "Invalid flight mode", 400
            
            return "Bad Request", 400

        #Fence inclusion/exclusion methods...

        @app.route("/fence/inclusive", methods=["POST"])
        def fence_inclusive():
            fence = request.get_json()

            self._so.gcom_fence_set({"inex":False, "type":"circle", "center":fence['center'], "radius":fence['radius']})

            return "Inclusive Fence Set"
        
        @app.route("/fence/exclusive", methods=["POST"])
        def fence_exclusive():
            fence = request.get_json()

            self._so.gcom_fence_set({"inex":True, "type":"circle", "center":fence['center'], "radius":fence['radius']})

            return "Exclusive Fence Set"
        
<<<<<<< HEAD

        #FENCE DIVERSION METHOD (BIG BOY)
        @app.route("/diversion", methods=["POST"])
        def fence_diversion():
            self._so.gcom_locked_set(True)
            
            fence = request.get_json()

            exclude = fence['exclude']
            target = fence['rejoin_at']

            target_waypoint = Waypoint(0, "", target['latitude'], target['longitude'], 0).get_coords_utm() #get target waypoint in utm
            target_waypoint = Point(target_waypoint[0], target_waypoint[1])

            exclude_waypoints = []
            for wp in exclude:
                wp_utm = Waypoint(0, "", wp['latitude'], wp['longitude'], 0).get_coords_utm() #convert to utm
                exclude_waypoints.append(Point(wp_utm[0], wp_utm[1]))

            #create exclusion fence Multipoint
            exclusion = MultiPoint(exclude_waypoints)
            exclusion_polygon = Polygon(exclude_waypoints)

            #find start_waypoint
            start_waypoint = None
            curr_wpq = [wp.get_coords_utm() for wp in self._so.gcom_currentmission_get()]
            for i in range(len(curr_wpq) - 1):
                path_between = LineString([[curr_wpq[i][0], curr_wpq[i][1]], 
                                          [curr_wpq[i + 1][0], curr_wpq[i + 1][1]]])
                if exclusion_polygon.distance(path_between) == 0:
                    start_waypoint = Point((curr_wpq[i][0], curr_wpq[i][1]))
                    break
            if start_waypoint == None:
                #no intersection
                self._so.gcom_locked_set(False)
                plt.scatter([ex[0] for ex in curr_wpq], [ex[1] for ex in curr_wpq], color='blue')
                plt.scatter([ex.x for ex in exclude_waypoints], [ex.y for ex in exclude_waypoints], color='red')
                plt.show()
                return "No intersection", 200

            #create augmented exclusion zone
            buffered_exclusion = exclusion.buffer(15)
            buffered_convex_verts = list(buffered_exclusion.convex_hull.exterior.coords)

            buffered_convex_verts.append(target_waypoint)
            buffered_convex_verts.append(start_waypoint)
            augmented_exclusion = MultiPoint(buffered_convex_verts)
        
            #create convex hull, find vertices
            convex_hull = augmented_exclusion.convex_hull
            augmented_convex_verts = list(convex_hull.exterior.coords)

            #calculate drone paths...
            direct_path = LineString([start_waypoint, target_waypoint])

            #plot drone paths with pyplot
            x, y = direct_path.xy
            plt.plot(x, y, color='blue', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
            plt.scatter([ex[0] for ex in curr_wpq], [ex[1] for ex in curr_wpq], color='blue')
            plt.scatter([ex.x for ex in exclude_waypoints], [ex.y for ex in exclude_waypoints], color='red')
            plt.scatter([aug[0] for aug in augmented_convex_verts], [aug[1] for aug in augmented_convex_verts], color='orange')
            plt.show()


            self._so.gcom_locked_set(False)
            return "diverting"
=======
        #diversion algorithm endpoint
        @app.route("/diversion", methods=["POST"])
        def diversion():
            payload = request.get_json()

            exclusions = payload["exclude"]
            
            avg_lat: float = 0
            avg_lon: float = 0

            count: int = 0

            for wp in exclusions:
                avg_lat += wp['latitude']
                avg_lon += wp['longitude']
                count += 1
            
            avg_lat /= count
            avg_lon /= count

            #find waypoint that is furthest from the average
            furthest = 0
            furthest_wp = None
            for wp in exclusions:
                dist = ((wp['latitude'] - avg_lat)**2 + (wp['longitude'] - avg_lon)**2)**0.5
                if dist > furthest:
                    furthest = dist
                    furthest_wp = wp

            avg_lon = float(f"{avg_lon:.6f}") 
            avg_lat = float(f"{avg_lat:.6f}")

            return f"Diversion algorithm received - avg lng,lat = ({avg_lon},{avg_lat}) furthest_wp: {furthest_wp}"

        app.config
>>>>>>> b056efbc12caae9bc1c7bcb5bf9abd0699df4b91
        
        #end of endpoints

        #run server
        if production:
            production_server.start()
        else:
            app.run(port=PORT)
