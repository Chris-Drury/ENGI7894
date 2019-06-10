from queue import Queue
import threading
import time
import random

served_customers = []
forced_to_leave_customers = []
# for clock simulation, instead of using a library we will just use some math to determine ratios in the main
t = 0

def monitor():
    def generate_customer():
        def retry_joining(customer_id):
            customer = Customer(customer_id)
            print("customer " + str(customer.order_number) + " is waitinig 20s to join a queue")
            time.sleep(20*t)
            if not line1.full() or not line2.full():
                if line2.qsize() > line1.qsize():
                    line1.put(customer)
                else:
                    line2.put(customer)
            print("the queue is still full, customer "+ str(customer.order_number) + " will come back in 600s")
            time.sleep(600*t)
            if not line1.full() or not line2.full():
                if line2.qsize() > line1.qsize():
                    line1.put(customer)
                else:
                    line2.put(customer)
            print("customer " + str(customer.order_number) + " is waitinig 40s to join a queue")
            time.sleep(40*t)
            if not line1.full() or not line2.full():
                if line2.qsize() > line1.qsize():
                    line1.put(customer)
                else:
                    line2.put(customer)
            print("customer " + str(customer.order_number) + " could not find a spot, forced to leave...")
            forced_to_leave_customers.append(customer)

        x = 0

        while(True):
            next_customer_time = random.uniform(t*50, t*101)
            if not line1.full() or not line2.full():
                if line2.qsize() > line1.qsize():
                    line1.put(Customer(x))
                else:
                    line2.put(Customer(x))
                print("customer: " + str(x) + " queued, seconds until next customer: " + str(next_customer_time/t))
            else:
                threading.Thread(target=retry_joining, daemon=True, args=[x]).start()

            x = x + 1
            time.sleep(next_customer_time)

    def dispatch():
        # initialize to start the logic properly in dispatch
        l1 = Customer(1)
        l2 = Customer(0)

        while(True):
            if (not line2.empty() or not line1.empty()) and not window.customer:
                if not line2.empty():
                    l2 = line2.queue[0]

                if not line1.empty():
                    l1 = line1.queue[0]

                if l2.order_number < l1.order_number:
                    window.customer = line2.get()
                else:
                    window.customer = line1.get()


    window = DriveThroughWindow(False, "Rick", False)

    line1 = Queue(maxsize=3)
    line2 = Queue(maxsize=3)

    crew_rick = CrewMember('Rick', window)
    crew_amy = CrewMember('Amy', window)

    # need to prep the crew:
    rick = threading.Thread(target=crew_rick.transaction, daemon=True)
    rick.start()
    amy = threading.Thread(target=crew_amy.transaction, daemon=True)
    amy.start()

    customer_generator = threading.Thread(target=generate_customer, daemon=True)
    customer_generator.start()

    # start the queue dispatch:
    queue_dispatcher = threading.Thread(target=dispatch, daemon=True)
    queue_dispatcher.start()


class DriveThrough:
    x_time = 0

    def __init__(self, x_time: int):
        self.x_time = x_time

    def start(self):
        drivethrough = threading.Thread(target=monitor, daemon=True)    
        drivethrough.start()
        time.sleep(self.x_time)  # 14400 => 4hrs
        drivethrough.join()


class DriveThroughWindow:
    def __init__(self, occupied: bool, last_attendant: str, customer):
        self.occupied = occupied
        self.last_attendant = last_attendant
        self.customer = customer


class CrewMember:
    def __init__(self, name: str, window: DriveThroughWindow):
        self.name = name
        self.window = window

    def transaction(self):
        while(True):
            if not self.window.occupied and self.window.last_attendant != self.name and self.window.customer:

                self.window.occupied = True

                service_time = random.uniform(t*300, t*601)
                print(self.name + " is taking " + str(service_time/t) + " seconds to process the transaction with customer: " + str(self.window.customer.order_number))
                time.sleep(service_time)
                self.window.customer.transaction(self, service_time)

                # spin the lock in fairness for the other crew member
                self.window.last_attendant = self.name
                
                # clear the customer as they have finished their transaction
                served_customers.append(self.window.customer)
                self.window.customer = None

                # unlock the window(lock)
                self.window.occupied = False


class Customer:
    def __init__(self, number: int):
        self.order_number = number
        self.duration = 0

    def transaction(self, crewmember, service_time):
        print("transaction with customer " + str(self.order_number) + " and crewmember " + crewmember.name + "\n")
        self.duration = service_time


if __name__ == "__main__":
    x = int(input("how long to run? (in seconds) \n"))    
    print("simulating 4hrs (14400s) over " + str(x) + " seconds")

    t = x/14400

    drive_through = DriveThrough(x)
    drive_through.start()

    print("Total number of customers that arrived: " + str(len(served_customers) + len(forced_to_leave_customers)))
    print("Total number of customers forced to leave: " + str(len(forced_to_leave_customers)))
    print("Total number of customers that were served: " + str(len(served_customers)))

    total_served_time = 0
    for customer in served_customers:
        total_served_time += customer.duration/t 
    print("\nAverage time taken to serve each customer: " + str(total_served_time/len(served_customers)))
