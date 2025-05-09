from collections.abc import Callable

from pymavlink import mavutil

class Callback():
    def __init__(
            self, 
            name: str,
            trigger_message_type: str, 
            trigger_condition: Callable = (lambda curr_msg, prev_msg: True), 
            payload: Callable = (lambda msg, conn, state: print(msg)),
            removable_flags: dict[str, bool] = {
                "on_payload_fired": True,
                "on_mission_switched": True,
                "on_deregister_called": True,
            }
        ):
        """
        A callback instance. Callbacks are composed of two components - the trigger, which controls
        when and how the callback fires, and the payload, which contains the code to run. 
        
        Parameters:
        `name`: A name to help disambiguate the callback.
        `trigger_message_type`: mavlink message type that triggers the callback, 
            e.g. `'GLOBAL_POSITION_INT'`
        `trigger_condition`: a function that should take in mavlink messages of the designated 
            trigger type and return a boolean that indicates whether or not the callback should
            fire on that message. 
            Also has access to the previous message of that time seen by the callback system. An 
            example of how this can be used is triggering specifically on the transition between
            waypoints 2 -> 3. 
            Functions must be able to handle cases where prev_msg is `None`.
            If unspecified, a function that will always return `True` will be used - i.e., the 
            callback will fire on every message of the correct type.
        `payload`: a function that contains the desired logic to run when the callback fires.
            Has access to the message it was triggered on, the `mavlink_connection` object, and 
            a state dictionary owned by the MPS server instance itself (for passing information
            back to the wider server context.) 
            If unspecified, a default function will be used that simply prints the message.
        `removable`: a dictionary with boolean flags indicating the conditions under which the 
            callback can be deleted/removed/deregistered.
            `on_payload_fired`: indicates that the callback will be removed after being triggered
                for the first and only time, i.e., it will only execute once.
            `on_mission_switched`: indicates that the callback will be removed when the mission
                is switched/updated, i.e., the callback is mission-specific and it would be 
                invalid for that callback to persist if the mission was switched before it was
                executed.
            `on_deregister_called`: indicates that the callback can be removed through the
                Callback System's deregistration functions.
            A Callback with all three of these flags set to `False` will be effectively permanent.
        """

        self.name = name
        self.trigger_message_type = trigger_message_type
        self.trigger_condition = trigger_condition
        self.payload = payload

        self.removable_flags = {
            "on_payload_fired": True,
            "on_mission_switched": True,
            "on_deregister_called": True,
        }
        self.removable_flags.update(removable_flags)

class CallbackSystem():
    def __init__(self, mav_connection: mavutil.mavfile, state: dict):
        self.conn = mav_connection
        self.state = state

        self.callbacks: dict[str, list[Callback]] = {}
        self.prev_messages: dict[str, object] = {}

    def __check_exec_indicate_removal(self, callback: Callback, curr_msg, prev_msg) -> bool:
        """
        Checks the callback's trigger condition and executes if it passes.
        Returns a boolean that indicates if the callback should be removed.
        """
        print(f"DEBUG: testing callback {callback.name}")

        keep = True

        if callback.trigger_condition(curr_msg, prev_msg):

            if callback.removable_flags.get("on_payload_fired"):
                # remove callback before firing it
                keep = False

            # fire callback
            callback.payload(curr_msg, self.conn, self.state)

            print(f"DEBUG: Fired Callback {callback.name}")
        
        return keep
    
    def update_and_check(self, latest_messages: dict):
        # traverse through all callbacks and check each of their triggers
        for callback_type, callback_list in self.callbacks.items():
            prev_msg = self.prev_messages.get(callback_type, None)
            curr_msg = latest_messages.get(callback_type, None)

            if curr_msg == None:
                # no point testing
                continue

            # check every callback in the list, filtering out those that get removed
            self.callbacks[callback_type] = list(filter(
                lambda callback: self.__check_exec_indicate_removal(callback, curr_msg, prev_msg), 
                callback_list
            ))

        # update prev_messages
        self.prev_messages.update(latest_messages)

    def register_callback(self, callback: Callback):
        print(f"DEBUG: registering {callback.name}")
        if callback.trigger_message_type not in self.callbacks.keys():
            self.callbacks[callback.trigger_message_type] = []
        self.callbacks.get(callback.trigger_message_type).append(callback)

    def deregister_callback(self, name: str):
        self.deregister_callback_by_condition(lambda callback: (name == callback.name))

    def deregister_callback_by_condition(self, condition: Callable = (lambda callback: False)):
        for callback_type, callback_list in self.callbacks.items():
            # filter the list of callbacks, keeping only those who cannot be deregistered directly
            # through methods and those for whom the condition evaluates to False.
            self.callbacks[callback_type] = list(filter(
                lambda callback: (callback.removable_flags.get("on_deregister_called") and not condition(callback)),
                callback_list
            ))
    
    def mission_switched(self):
        """
        The mission switched, so deregister all callbacks for which `self.removable_flags["on_mission_switched"]` is `True`.
        """

        print("DEBUG: Clearing Callbacks on Mission Switch")

        for callback_type, callback_list in self.callbacks.items():
            # filter out all callbacks that are set to expire on mission switch
            self.callbacks[callback_type] = list(filter(
                lambda callback: not callback.removable_flags.get("on_mission_switched"),
                callback_list
            ))