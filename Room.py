from Log import *

class Room:
    """
    Room class to represent an emergency room.
    Stores room number, capacity threshold, and current capacity.
    """

    def __init__(self, room_number, capacity_threshold):
        self.room_number = room_number
        self.capacity_threshold = capacity_threshold
        self.current_capacity = 0  # Start with 0 patients

    def add_patient(self):
        self.current_capacity += 1
        Log.i(f"Patient added. Current capacity: {self.current_capacity}")

    def remove_patient(self):
        if self.current_capacity > 0:
            self.current_capacity -= 1
            Log.i(f"Patient removed. Current capacity: {self.current_capacity}")
        else:
            Log.w("No patients to remove.")

    def reset_count(self):
        self.current_capacity = 0
        Log.i("Patient count reset to 0.")

    def is_over_capacity(self):
        return self.current_capacity > self.capacity_threshold

    def is_at_capacity(self):
        return self.current_capacity == self.capacity_threshold

    def is_below_capacity(self):
        return self.current_capacity < self.capacity_threshold
