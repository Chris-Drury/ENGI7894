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
            if not queue_lock.locked:
                queue_lock.lock()
                if not line1.full() or not line2.full() or not line3.full():
                    if not line3.full():
                        line3.put(Customer(x))
                    elif not line2.full():
                        line2.put(Customer(x))
                    else: 
                        line1.put(Customer(x))
                queue_lock.unlock()
            print("the queue is still full, customer "+ str(customer.order_number) + " will come back in 600s")
            time.sleep(600*t)
            if not queue_lock.locked:
                queue_lock.lock()
                if not line1.full() or not line2.full() or not line3.full():
                    if not line3.full():
                        line3.put(Customer(x))
                    elif not line2.full():
                        line2.put(Customer(x))
                    else: 
                        line1.put(Customer(x))
                queue_lock.unlock()
            print("customer " + str(customer.order_number) + " is waitinig 40s to join a queue")
            time.sleep(40*t)
            if not queue_lock.locked:
                queue_lock.lock()
                if not line1.full() or not line2.full() or not line3.full():
                    if not line3.full():
                        line3.put(Customer(x))
                    elif not line2.full():
                        line2.put(Customer(x))
                    else: 
                        line1.put(Customer(x))
                queue_lock.unlock()
            print("customer " + str(customer.order_number) + " could not find a spot, forced to leave...")
            forced_to_leave_customers.append(customer)
        
        x = 0

        while(True):
            next_customer_time = random.uniform(t*50, t*100)
            if not queue_lock.locked:
                queue_lock.lock()
                if not line1.full() or not line2.full() or not line3.full():
                    if not line3.full():
                        line3.put(Customer(x))
                    elif not line2.full():
                        line2.put(Customer(x))
                    else: 
                        line1.put(Customer(x))
                    queue_lock.unlock()
                    print("customer " + str(x) + " was queued, time until next customer: " + str(next_customer_time/t) + "\n")
                else:
                    queue_lock.unlock()
                    threading.Thread(target=retry_joining, daemon=True, args=[x]).start()

            x = x + 1
            time.sleep(next_customer_time)


    queue_lock = QueueLock()

    line1 = Queue(maxsize=2)
    line2 = Queue(maxsize=2)
    line3 = Queue(maxsize=2)

    staff_john = Cashier("John", line1)
    staff_mabel = Cashier("Mabel", line2)
    staff_timmy = Cashier("Timmy", line3)

    john = threading.Thread(target=staff_john.checkout, daemon=True)
    john.start()
    mabel = threading.Thread(target=staff_mabel.checkout, daemon=True)
    mabel.start()
    timmy = threading.Thread(target=staff_timmy.checkout, daemon=True)
    timmy.start()

    customer_generator = threading.Thread(target=generate_customer, daemon=True)
    customer_generator.start()

class QueueLock:
    locked: bool

    def __init__(self):
        self.locked = False
    
    def lock(self):
        locked = True

    def unlock(self):
        locked = False

class GroceryQueue:
    x_time = 0

    def __init__(self, x_time: int):
        self.x_time = x_time

    def start(self):
        grocerystore = threading.Thread(target=monitor, daemon=True)    
        grocerystore.start()
        time.sleep(self.x_time)  # 14400 => 4hrs
        grocerystore.join()


class Cashier:
    def __init__(self, name, queue):
        self.name = name
        self.queue = queue


    def checkout(self):
        while(True):
            if not self.queue.empty():
                customer = self.queue.queue[0] # the customer is still in the line while in check-out 

                service_time = random.uniform(t*300, t*601)
                print(self.name + " is now taking " + str(service_time/t) + " seconds to serve customer " + str(customer.order_number) + "\n")
                time.sleep(service_time)

                customer.get_served(service_time, self)
                served_customers.append(self.queue.get()) # the customer has now been served


class Customer():
    def __init__(self, customer_id: int):
        self.order_number = customer_id
        self.duration = 0

    def get_served(self, service_time, staff_member):
        print("Customer " + str(self.order_number) + " was served by " + staff_member.name)
        self.duration = service_time


if __name__ == "__main__":
    x = int(input("how long to run? (in seconds) \n"))    
    print("simulating 4hrs (14400s) over " + str(x) + " seconds")

    t = x/14400

    grocery_queue = GroceryQueue(x)
    grocery_queue.start()

    print("Total number of customers that arrived: " + str(len(served_customers) + len(forced_to_leave_customers)))
    print("Total number of customers forced to leave: " + str(len(forced_to_leave_customers)))
    print("Total number of customers that were served: " + str(len(served_customers)))

    total_served_time = 0
    for customer in served_customers:
        total_served_time += customer.duration/t 
    print("\nAverage time taken to serve each customer: " + str(total_served_time/len(served_customers)))