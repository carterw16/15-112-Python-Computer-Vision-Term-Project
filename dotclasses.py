from videofiltering import *
import random
import numpy as np
from PIL import Image, ImageTk

class GameObject(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.color = "orange" 
    
    def draw(self, canvas):
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y + self.r, fill=self.color)
    
    @staticmethod
    def distance(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

class Dot(GameObject):
    allDots = []
    def __init__(self, x, y, r, id, delay):
        super().__init__(x, y, r)
        self.color = random.choice(["blue", "green","yellow","purple"])
        self.id = id
        self.speedConstant = delay
        self.growthRate = 10
        Dot.allDots.append(self)

    def __eq__(self, other):
        return isinstance(other, Dot) and self.id == other.id
    
    def __repr__(self):
        return f"{self.id} {self.x} {self.y} {self.color}"

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
        return 10

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