from flask import Flask, request
from flask_cors import CORS, cross_origin
import json
from shapely.geometry import Point, Polygon, MultiPoint, LineString
from matplotlib import pyplot as plt
import time
from flask_socketio import SocketIO

from server.common.conversion import *
from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.status import Status
from server.common.sharedobject import SharedObject
from server.common.encoders import command_string_to_int, command_int_to_string

def plot_shape(points, color, close=False, scatter=True):
    adjust = 0 if close else 1

    #plot points
    if scatter:
        plt.scatter([pt[0] for pt in points], [pt[1] for pt in points], color=color)

    #plot connecting lines
    for i in range(len(points) - adjust):
        curr = points[i]
        next = points[(i + 1) % len(points)]
        plt.plot([curr[0], next[0]], [curr[1], next[1]], color=color, alpha=0.7, linewidth=1, zorder=2)

class GCOM_Server():
    def __init__(self, so):
        self._so: SharedObject = so

        #print("GCOM_Server Initialized")

    def serve_forever(self, production=True, HOST="localhost", PORT=9000):
        print("GCOM HTTP Server starting...")
        app = Flask(__name__)
        CORS(app)
        cors = CORS(app)
        app.config['CORS_HEADERS'] = 'Content-Type'
        socketio = SocketIO(app)

        # GET endpoints
        @app.route("/", methods=["GET"])
        @cross_origin()
        def index():
            return "GCOM Server Running", 200

        @app.route("/queue", methods=["GET"])
        @cross_origin()
        def get_queue():
            self._so.gcom_currentmission_trigger_update()
            while self._so._currentmission_flg_ready == False:
                time.sleep(0.01)

            ret = self._so.gcom_currentmission_get() # This is a dict of wpq (hopefully)
            formatted = []
            for wp in ret:
                wp_dict = wp.get_asdict()
                wp_dict.update(wp.get_command())
                formatted.append(wp_dict)
            
            wpno = int(self._so.get_status()._wpn)
            remaining = formatted[wpno-1:]
            retJSON = json.dumps(remaining) # This should convert the dict to JSON

            print("Queue sent to GCOM")

            return retJSON

        @app.route("/status", methods=["GET"])
        @cross_origin()
        def get_status():
            ret: Status = self._so.get_status()
            retJSON = json.dumps(ret.as_dictionary())

            print("Status sent to GCOM")

            return retJSON

        @app.route("/land", methods=["GET"])
        @cross_origin()
        def land():
            print("Landing")
            self._so.flightmode_set("loiter")
            self._so.gcom_landing_set(True)

            return "Landing in Place", 200

        @app.route("/rtl", methods=["GET", "POST"])
        @cross_origin()
        def rtl():
            altitude = request.get_json().get('altitude', 50)

            print(f"RTL at {altitude}")
            self._so.gcom_rtl_set(altitude)

            return "Returning to Launch", 200

        # VTOL LAND ENDPOINT

        @app.route("/land", methods=["POST"])
        @cross_origin()
        def vtol_land():
            land = request.get_json()
            if not 'latitude' in land or not 'longitude' in land:
                return "Latitude and Longitude cannot be null", 400
            
            self._so.gcom_vtol_land_set(land)

            return "Landing at specified location", 200

        # POST endpoints

        @app.route("/queue", methods=["POST"])
        @cross_origin()
        def post_queue():
            payload = request.get_json()

            ret: Status = self._so.get_status()
            last_altitude = ret._alt if ret != () else 50

            wpq = []
            for wpdict in payload:
                altitude = wpdict.get('altitude')
                if altitude != None:
                    last_altitude = altitude
                else:
                    altitude = last_altitude

                command = wpdict.get('command', "WAYPOINT") 
                # converts any unknown waypoint types to WAYPOINT
                command = command_int_to_string(command_string_to_int(command))

                param1 = wpdict.get('param1', 0)
                param2 = wpdict.get('param2', 0)
                param3 = wpdict.get('param3', 0)
                param4 = wpdict.get('param4', 0)
                
                wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude, 
                              command, param1, param2, param3, param4)
                wpq.append(wp)
            
            self._so.gcom_newmission_set(WaypointQueue(wpq.copy()))
            copy = WaypointQueue(wpq.copy()).aslist()
            wpq.clear()

            return "ok", 200
        
        @app.route("/insert", methods=['POST'])
        @cross_origin()
        def insert_wp():
            payload = request.get_json()

            ret: Status = self._so.get_status()
            last_altitude = ret._alt if ret != () else 50

            # gets new waypoints
            new_waypoints = []
            for wpdict in payload:
                altitude = wpdict.get('altitude')
                if altitude != None:
                    last_altitude = altitude
                else:
                    altitude = last_altitude

                command = wpdict.get('command', "WAYPOINT") 
                # converts any unknown waypoint types to WAYPOINT
                command = command_int_to_string(command_string_to_int(command))

                param1 = wpdict.get('param1', 0)
                param2 = wpdict.get('param2', 0)
                param3 = wpdict.get('param3', 0)
                param4 = wpdict.get('param4', 0)
                
                wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude, 
                              command, param1, param2, param3, param4)
                new_waypoints.append(wp)
            
            # insert new waypoints start at index
            self._so.gcom_newinsert_set(WaypointQueue(new_waypoints.copy()))
            copy = WaypointQueue(new_waypoints.copy()).aslist()
            new_waypoints.clear()

            return "ok", 200
        
        @app.route("/clear", methods=['GET'])
        @cross_origin()
        def clear_queue():
            self._so.gcom_newmission_set(WaypointQueue([]))

            return "ok", 200
    
        @app.route("/takeoff", methods=["POST"])
        @cross_origin()
        def takeoff():
            payload = request.get_json()

            if not('altitude' in payload):
                return "Altitude cannot be null", 400

            altitude = int(payload['altitude'])
            print(f"Taking off to altitude {altitude}")
            self._so.gcom_takeoffalt_set(altitude)

            result = None 
            while result == None:
                result = self._so.takeoff_get_result()
                time.sleep(0.05)
            
            if result == 1:
                return "Takeoff command received", 200
            else:
                return "Takeoff unsuccessful", 400

        @app.route("/home", methods=["POST"])
        @cross_origin()
        def home():
            home = request.get_json()

            if 'longitude' not in home or 'latitude' not in home or 'altitude' not in home:
                return "Long/lat/alt cannot be null", 400

            self._so.gcom_newhome_set(home)

            return "Setting New Home", 200
        
        # VTOL endpoints
        @app.route("/vtol/transition", methods=["GET", "POST"])
        @cross_origin()
        def vtol_transition():
            if request.method == "GET":
                return json.dumps({'mode': self._so.mps_vtol_get()})
            
            elif request.method == "POST":
                payload = request.get_json(silent=True)
                mode = int(payload['mode'])
                if mode == 3 or mode == 4:
                    self._so.gcom_vtol_set(mode)
                    return "Changing flight mode", 200
                else:
                    return "Invalid flight mode", 400
            
            return "Bad Request", 400

        # FENCE DIVERSION METHOD (BIG BOY)
        @app.route("/diversion", methods=["POST"])
        @cross_origin()
        def fence_diversion():
            self._so.gcom_locked_set(True)
            
            fence = request.get_json()

            exclude = fence['exclude']
            target = fence['rejoin_at']

            targetwp = Waypoint(0, "", target['latitude'], target['longitude'], 0)
            target_waypoint = targetwp.get_coords_utm() #get target waypoint in utm
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
                    start_waypoint_index = i
                    break
            if start_waypoint == None:
                #no intersection
                self._so.gcom_locked_set(False)

                #original mission waypoints
                plot_shape(curr_wpq, 'blue', False)
                #exclusion zone
                plot_shape([(ex.x, ex.y) for ex in exclude_waypoints], 'red', True)

                ax = plt.gca()
                ax.set_aspect('equal', adjustable='box')
                plt.savefig('no-diversion.png')
                #plt.show()

                return "No intersection", 200

            #create augmented exclusion zone
            buffered_exclusion = exclusion.buffer(20, quad_segs=5, cap_style='square', join_style='mitre', mitre_limit=20)
            buffered_convex_verts = list(buffered_exclusion.convex_hull.exterior.coords)

            buffered_convex_verts.append(target_waypoint)
            buffered_convex_verts.append(start_waypoint)
            augmented_exclusion = MultiPoint(buffered_convex_verts)
        
            #create convex hull, find vertices
            convex_hull = augmented_exclusion.convex_hull
            augmented_convex_verts = list(convex_hull.exterior.coords)

            #separate drone paths...
            path_vertices = {False:[], True:[]}
            current_path = False
            prepend = False
            prepend_list = []
            for aug in augmented_convex_verts:
                #if aug is a start/end waypoint, switch between paths
                if (aug[0] == start_waypoint.x and aug[1] == start_waypoint.y) or (aug[0] == target_waypoint.x and aug[1] == target_waypoint.y):
                    path_vertices[current_path].append(aug)
                    current_path = not current_path
                    if not current_path:
                        #if current_path returns to false
                        prepend = True
                
                #count line segment between current aug and next vertex as part of current path
                if prepend:
                    prepend_list.append(aug)
                else:
                    path_vertices[current_path].append(aug)
            #prepend prepend_list
            path_vertices[False][:0] = prepend_list

            #unreverse reversed paths
            for path in path_vertices.values():
                if path[0][0] == target_waypoint.x and path[0][1] == target_waypoint.y:
                    path.reverse()

            #calculate path lengths
            path_lengths = {False:0, True:0}
            for path in [False, True]:
                current_path = path_vertices[path]
                length = 0
                for i in range(len(current_path) - 1):
                    current_vertex = current_path[i]
                    next_vertex = current_path[i + 1]
                    segment_length = ((next_vertex[0] - current_vertex[0]) ** 2 + (next_vertex[1] - current_vertex[1]) ** 2) ** 0.5
                    length += segment_length
                path_lengths[path] = length
            
            shorter_path = (path_lengths[True] < path_lengths[False])

            #plot information with pyplot
            #direct path
            direct_path = LineString([start_waypoint, target_waypoint])
            x, y = direct_path.xy
            plt.plot(x, y, color='blue', alpha=0.7, linewidth=2, solid_capstyle='round', zorder=2)
            #original mission waypoints
            plot_shape(curr_wpq, 'blue', False)
            #exclusion zone
            plot_shape([(ex.x, ex.y) for ex in exclude_waypoints], 'red', True)
            #augmented exclusion zone
            plt.scatter([aug[0] for aug in augmented_convex_verts], [aug[1] for aug in augmented_convex_verts], color='orange')
            #shorter path in lime
            plot_shape(path_vertices[shorter_path], 'lime', False, False)
            #other path in green
            plot_shape(path_vertices[not shorter_path], 'green', False, False)

            ax = plt.gca()
            ax.set_aspect('equal', adjustable='box')
            plt.savefig('diversion.png')
            #plt.show()

            #construct diverted waypoint queue
            original_queue = self._so.gcom_currentmission_get()
            diverted_queue = []

            #same as original, up to and not including the start waypoint
            diverted_queue.extend([wp for wp in original_queue[:start_waypoint_index]])
            
            #obtain altitude, UTM zone, and hemisphere of start_waypoint to use for diverted path
            start_wp = original_queue[start_waypoint_index]
            start_waypoint_alt = start_wp._alt
            start_waypoint_zone = convert_gps_to_utm_zone(start_wp._lng)
            start_waypoint_hemi = 1 if start_wp._lat >= 0 else -1
            #add diversion paths to queue
            for i in range(len(path_vertices[shorter_path])):
                current_vertex = path_vertices[shorter_path][i]
                vertex_latlng = convert_utm_to_gps(current_vertex[0], current_vertex[1], start_waypoint_zone, start_waypoint_hemi)
                diverted_queue.append(Waypoint(-i, f"diversion-{i}", vertex_latlng[0], vertex_latlng[1], start_waypoint_alt))

            #determine index of target wp
            for i in range(len(original_queue)):
                target_waypoint_index = i
                if original_queue[i].distance(targetwp, False) < 0.1:
                    break

            #extend with rest of the original queue
            diverted_queue.extend([wp for wp in original_queue[target_waypoint_index:]])

            #send diverted queue to client as new mission
            self._so.gcom_newmission_set(WaypointQueue(diverted_queue.copy()))
            diverted_queue.clear()

            self._so.gcom_locked_set(False)
            return "diverting"
        
        @app.route("/flightmode", methods=["PUT"])
        @cross_origin()
        def change_flight_mode():
            input = request.get_json()
            
            if input['mode'] in ['loiter', 'stabilize', 'auto', 'guided']:
                self._so.flightmode_set(input['mode'])
                return f"OK! Changed mode: {input['mode']}", 200
            elif input['mode'] in ['vtol', 'plane']:
                print("changing mode")
                self._so.flightConfig_set(input['mode'])
                return f"OK! Changed mode: {input['mode']}", 200
            else:
                return f"Unrecognized mode: {input['mode']}", 400
        
        @app.route("/arm", methods=["PUT"])
        @cross_origin()
        def arm_disarm_drone():
            input = request.get_json()

            if input['arm'] in [1, 0]:
                print(f"arming {int(input['arm'])}")
                self._so.arm_set(int(input['arm']))

                result = None
                while result == None:
                    result = self._so.arm_get_result()
                    time.sleep(0.05)
                
                if result == 1:
                    return f"OK! {'Armed drone' if input['arm'] else 'Disarmed drone'}", 200
                else:
                    return f"Arm/disarm failed - drone is NOT in the requested state", 418
            else:
                return f"Unrecognized arm/disarm command parameter", 400
        
        @app.route("/altstandard", methods=["PUT"])
        @cross_origin()
        def altstandard():
            #Call into altitude_standard_set
            return "UNIMPLMENTED", 410
        
        #Socket stuff
        @socketio.on("connect")
        def handle_connect():
            print("Client connected to socket")
            socketio.emit('okay', {'data': 'Connected'})

        @socketio.on("disconnect")
        def handle_disconnect():
            print("Client disconnected")

        @socketio.on("message")
        def handle_message(data):
            ret: Status = self._so.get_status()
            retJSON =  json.dumps(ret.as_dictionary())

            print("Status sent to GCOM")
            
            socketio.emit('status_response', {'status_data': retJSON})
            
        #run server
        # if production:
        #     # Option 1: Using gevent and gevent-websocket for production
        #     server = pywsgi.WSGIServer(('0.0.0.0', PORT), app, handler_class=WebSocketHandler)
        #     server.serve_forever()
        # else:
        #     # Option 2: Using socketio.run for development (supports WebSocket)
        #     socketio.start_background_task(background_task)
        socketio.run(app, host='0.0.0.0', port=PORT, debug=True, use_reloader=False)
