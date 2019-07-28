from mpi4py import MPI
import random

import time
start_time = time.time()

comm = MPI.COMM_WORLD
node = comm.Get_rank()

size = int(comm.Get_size())

numDataPerNode = 8192//size
data = []
# lets ensure node 0 is host:
if node == 0:
    # create the data set to be as large as specified, with an even larger (4)
    # set of numbers that could randomly show up in the list
    data = random.sample(range(numDataPerNode*size*4), numDataPerNode*size)
    print(data)
    half = len(data)//2
    i = size//2
    step = i//2; wait = step + 1

    # send the array split each time.
    # ie if node 0, send to 4, split, send to 2, split, send to 1, split, then keep the rest
    while i > node:
        package = data[half:] + [step]
        comm.send(package, i)
        data = data[:half]
        half = len(data)//2
        i = i//2
        step = step//2

    if step ==0:
        step = step + 1

    data.sort()
    # now we wait and recieve and sort until all has been recieved
    while wait > 0:
        package = None
        package = comm.recv(source=node+step)
        data = data + package
        data.sort()
        step = step*2
        wait = wait - 1

    # print(data)

elif node % 2 == 0:
    # Non-blocking wait
    data = comm.recv(source=MPI.ANY_SOURCE)
    step = data.pop(-1); wait = step
    half = len(data)//2

    target = node + step
    # send the array split each time.
    # ie if node 4, send to 6, split, send to 5, split then keep the rest
    step = step//2
    while target > node:
        package = data[half:] + [step]
        comm.send(package, target)
        data = data[:half]
        half = len(data)//2
        target = node + step
        step = step//2

    # if node == 4: 
    if step ==0:
        step = step + 1
    data.sort()

    # now we wait and recieve and sort until all has been recieved
    while wait > 0:
        package = None
        package = comm.recv(source=node+step)
        data = data + package
        data.sort()
        step = step*2
        comm.send(data, node-step)
        wait = wait - 1

# This would be the leaf
else:
    data = comm.recv(source=MPI.ANY_SOURCE)
    step = data.pop(-1)
    if step ==0:
        step = step + 1

    data.sort()

    comm.send(data, node-step)

if node == 0:
    print("Node: ", node, "-----------------------\n", data, "\n") 
    print("--- %s seconds ---" % (time.time() - start_time))
else:
    print("Node : ", node, " is done!")

# 0.03842902183532715s for 4096 elements at 8 nodes
# 0.05340075492858887s for 8192 elements at 8 nodes

# 0.016469717025756836s for 4096 elements at 4 nodes
# 0.024457216262817383s for 8192 elements at 8 nodes

# This clearly shows that while increasing the number of nodes may theoretically decrease run time,
# If the number of elements being acted on is too low, the cost of setting up and working with MPI
# may be more than using less nodes and doing the calculations in bulk

# In this case, sorting 4096 and 8192 elements using 4 nodes saves time, compared to the sort
# when waiting on and setting up 4 additional nodes to do the same work