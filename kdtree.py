import random, time

class KDTree(object):
    def __init__(self, objects):
        self.objects = objects
        self.root = KDTree.buildTree(self.objects)
    
    def __repr__(self):
        return str(self.root)

    @staticmethod
    def buildTree(objects, d=0):
        if len(objects) == 0:
            return None
        if d % 2 == 0:
            dimension = "x"
        else:
            dimension = "y"
        sortedObjects = sorted(objects, key=lambda obj: getattr(obj, dimension))

        midIndex = len(sortedObjects) // 2
        mid = sortedObjects[midIndex]
        leftChild = KDTree.buildTree(sortedObjects[0:midIndex], d + 1)
        rightChild = KDTree.buildTree(sortedObjects[midIndex + 1:len(sortedObjects)], d + 1)

        largestLeftR = 0
        largestRightR = 0
        if leftChild is not None:
            largestLeftR = leftChild.largestRInSubtree
        if rightChild is not None:
            largestRightR = rightChild.largestRInSubtree
        
        largestRInSubtree = max(largestLeftR, largestRightR, mid.r)
         
        return Node(mid, leftChild, rightChild, largestRInSubtree)

    def toList(self):
        pass

    def insert(self, item):
        self.objects.append(item)
        self.root = KDTree.buildTree(self.objects)


    def delete(self, item):
        self.objects.remove(item)
        self.root = KDTree.buildTree(self.objects)

    def findObjectsWithinDist(self, item, targetDist):
        return KDTree.findObjectsWithinDistHelper(self.root, item.x, item.y, item.r, targetDist)
    
    @staticmethod
    def findObjectsWithinDistHelper(node, x, y, r, targetDist, d=0):
        # print(f'curr: {node}')
        if node is None:
            return []
        ret = []
        if d % 2 == 0:
            dimension = "x"
            dimValue = x
        else:
            dimension = "y"
            dimValue = y
        
        distToNode = KDTree.distance(node.x, node.y, x, y) - (node.r + r)
        distToDivider = abs(dimValue - getattr(node, dimension))
        distToDivider = distToDivider - r

        # print(f"ADDD??? {distToNode} {targetDist}")  
        if distToNode < 0:
            distToNode = 0      
        if distToNode <= targetDist:
            ret.append((node.item, distToNode))
        
        leftSubtreeLargestR = 0
        rightSubtreeLargestR = 0

        #adjustment for radius of dots on opp. side of divider
        if node.leftChild is not None:
            leftSubtreeLargestR = node.leftChild.largestRInSubtree 
        if node.rightChild is not None:
            rightSubtreeLargestR = node.rightChild.largestRInSubtree

        closePointsOnLeft = []
        closePointsOnRight = []
        if dimValue < getattr(node, dimension):
            closePointsOnLeft = KDTree.findObjectsWithinDistHelper(node.leftChild, x, y, r, targetDist, d+1)
            if distToDivider <= targetDist + rightSubtreeLargestR:
                closePointsOnRight = KDTree.findObjectsWithinDistHelper(node.rightChild, x, y, r, targetDist, d+1)
        else:
            closePointsOnRight = KDTree.findObjectsWithinDistHelper(node.rightChild, x, y, r, targetDist, d+1)
            if distToDivider <= targetDist + leftSubtreeLargestR:
                closePointsOnLeft = KDTree.findObjectsWithinDistHelper(node.leftChild, x, y, r, targetDist, d+1)

        # print(ret, closePointsOnLeft, closePointsOnRight)
        return ret + closePointsOnLeft + closePointsOnRight

        # WE ONLY WANT TO DO THIS IF EITHER
        # We are on the left OR
        # DIST TO DIVIDER < dist

        # if distToDivider < dist: # if distance is less we search otherwise prune

            # return findObjectsWithinDistHelper()
    
    @staticmethod
    def distance(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def findNClosestObjects(self, object, n):
        pass

class Node(object):
    def __init__(self, item, leftChild=None, rightChild=None, largestRInSubtree=None):
        self.item = item
        self.x = item.x
        self.y = item.y
        self.r = item.r
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.largestRInSubtree = largestRInSubtree
    
    def __repr__(self):
        ret = f'{self.item}, LR: {self.largestRInSubtree}'
        if self.leftChild:
            ret += f" left: {self.leftChild.item}"
        else:
            ret += " Noleft"
        if self.rightChild:
            ret += f" right: {self.rightChild.item}"
        else:
            ret += " Noright"
        if self.leftChild:
            ret += f"\n {self.leftChild}"
        if self.rightChild:
            ret += f"\n {self.rightChild}"
        return ret

class DummyObject(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
    
    def __repr__(self):
        return f"({self.x}, {self.y}, r={self.r})"

def naiveFindObjectsWithinDist(objects, item, targetDist):
    closest = []
    for obj in objects:
        dist = KDTree.distance(obj.x, obj.y, item.x, item.y) - (obj.r + item.r)
        if dist <= targetDist:
            closest.append(obj)
    return closest

def testKDTree():
    dummies = []
    for i in range(10):
        dummies.append(DummyObject(random.randint(0,20),random.randint(0,20), random.randint(1,4)))
    # print(dummies)
    t = KDTree(dummies)
    # print(t)
    # print("%%%"*10)
    # t.delete(dummies[0])
    # print(t)
    # start = time.time()
    # print(naiveFindObjectsWithinDist(dummies, DummyObject(0,0,1), 5))
    # print(time.time()-start)
    # start = time.time()
    # print(t.findObjectsWithinDist(DummyObject(0,0,1), 5))

    sp = (0, 0, 1)
    searchDist = 5
    naives = naiveFindObjectsWithinDist(dummies, DummyObject(*sp), searchDist)
    news = t.findObjectsWithinDist(DummyObject(*sp), searchDist)
    print(news)
    
    import numpy as np
    # main_list = np.setdiff1d(list_2,list_1
    # print(set(naives))
    # print(set(news))
    # if len(news) != len(naives):
    #     print("DIFF")
    #     print(news)
    #     print(naives)
    #     print(t)
    # else:
    #     print('they seem to match')
    #     print(news)
    #     print(naives)

    # print(time.time()-start)

if __name__ == "__main__":
    testKDTree()

    
        

