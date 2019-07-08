from enum import Enum
import threading
import time
import random

latest = {
    "a" : None,
    "b" : None,
    "c" : None,
    "d" : None}


def traffic():
    # create the lock (intersection)
    cross = Intersection()

    # create the roads
    a = Road(3, 'a', cross)
    b = Road(2, 'b', cross)
    c = Road(1, 'c', cross)
    d = Road(1, 'd', cross)

    # start changing the lights
    thread_lights = threading.Thread(target=cross.control_lights, daemon=True)
    thread_lights.start()

    # begin running the threads (roads and their cars)
    thread_a = threading.Thread(target=a.drive_car, daemon=True)
    thread_a.start()

    thread_b = threading.Thread(target=b.drive_car, daemon=True)
    thread_b.start()

    thread_c = threading.Thread(target=c.drive_car, daemon=True)
    thread_c.start()

    thread_d = threading.Thread(target=d.drive_car, daemon=True)
    thread_d.start()

    while not a.empty or not b.empty or not c.empty or not d.empty or cross.driving_cars:
        time.sleep(2)  # continue waiting in two second intervals until the simulation is complete
    
    
    print("Simulation Complete!")


class Car():
    direction = None
    name = None

    def __init__(self, name: str):
        # randomly determine the direction that the car will want to take
        self.direction = Direction(random.randint(1,3))
        self.name = name


# define our lock (called lights)
class Intersection():
    lights = {
        "a" : None,
        "b" : None,
        "c" : None,
        "d" : None}
    # lightsCA = None
    # lightsBD = None
    driving_cars = []

    def __init__(self):
        # initialize the lights to Green and Red
        self.lights["a"] = Colour(1); self.lights["c"] = Colour(1)
        self.lights["b"] = Colour(3); self.lights["d"] = Colour(3)
        # self.lightsCA = Colour(1)
        # self.lightsBD = Colour(3)

    def control_lights(self):
        while(True):
            # wait 10 seconds and switch the lights to yellow
            time.sleep(10)
            self.lights["a"] = Colour(2); self.lights["c"] = Colour(2)
            print("The CA lights are now yellow!")

            # wait 2 seconds and switch the lights to red and the opposite to green
            time.sleep(2)
            self.lights["a"] = Colour(3); self.lights["c"] = Colour(3)
            print("The CA lights are now red!")
            self.lights["b"] = Colour(1); self.lights["d"] = Colour(1)
            print("The BD lights are now green!")

            # wait another 10 seconds and switch the other lights to yellow
            time.sleep(10)
            self.lights["b"] = Colour(2); self.lights["d"] = Colour(2)
            print("The BD lights are now yellow!")

            # wait another 2 seconds and switch the lights to red and the opposite to green
            time.sleep(2)
            self.lights["b"] = Colour(3); self.lights["d"] = Colour(3)
            print("The BD lights are now red!")
            self.lights["a"] = Colour(1); self.lights["c"] = Colour(1)
            print("The CA lights are now green!")

            # after this a full loop in the light colours have occured

    def drive_car_through(self, car: Car):
        # it will take time to drive the car, 
        # add it for a short duration so that other intersections can see it too
        self.driving_cars.append(car)
        print("car " + car.name + " is driving " + car.direction.name + "....\n")
        time.sleep(2)
        self.driving_cars.remove(car)
        print("car " + car.name + " is through!\n")
        del car


class Road():
    cars = []
    letter = None
    intersection = None
    empty = False

    def __init__(self, car_number: int, letter: str, intersection: Intersection):
        self.intersection = intersection
        self.letter = letter
        self.cars = []
        # initialize the road with the needed cars
        for i in range(car_number):
            self.cars.append(Car(letter + "v" + str(i+1)))

    # check if the road's car can enter the traffic based off of its direction
    def drive_car(self):
        while(True):
            car = self.cars[0]
            latest[self.letter] = car.direction
            if car.direction == Direction.LEFT:
                if self.intersection.lights[self.letter] != Colour.RED:
                    # we need to check the oncoming traffic before turning
                    safe = True  # lets initially assume it is safe, but check, and not turn if we detrermine its not safe
                    for inter_car in self.intersection.driving_cars:
                        # if we have a car driving straight from the opposite direction it is not safe
                        if inter_car.direction == Direction.STRAIGHT:
                            # check if it is from the opposite direction
                            if self.letter == "a" and ("cv" in inter_car.name or latest["c"] == Direction.STRAIGHT):
                                safe = False
                            elif self.letter == "c" and ("av" in inter_car.name or latest["a"] == Direction.STRAIGHT):
                                safe = False
                            elif self.letter == "b" and ("dv" in inter_car.name or latest["d"] == Direction.STRAIGHT):
                                safe = False
                            elif self.letter == "d" and ("bv" in inter_car.name or latest["b"] == Direction.STRAIGHT):
                                safe = False

                    if safe:
                        threading.Thread(target=self.intersection.drive_car_through, args=[self.cars.pop(0)], daemon=True).start()
                    else:
                        print("car " + car.name + " cannot turn left yet! waiting 1 second...")
                        time.sleep(1)

            elif car.direction == Direction.STRAIGHT:
                # we can only drive straight if the light is not red
                if self.intersection.lights[self.letter] != Colour.RED:
                    threading.Thread(target=self.intersection.drive_car_through, args=[self.cars.pop(0)], daemon=True).start()

            elif car.direction == Direction.RIGHT:
                # if going right on a green light take the turn
                if self.intersection.lights[self.letter] != Colour.RED:
                    threading.Thread(target=self.intersection.drive_car_through, args=[self.cars.pop(0)], daemon=True).start()

                # if going right on a red check if there is incoming traffic every 3 seconds
                elif self.intersection.lights[self.letter] == Colour.RED:
                    # we need to check the oncoming traffic before turning
                    safe = True  # lets initially assume it is safe, but check, and not turn if we detrermine its not safe
                    for inter_car in self.intersection.driving_cars:
                        # if we have a car driving straight on the left then it is not safe
                        if inter_car.direction == Direction.STRAIGHT:
                            # check if this car is coming from the left
                            if self.letter == "a" and "bv" in inter_car.name:
                                safe = False
                            elif self.letter == "c" and "dv" in inter_car.name:
                                safe = False
                            elif self.letter == "b" and "cv" in inter_car.name:
                                safe = False
                            elif self.letter == "d" and "av" in inter_car.name:
                                safe = False

                    if safe:
                        threading.Thread(target=self.intersection.drive_car_through, args=[self.cars.pop(0)], daemon=True).start()
                    else:
                        print("car " + car.name + " cannot turn right yet... waiting 3 seconds...")
                        time.sleep(3)  # if its not safe wait 3 seconds and check again

            # if the road is empty stop running the thread!
            if not self.cars:
                self.empty = True 
                print("All cars have left road " + self.letter + "\n")
                break


# Define an enum for the possible directions
class Direction(Enum):
    LEFT = 1
    STRAIGHT = 2
    RIGHT = 3

# Define an enum for the possible light colours
class Colour(Enum):
    GREEN = 1
    YELLOW = 2
    RED = 3


if __name__ == "__main__":
    traffic()