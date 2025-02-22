"""
A basic template file for using the Model class in PicoLibrary
This will allow you to implement simple Statemodels with some basic
event-based transitions.
"""

# Import whatever Library classes you need - StateModel is obviously needed
# Counters imported for Timer functionality, Button imported for button events
import time
import random
from Log import *
from StateModel import *
from Counters import *
from Button import *
from Sensors import *
from Buzzer import *
from Lights import *
from Displays import *
from Room import *


"""
This is the template for a Controller - you should rename this class to something
that is supported by your class diagram. This should associate with your other
classes, and any PicoLibrary classes. If you are using Buttons, you will implement
buttonPressed and buttonReleased.

To implement the state model, you will need to implement __init__ and 4 other methods
to support model start, stop, entry actions, exit actions, and state actions.

The following methods must be implemented:
__init__: create instances of your View and Business model classes, create an instance
of the StateModel with the necessary number of states and add the transitions, buttons
and timers that the StateModel needs

stateEntered(self, state, event) - Entry actions
stateLeft(self, state, event) - Exit actions
stateDo(self, state) - do Activities

# A couple other methods are available - but they can be left alone for most purposes

run(self) - runs the State Model - this will start at State 0 and drive the state model
stop(self) - stops the State Model - will stop processing events and stop the timers

This template currently implements a very simple state model that uses a button to
transition from state 0 to state 1 then a 5 second timer to go back to state 0.
"""

class EmergencyRoomController:

    def __init__(self, room_number, capacity_threshold, sensor_pin, buzzer, led_green_pin, led_yellow_pin, led_red_pin, lcd_sda, lcd_scl, button_1_pin, button_2_pin):
        
        # Instantiate whatever classes from your own model that you need to control
        # Handlers can now be set to None - we will add them to the model and it will
        # do the handling
        
        Log.i(f"Initializing Emergency Room Controller for Room {room_number}")
        self.room = Room(room_number, capacity_threshold)
        
        
        # Hardware components
        self.sensor = DigitalSensor(sensor_pin, name="Sensor", lowActive=True)  
        #Sensor: lowAcive = False for wokwi, lowActive = True for demo
        #For some reason in wokwi i am NOT able to stop it from triggering it works fine on hardware.
        self.buzzer = PassiveBuzzer(buzzer, name="Buzzer")
        self.led_green = Light(led_green_pin, "Green LED")  # Green LED for low capacity
        self.led_yellow = Light(led_yellow_pin, "Yellow LED")  # Yellow LED for medium capacity
        self.led_red = Light(led_red_pin, "Red LED")  # Red LED for full capacity
        self.lcd = LCDDisplay(sda=lcd_sda, scl=lcd_scl)



        
        
        # Instantiate a Model. Needs to have the number of states, self as the handler
        # You can also say debug=True to see some of the transitions on the screen
        # Here is a sample for a model with 4 states
        self._model = StateModel(5, self, debug=True)

        
        # Instantiate any Buttons that you want to process events from and add
        # them to the model
        
        self.b1 = Button(button_1_pin, "button1", handler=self)  # Reduce patient count
        self.b2 = Button(button_2_pin, "button2", handler=self)  # Reset patient count
        
        self._model.addButton(self.b1)
        self._model.addButton(self.b2)
        # add other buttons if needed. Note that button names must be distinct
        # for all buttons. Events will come back with [buttonname]_press and
        # [buttonname]_release
        
        # Add any timer you have. Multiple timers may be added but they must all
        # have distinct names. Events come back as [timername}_timeout
        self._timer = SoftwareTimer(name="timer1", handler=None)
        self._model.addTimer(self._timer)

        # Add any custom events as appropriate for your state model. e.g.
        # self._model.addCustomEvent("collision_detected")
        
        self._model.addCustomEvent("motion_detected")
        self._model.addCustomEvent("b2_resets")
        self._model.addCustomEvent("b1_reduces_count")
        self._model.addCustomEvent("green_warning")
        self._model.addCustomEvent("yellow_warning")
        self._model.addCustomEvent("red_warning")
        self._model.addCustomEvent("back_to_idle")        



        ## I NEED TO ADD MORE TRANSITIONS 
        
        # Now add all the transitions from your state model. Any custom events
        # must be defined above first. You can have a state transition to another
        # state based on multiple events - which is why the eventlist is an array
        # Syntax: self._model.addTransition( SOURCESTATE, [eventlist], DESTSTATE)
        
        # From Rest (State 0)
        self._model.addTransition(0, ["motion_detected"], 1)
        self._model.addTransition(0, ["b2_resets"], 1)
        self._model.addTransition(0, ["b1_reduces_count"], 1)

        # From CapacityLevelCalculated (State 1)
        self._model.addTransition(1, ["green_warning"], 2)
        self._model.addTransition(1, ["yellow_warning"], 3)
        self._model.addTransition(1, ["red_warning"], 4)

        # From CapacityLow (State 2)
        self._model.addTransition(2, ["back_to_idle"], 0)

        # From CapacityMedium (State 3)
        self._model.addTransition(3, ["back_to_idle"], 0)

        # From CapacityHigh (State 4)
        self._model.addTransition(4, ["back_to_idle"], 0)
    
    def stateEntered(self, state, event):
        """
        stateEntered - is the handler for performing entry actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        """
        
        # If statements to do whatever entry/actions you need for
        # for states that have entry actions
        Log.d(f'State {state} waiting for motion...')
        if state == 0:
            self.updateIndicators()
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity)+"State:"+str(self._model._curState))

        
        elif state == 1:
            self.room.add_patient()
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity)+"State:"+str(self._model._curState))
            self.calculate_capacity_threshold()
            time.sleep(0.5)
            
        
        elif state == 2:
            self.buzzer.beep(DO, 150)
            time.sleep(0.5)
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity)+"State:"+str(self._model._curState))
            self.calculate_capacity_threshold()
            self._model.processEvent("back_to_idle")
        
        elif state == 3:
            self.buzzer.beep(RE, 150)
            time.sleep(0.5)
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity)+"State:"+str(self._model._curState))
            self.calculate_capacity_threshold()
            self._model.processEvent("back_to_idle")
        
        elif state == 4:
            self.buzzer.beep(MI, 150)
            time.sleep(0.5)
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity)+"State:"+str(self._model._curState))
            self.calculate_capacity_threshold()
            self._model.processEvent("back_to_idle")
            
        
            
    def stateLeft(self, state, event):
        """
        stateLeft - is the handler for performing exit/actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        
        This is just like stateEntered, perform only exit/actions here
        """

        Log.d(f'State {state} exited on event {event}')
        if state == 0:
            # exit actions for state 0
            pass
        # etc.
    
    def stateEvent(self, state, event)->bool:
        """
        stateEvent - handler for performing actions for a specific event
        without leaving the current state. 
        Note that transitions take precedence over state events, so if you
        have a transition as well as an in-state action for the same event,
        the in-state action will never be called.

        This handler must return True if the event was processed, otherwise
        must return False.
        """
        
        # Recommend using the debug statement below ONLY if necessary - may
        # generate a lot of useless debug information.
        # Log.d(f'State {state} received event {event}')
        
        # Handle internal events here - if you need to do something
        if state == 0 and event == 'button1_press':
            self.buzzer.beep(FA, 150)
            self.room.remove_patient()
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity))
            self.calculate_capacity_threshold()
            self.updateIndicators()
            Log.d("Button b1 pressed: Reduced patient count.")
            return True

        if state == 0 and event == 'button2_press':
            self.buzzer.beep(SO, 150)
            self.room.reset_count()
            self.lcd.showText("Patient Count: " + str(self.room.current_capacity))
            self.calculate_capacity_threshold()
            self.updateIndicators()
            Log.d("Button b2 pressed: Reset patient count.")
            return True
        
        # Note the return False if notne of the conditions are met
        return False

    def stateDo(self, state):
        """
        stateDo - the method that handles the do/actions for each state
        """
        
        # Now if you want to do different things for each state that has do actions
        if state == 0:
            if self.sensor.tripped():
                Log.i("Motion detected while in Rest State (0). Triggering event.")
                self._model.processEvent("motion_detected")
        elif state == 1:
            pass
        

    def calculate_capacity_threshold(self):
        if self.room.is_over_capacity() and self._model._curState != 4:
            self._model.processEvent("red_warning")
        elif self.room.is_at_capacity() and self._model._curState != 3:
            self._model.processEvent("yellow_warning")
        elif self.room.is_below_capacity() and self._model._curState != 2:
            self._model.processEvent("green_warning")
    
    def updateIndicators(self):
        # Turn off all LEDs
        for led in (self.led_green, self.led_yellow, self.led_red):
            led.off()

        # Turn on the appropriate LED based on room capacity.
        if self.room.is_below_capacity():
            self.led_green.on()
        elif self.room.is_at_capacity():
            self.led_yellow.on()
        elif self.room.is_over_capacity():
            self.led_red.on()

     

    def run(self):
        """
        Create a run() method - you can call it anything you want really, but
        this is what you will need to call from main.py or someplace to start
        the state model.
        """
        
        # The run method should simply do any initializations (if needed)
        # and then call the model's run method.
        # You can send a delay as a parameter if you want something other
        # than the default 0.1s. e.g.,  self._model.run(0.25)
        self._model.run()

    def stop(self):
        self.led_yellow.off()
        self.led_red.off()
        self.led_green.off()
        self.lcd.reset()
        self._model.stop()
