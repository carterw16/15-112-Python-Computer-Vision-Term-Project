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

        return Node(mid, leftChild, rightChild)

    def toList(self):
        pass

    def insert(self, item):
        self.objects.append(item)
        self.root = KDTree.buildTree(self.objects)


    def delete(self, item):
        self.objects.remove(item)
        self.root = KDTree.buildTree(self.objects)

    def findObjectsWithinDist(self, item, targetDist):
        return KDTree.findObjectsWithinDistHelper(self.root, item.x, item.y, targetDist)
    
    @staticmethod
    def findObjectsWithinDistHelper(node, x, y, targetDist, d=0):
        if node is None:
            return []
        ret = []
        if d % 2 == 0:
            dimension = "x"
            dimValue = x
        else:
            dimension = "y"
            dimValue = y
        
        distToNode = KDTree.distance(node.x, node.y, x, y)
        distToDivider = abs(dimValue - getattr(node, dimension))
        
        if distToNode <= targetDist:
            ret.append(node.item)

        closePointsOnLeft = []
        closePointsOnRight = []
        if dimValue < getattr(node, dimension):
            closePointsOnLeft = KDTree.findObjectsWithinDistHelper(node.leftChild, x, y, targetDist, d+1)
            if distToDivider < targetDist:
                closePointsOnRight = KDTree.findObjectsWithinDistHelper(node.rightChild, x, y, targetDist, d+1)
        else:
            closePointsOnRight = KDTree.findObjectsWithinDistHelper(node.rightChild, x, y, targetDist, d+1)
            if distToDivider < targetDist:
                closePointsOnLeft = KDTree.findObjectsWithinDistHelper(node.leftChild, x, y, targetDist, d+1)

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
    def __init__(self, item, leftChild=None, rightChild=None):
        self.item = item
        self.x = item.x
        self.y = item.y
        self.leftChild = leftChild
        self.rightChild = rightChild
    
    def __repr__(self):
        ret = str(self.item)
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"


def testKDTree():
    dummies = []
    for i in range(10):
        dummies.append(DummyObject(i,i))
    t = KDTree(dummies)
    print(t)
    print("%%%"*10)
    t.delete(dummies[0])
    print(t)

if __name__ == "__main__":
    testKDTree()

    
        

