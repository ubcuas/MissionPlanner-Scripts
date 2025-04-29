from collections.abc import Callable

from pymavlink import mavutil

class Callback():
    def __init__(
            self, 
            name: str,
            trigger_message_type: str, 
            trigger_condition: Callable = (lambda curr_msg, prev_msg: True), 
            payload: Callable = (lambda msg, conn, state: print(msg)),
            only_once: bool = True
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
        `only_once`: indicates that the callback should only execute once, i.e. it will be removed
            after being triggered for the first and only time.
        """

        self.name = name
        self.trigger_message_type = trigger_message_type
        self.trigger_condition = trigger_condition
        self.payload = payload
        self.only_once = only_once

class CallbackSystem():
    def __init__(self, mav_connection: mavutil.mavfile, state: dict):
        self.conn = mav_connection
        self.state = state

        self.callbacks: dict[str, list[Callback]] = {}
        self.prev_messages: dict[str, object] = {}
    
    def update_and_check(self, latest_messages: dict):
        # traverse through all callbacks and check each of their triggers
        print(f"DEBUG: update_and_check called")
        for callback_type, callback_list in self.callbacks.items():
            prev_msg = self.prev_messages.get(callback_type, None)
            curr_msg = latest_messages.get(callback_type, None)

            if curr_msg == None:
                # no point testing
                continue

            for callback in callback_list:
                print(f"DEBUG: testing callback {callback.name}")
                if callback.trigger_condition(curr_msg, prev_msg):

                    if callback.only_once:
                        # remove callback before firing it
                        self.callbacks[callback_type].remove(callback)

                    # fire callback
                    callback.payload(curr_msg, self.conn, self.state)

                    print(f"DEBUG: Fired Callback {callback.name}")

        # update prev_messages
        self.prev_messages.update(latest_messages)

    def register_callback(self, callback: Callback):
        print(f"DEBUG: registering {callback.name}")
        if callback.trigger_message_type not in self.callbacks.keys():
            self.callbacks[callback.trigger_message_type] = []
        self.callbacks.get(callback.trigger_message_type).append(callback)

    # def unregister_callback(self, name: str, trigger_message_type: int):
    #     pass