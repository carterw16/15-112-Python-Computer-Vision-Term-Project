import cv2
import numpy as np
import time

def findGreaterThan(arr, n):
    greaters = []
    for i in range(len(arr)):
        if arr[i] > n:
            greaters.append(arr[i])
    return np.array(greaters)

def findGreaterThanFast(arr, n):
    return arr[arr > n]

def makeArrays():
    x = np.ones((3,3))
    print(x)
    y = np.array([1,4,7])
    print(y)
    z = np.random.rand(5,10)
    print(z)

def compareNumpyWhatever():
    arr = np.random.rand(1000000)
    print(arr)
    start = time.time()
    print(findGreaterThan(arr, 0.5))
    print(time.time() - start)
    print("*"*50)
    start = time.time()
    print(findGreaterThanFast(arr, 0.5))
    print(time.time() - start)

def dimensions():
    arr = np.random.rand(5,10,3)
    print(arr.shape)
    print(arr.flatten())
    print(len(arr.flatten()))
    print(np.reshape(arr,(3,50)).T)

def basicIndexing():
    arr = np.random.rand(4,5,3)
    print(arr)
    print(arr[0,0,0])
    print(arr[1,1,2])
    print(arr[-1,-1,-1])

def numpyFunctions():
    arr = np.random.rand(4,5,3)
    print(arr)
    print(np.max(arr))
    print(np.mean(arr))
    print(np.argmax(arr))

def slicing():
    arr = np.random.rand(4,5,3)
    print(arr)
    # grab red color channel
    redChannelIndex = 0
    print(arr[:,:,redChannelIndex])
    print(arr[:,:,redChannelIndex].reshape(4,5,1))

def main():
    arr = np.random.rand(4,5,3)
    print(arr)



main()