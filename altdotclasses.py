from videofiltering import *
import random
import numpy as np
from PIL import Image, ImageTk

__CWDEBUG__ = False

    #find list of closest food/smaller object
    #for target in list:
    #   if safe to attack:
            #attack
    #if no targets safe to attack:
    #   escape closest danger
def determineMove(self, closestDots):
    nextDir = self.velocity

    target = self.findSafeTarget(closestDots)

    if target is not None:
        nextDir = self.getVectorFromSelf(target.x, target.y)
    else:
        closestThreat = self.findClosestThreat(closestDots)
        if closestThreat is not None:
            vectorToThreat = self.getVectorFromSelf(closestThreat.x, closestThreat.y)
            nextDir = - vectorToThreat
    return nextDir


def findClosestThreat(self, closestDots):
    for dot in closestDots:
        if dot.r > self.r:
            return dot
    return None

def findSafeTarget(self, closestDots):
    for dot in closestDots:
        if dot.r < self.r:
            if self.checkTargetSafety(dot, closestDots):
                return dot
    return None

def checkTargetSafety(self, target, closestDots):
    for dot in closestDots:
        if dot.r > self.r:
            selfToTargetDist = self.distance(target.x, target.y, self.x, self.y) 
            dotToTargetDist = self.distance(target.x, target.y, dot.x, dot.y) 
            if dotToTargetDist < selfToTargetDist:
                return False
    return True
        
def getVectorFromSelf(self, otherX, otherY):
    vector = np.array([otherX, otherY]) - np.array([self.x, self.y])
    return self.normalizeVector(vector)

def update(self, closestDots, bounds=None):
        # print(closestDots)

        if closestDots is None or len(closestDots) == 0:
            self.mode = "coast"
        elif len(closestDots) > 0:
            closestDots = sorted(closestDots, key=lambda dotDistTups: dotDistTups[1])
            self.setMode(closestDots) 
            if self.mode == "defensive":
                nextDir = self.defensiveVector(closestDots, bounds)
            elif self.mode == "offensive":
                nextDir = self.offensiveVector(closestDots)
        if self.mode == "coast":
            # print("COAST")
            nextDir = self.velocity
            # else:
                # print("NO MODE")


        self.x, self.y = self.takeStep(nextDir, bounds)
        self.velocity = nextDir
    
    def takeStep(self, nextDir, bounds):
        maxX = bounds[0] // 2
        maxY = bounds[1] // 2
        speed = self.getTopSpeed()
        newX = self.x + nextDir[0]*speed
        newY = self.y + nextDir[1]*speed
        if bounds:
            newX = min(maxX-self.r, newX)
            newX = max(-maxX+self.r, newX)
            newY = min(maxY-self.r, newY)
            newY = max(-maxY+self.r, newY) 
        
        return newX, newY

    def offensiveVector(self, closestDots):
        # print("OFFENSIVE")
        # print(closestDots[0][0])
        return self.getVectorFromSelf(closestDots[0][0].x, closestDots[0][0].y)

    def defensiveVector(self, closestDots, bounds):
        # print("DEFENSE")
        allVectors = []
        # averageVector = np.array([0.,0.])
        for dot, dist in closestDots:
            if dot.r > self.r:
                vectorToDot = self.getVectorFromSelf(dot.x, dot.y)
                oppositeVector = -vectorToDot
                dist = self.distance(self.x, self.y, dot.x, dot.y)
                dp = self.dotProduct(vectorToDot, dot.velocity)
                # weight = 50*(dp + 1)/(dot.r * dist)
                # weight = 1
                # print("W", weight)
                # averageVector += oppositeVector * weight
                allVectors.append(oppositeVector)
        # check if close to boundary
        
        distToRightBound = self.distance(self.x, self.y, bounds[0], self.y)
        distToBottomBound = self.distance(self.x, self.y, self.x, bounds[1])
        distToLeftBound = self.distance(self.x, self.y, 0, self.y)
        distToTopBound = self.distance(self.x, self.y, self.x, 0)
        if distToRightBound < self.r * 4: 
            # print('close to right')
        # averageVector += self.boundsVector(bounds[0], self.y)
            allVectors.append(self.boundsVector(bounds[0], self.y))
        if distToBottomBound < self.r * 4:
            # print('close to bottom')
        # averageVector += self.boundsVector(self.x, bounds[1])
            allVectors.append(self.boundsVector(self.x, bounds[1]))

        if distToLeftBound < self.r * 4:
            # print('close to left')
        # averageVector += self.boundsVector(0, self.y)
            allVectors.append(self.boundsVector(0, self.y))

        if distToTopBound < self.r * 4:
        #     print('close to top')
        # averageVector += self.boundsVector(self.x, 0)
            allVectors.append(self.boundsVector(self.x, 0))
        # print(allVectors)
        sumVector = np.array([0., 0.])
        for v in allVectors:
            sumVector += v
        self.allVectors = allVectors
        # print(allVectors)
        # print(sumVector) 
        ret = self.normalizeVector(sumVector)  
        # print("**", ret)
        # print(allVectors) 
        return ret
    
    def boundsVector(self, x, y):
        vectorToDot = self.getVectorFromSelf(x, y)
        oppositeVector = -vectorToDot
        dist = self.distance(self.x, self.y, x, y)
        # weight = self.r / (dist + self.r)
        return oppositeVector

    def setMode(self, closestDots):
        # closest, closestDistance = self.getClosestDot(closestDots)
        closest = closestDots[0][0]
        closestDist = closestDots[0][1]
        closestVector = closest.velocity
        vectorFromClosest = -self.getVectorFromSelf(closest.x, closest.y)
        if closest.r < self.r:
            self.mode = "offensive"
        elif closest.r > self.r:
            # movingToward = self.dotProduct(closestVector, vectorFromClosest) > 0
            # withinDiameter = closestDist < (2*self.r)

            # if movingToward:
            #     self.mode = 'defensive'
            # elif withinDiameter:
            #     self.mode = 'defensive'
            # else:
            #     self.mode ='offensive'
            
            self.mode = "defensive"
        else:
            self.mode = "coast"


    
    @staticmethod
    def normalizeVector(vector):
        norm = np.linalg.norm(vector)
        if norm == 0: print('norm 0', vector, norm)
        return vector / norm





class BasicObject(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.color = "orange" 
        self.name = "food"
    
    def draw(self, canvas):
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y + self.r, fill=self.color)

    def __repr__(self):
        return f"{self.x} {self.y} {self.name}"

class GameObject(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.color = "orange" 
        self.name = "food"
    
    def draw(self, canvas):
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y + self.r, fill=self.color)
        if __CWDEBUG__ 

    @staticmethod
    def distance(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def __repr__(self):
        return f"{self.x} {self.y} {self.name}"

class Dot(object):

    def __init__(self, x, y, r, id, delay):
        go = GameObject(x, y, r)
        go.color = random.choice(["blue", "green","yellow","purple"])
        go.id = id
        self.gos = [go]
        self.delay = delay
        self.growthRate = 10
        self.direction = None

    def __eq__(self, other):
        return isinstance(other, Dot) and self.id == other.id
    
    def __repr__(self):
        return f"{self.id} {self.x} {self.y} {self.color}"

    def split(self):

        startingX = self.gos[0].x
        startingY = self.gos[0].y
        startingR = self.gos[0].r

        newR = startingR/2
        self.gos[0].r = newR
        
        go = GameObject(startingX+startingR, startingY, newR)
        go.color = self.gos[0].color
        go.id = self.gos[0].id
        self.gos.append(go)

    # def update(self, bounds=None, closestDots):
    #     if len(closestDots) > 0:

    def draw(self, canvas):
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y + self.r, fill=self.color)
        canvas.create_text(self.x, self.y, text = self.id)

    def update(self, bounds=None):
        dirVector, mag = self.checkClosestDot()
        speed = self.getTopSpeed() * mag
        self.x += dirVector[0]*speed
        self.y += dirVector[1]*speed
        newX = self.x + dirVector[0]*speed
        newY = self.y + dirVector[1]*speed
        if bounds:
            newX = min(bounds[0], newX)
            newX = max(0, newX)
            newY = min(bounds[1], newY)
            newY = max(0, newY) 
        self.x = newX
        self.y = newY

    # returns velocity in two parts: direction (as normalized vector), magnitude
    def checkClosestDot(self):
        closest, closestDistance = self.getClosestDot()
        closestVector = np.array([closest.x, closest.y]) - np.array([self.x, self.y])
        normalized = closestVector / closestDistance
        if closest.r > self.r:
            normalized = - normalized
        return normalized, 1
    
    # returns top speed depending on radius
    def getTopSpeed(self):
        return 8 * self.delay/self.r

    # returns closest dot to self and distance to dot
    def getClosestDot(self):
        closest = None
        closestDistance = np.inf
        for dot in Dot.allDots:
            nextDistance = self.distance(self.x, self.y, dot.x, dot.y)
            if nextDistance < closestDistance and dot != self:
                closest = dot
                closestDistance = nextDistance
        return closest, closestDistance

    def move(self, x, y):
        self.x = x
        self.y = y
    
    def grow(self, otherR, isFood):
        if isFood:
            self.r += (otherR / self.r) * self.growthRate * 2
        else:
            self.r += (otherR / self.r) * self.growthRate
        
class MyDot(Dot):
    def __init__(self, x, y, r, id, delay, isFromCam):
        super().__init__(x, y, r, id, delay)
        self.isFromCam = isFromCam
        self.color = "red"
        self.frame = None
    
    # returns velocity in two parts: direction (as normalized vector), magnitude
    def getVelocityFromCam(self, camX, camY, shape):
        camDistance = self.distance(shape[1]/2, shape[0]/2, camX, camY)
        dotVector = np.array([camX, camY]) - np.array([shape[1]/2, shape[0]/2])
        normalized = dotVector / camDistance
        return normalized, 1
    
    def update(self, gameBounds, cap):
        camXY, shape, frame = getPositionFromVideo(cap)
        self.saveImage(shape, frame, gameBounds)
        camX, camY = camXY
        dirVector, mag = self.getVelocityFromCam(camX, camY, shape)
        speed = self.getTopSpeed() * mag
        self.x += dirVector[0]*speed
        self.y += dirVector[1]*speed
        newX = self.x + dirVector[0]*speed
        newY = self.y + dirVector[1]*speed
        if gameBounds:
            newX = min(gameBounds[0], newX)
            newX = max(0, newX)
            newY = min(gameBounds[1], newY)
            newY = max(0, newY) 
        self.x = newX
        self.y = newY
    
    def saveImage(self, shape, frame, gameBounds):
        # transparent = np.dstack((frame, np.zeros((shape[0], shape[1]))))
        resized = cv2.resize(frame, (int(gameBounds[0]/6), int(gameBounds[1]/6)))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        converted = Image.fromarray(rgb)
        img = ImageTk.PhotoImage(converted)
        self.frame = img

class SplitDot(object):
    def __init__(self, dotList, r):


