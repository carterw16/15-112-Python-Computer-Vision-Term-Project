from videofiltering import *
import random, time
import numpy as np
from PIL import Image, ImageTk


class GameObject(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.color = "orange" 
        self.name = "food"
        self.velocity = [0,0]
    
    def draw(self, canvas, gameCenter):
        x = gameCenter[0] + self.x
        y = gameCenter[1] + self.y
        canvas.create_oval(x-self.r, y-self.r, x+self.r, y + self.r, fill=self.color)
    
    @staticmethod
    def distance(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def distanceBetweenCenters(self, dot):
        return ((self.x-dot.x)**2+(self.y-dot.y)**2)**0.5
    
    def distanceBetweenEdges(self, dot):
        return ((self.x-dot.x)**2+(self.y-dot.y)**2)**0.5 - (self.r + dot.r)

    @staticmethod
    def dotProduct(vector1, vector2):
        return np.dot(vector1, vector2)

    def __repr__(self):
        return f"{self.x} {self.y} {self.name}"
    
    def isOverlapping(self, other):
        if self.distance(self.x, self.y, other.x, other.y) < self.r + other.r: 
            return True
        return False

class SubDot(GameObject):
    def __init__(self, parentX, parentY, r, color, xOffset, yOffset, parent):
        super().__init__(parentX + xOffset, parentY + yOffset, r)
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.color = color
        self.parent = parent

    # def draw(self, canvas, dotCenter):
    #     x = dotCenter[0] + self.xOffset
    #     y = dotCenter[1] + self.yOffset
    #     canvas.create_oval(x-self.r, y-self.r, x+self.r, y + self.r, fill=self.color)
    
    def update(self, parentX, parentY):
        self.x = parentX + self.xOffset
        self.y = parentY + self.yOffset
    
    def updateOffsets(self, growthRate):
        self.xOffset *= growthRate
        self.yOffset *= growthRate
    
    def __eq__(self, other):
        return (self.xOffset == other.xOffset and self.yOffset == other.yOffset 
        and self.parent == other.parent)
    
    

class Dot(GameObject):
    # allDots = []
    def __init__(self, x, y, r, id, delay):
        super().__init__(x, y, r)
        self.color = random.choice(["blue", "green","yellow","purple"])
        self.id = id
        self.delay = delay
        self.growthRate = 10
        self.mode = None
        self.isSplit = False
        self.subDotList = [SubDot(self.x, self.y, self.r, self.color, 0, 0, self)]
        self.splitTime = None
        
        self.velocity = [0,0]
        # if self.isSplit:
        #     newR = self.r // 2
        #     self.dotList = [Dot(self.x-newR, self.y-newR, newR, -1, self.delay, False),
        #     Dot(self.x+newR, self.y+newR, newR, -1, self.delay, False)]
        # else:
        #     self.dotList = [self]

        # Dot.allDots.append(self)

    def __eq__(self, other):
        return isinstance(other, Dot) and self.id == other.id
    
    def __repr__(self):
        return f"{self.id} {self.x} {self.y} {self.color} {type(self)}"
    
    # sort closestDots by dist. 
    # default to coasting
    # look for closest target
    # if target safe go at it
    # else go away from closest threat
    def determineMove(self, closestDots):
        closestDots = sorted(closestDots, key=lambda dotDistTups: dotDistTups[1])
        nextDir = self.coast()
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
        for dot, dist in closestDots:
            if dot.r > self.r:
                return dot
        return None

    # returns closest safe target or none if no safe targets
    def findSafeTarget(self, closestDots):
        for dot, dist in closestDots:
            if dot.r < self.r:
                if self.checkTargetSafety(dot, closestDots):
                    return dot
        return None

    # returns true if target is safe, else false
    def checkTargetSafety(self, target, closestDots):
        for dot, dist in closestDots:
            if dot.r > self.r:
                selfToTargetDist = self.distanceBetweenEdges(target)
                dotToTargetDist = target.distanceBetweenEdges(dot)
                if dotToTargetDist < selfToTargetDist:
                    return False
        return True

    def split(self):
        if self.isSplit is False:
            self.splitTime = time.time()
            self.isSplit = True
            newR = self.r // 2
            self.subDotList = [SubDot(self.x, self.y, newR, self.color, newR, 0, self),
                                SubDot(self.x, self.y, newR, self.color, -newR, 0, self)]

    def coast(self):
        return self.velocity

    def update(self, closestDots, bounds=None):
        # print(closestDots)
        if closestDots is None or len(closestDots) == 0:
            # self.mode = "coast"
            nextDir = self.coast()
        # elif len(closestDots) > 0:
        #     if self.id == -1:
        #         print(self.color, closestDots)
        #     closestDots = sorted(closestDots, key=lambda dotDistTups: dotDistTups[1])
        #     self.setMode(closestDots) 
        #     if self.mode == "defensive":
        #         nextDir = self.defensiveVector(closestDots, bounds)
        #     elif self.mode == "offensive":
        #         nextDir = self.offensiveVector(closestDots)
        # if self.mode == "coast":
        #     # print("COAST")
        #     nextDir = self.velocity
        #     # else:
        #         # print("NO MODE")
        else:
            nextDir = self.determineMove(closestDots)
        
        # print(self.id, self.x, self.y)
        if self.isSplit and time.time() - self.splitTime > 5:
            self.recombineSubDots()

        self.x, self.y = self.takeStep(nextDir, bounds)
        for subDot in self.subDotList:
            subDot.update(self.x, self.y)
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

    def getVectorFromSelf(self, otherX, otherY):
        vector = np.array([otherX, otherY]) - np.array([self.x, self.y])
        return self.normalizeVector(vector)
    
    @staticmethod
    def normalizeVector(vector):
        norm = np.linalg.norm(vector)
        if norm == 0: print('norm 0', vector, norm)
        return vector / norm

    # def getClosestDot(self, closestDots):
    #     closest = None
    #     closestDistance = np.inf
    #     for dot in closestDots:
    #         nextDistance = self.distance(self.x, self.y, dot.x, dot.y)
    #         if nextDistance < closestDistance and dot != self:
    #             closest = dot
    #             closestDistance = nextDistance
    #     return closest, closestDistance

    def drawVector(self, canvas, x, y, l=100, gameCenter=(0,0)):
        x = gameCenter[0] + self.x
        y = gameCenter[1] + self.y
        v = self.normalizeVector([x, y])
        canvas.create_line(x, y, x+(l*v[0]), y+(l*v[1]))

    def draw(self, canvas, gameCenter):
        x = gameCenter[0] + self.x
        y = gameCenter[1] + self.y
        # if self.id == -1:
            # print(self.dotList)
        for sd in self.subDotList:
            # if self.id == -1:
            #     print(dot)
            sd.draw(canvas, gameCenter)
        # self.drawVector(canvas, self.velocity[0], self.velocity[1], 100, gameCenter)
        # try:
        #     for v in self.allVectors:
        #         self.drawVector(canvas, v[0], v[1], l=50, gameCenter=gameCenter)
        # except: pass

    
    # returns top speed depending on radius
    def getTopSpeed(self):
        r = self.r
        boost = 1
        if self.isSplit:
            r = self.subDotList[0].r
            if time.time() - self.splitTime < 1:
                boost = 2
        minR = 20
        topSpeed = 400/r * boost
        if topSpeed > 2 * minR:
            # print("clipping")
            topSpeed = 2 * minR
        # ('****', self.id, topSpeed)
        return topSpeed
    
    # def getClosestDot(self):
    #     closest = None
    #     closestDistance = np.inf
    #     for dot in Dot.allDots:
    #         nextDistance = self.distance(self.x, self.y, dot.x, dot.y)
    #         if nextDistance < closestDistance and dot != self:
    #             closest = dot
    #             closestDistance = nextDistance
    #     return closest, closestDistance

    def move(self, x, y):
        self.x = x
        self.y = y
    
    def grow(self, otherR, isFood):
        originalR = self.r
        if isFood:
            growth = (otherR / self.r) * self.growthRate * 2
        else:
            growth = (otherR / self.r) * self.growthRate

        self.r += growth
        growthRate = self.r / originalR
        for subDot in self.subDotList:
            subDot.r = self.r / len(self.subDotList)
            subDot.updateOffsets(growthRate)
    
    def removeSubDot(self, subDot):
        self.subDotList.remove(subDot)
        if len(self.subDotList) > 0:
            self.r -= subDot.r
            self.x = np.mean([sd.x for sd in self.subDotList])
            self.y = np.mean([sd.y for sd in self.subDotList])
            if len(self.subDotList) == 1:
                self.isSplit = False
    
    def recombineSubDots(self):
        self.subDotList = [SubDot(self.x, self.y, self.r, self.color, 0, 0, self)]
        self.isSplit = False

        
class MyDot(Dot):
    def __init__(self, x, y, r, id, delay, isFromCam):
        super().__init__(x, y, r, id, delay)
        self.isFromCam = isFromCam
        self.color = "red"
        self.frame = None
        self.subDotList = [SubDot(self.x, self.y, self.r, self.color, 0, 0, self)]
        # if self.isSplit:
        #     newR = self.r // 2
        #     self.dotList = [MyDot(self.x-newR, self.y-newR, newR, -1, self.delay, True, False),
        #     MyDot(self.x+newR, self.y+newR, newR, -1, self.delay, True, False)]
        # else:
        #     self.dotList = [self]

    def update(self, gameBounds, cap, hueRange, satRange=(180,255), valRange=(100,255)):
        camX, camY, shape = self.getFrame(cap, 1/6, hueRange, satRange, valRange)
        dirVector, mag = self.getVelocityFromCam(camX, camY, shape)

        if self.isSplit and time.time() - self.splitTime > 10:
            self.recombineSubDots()

        self.x, self.y = self.takeStep(dirVector, gameBounds)

        for subDot in self.subDotList:
            subDot.update(self.x, self.y)
        self.velocity = dirVector
    
    def getFrame(self, cap, sizeFactor, hueRange, satRange=(180,255), valRange=(100,255)):
        camXY, shape, frame = getPositionFromVideo(cap, hueRange, satRange, valRange)
        self.saveImage(shape, frame, (shape[1], shape[0]), sizeFactor)
        camX, camY = camXY
        return camX, camY, shape

    # returns velocity in two parts: direction (as normalized vector), magnitude
    def getVelocityFromCam(self, camX, camY, shape):
        camDistance = self.distance(shape[1]/2, shape[0]/2, camX, camY)
        dotVector = np.array([camX, camY]) - np.array([shape[1]/2, shape[0]/2])
        normalized = dotVector / camDistance
        return normalized, 1
    
    def saveImage(self, shape, frame, gameBounds, sizeFactor):
        # transparent = np.dstack((frame, np.zeros((shape[0], shape[1]))))
        resized = cv2.resize(frame, (int(gameBounds[0] * sizeFactor), int(gameBounds[1] * sizeFactor)))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        converted = Image.fromarray(rgb)
        img = ImageTk.PhotoImage(converted)
        self.frame = img


# class SplitDot(object):
#     def __init__(self, dotList, x, y):
#         self.dotList = dotList
#         self.x = x
#         self.y = y
    
#     def draw(self, canvas, gameCenter):
#         for dot in self.dotList:
#             x = gameCenter[0] + dot.x
#             y = gameCenter[1] + dot.y
#             canvas.create_oval(x-dot.r, y-dot.r, x+dot.r, y + dot.r, fill=dot.color)
#             canvas.create_text(x, y, text = dot.id)


