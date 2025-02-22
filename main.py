
from EmergencyRoomController import *


# Test your model. Note that this only runs the template class above
# If you are using a separate main.py or other control script,
# you will run your model from there.
if __name__ == '__main__':
    p = EmergencyRoomController(
        room_number=6106, 
        capacity_threshold=3, 
        sensor_pin=28, 
        buzzer=17, 
        led_green_pin=5, 
        led_yellow_pin=9, 
        led_red_pin=13, 
        lcd_sda=0, 
        lcd_scl=1,
        button_1_pin=15,
        button_2_pin=2
    )
    try:
        p.run()
    except KeyboardInterrupt:
        p.stop()
  