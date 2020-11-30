from cmu_112_graphics import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import math, time
import random

""" TODO:
    1. make dots get bigger when they eat
    2. fix speed function
    3. moving screen
    4. food
    5. improve AI algorithm (k-d tree)
    7. multiplayer
    8. UI
        a. menu screen with start game btn, calibrate
    9. splitting into smaller dots
"""

class Dot(object):
    allDots = []
    def __init__(self, x, y, r, id, delay):
        self.x = x
        self.y = y
        self.r = r
        self.color = random.choice(["blue", "green","yellow","purple"])
        self.id = id
        self.speedConstant = delay
        Dot.allDots.append(self)

    def __eq__(self, other):
        return isinstance(other, Dot) and self.id == other.id

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
   
    @staticmethod
    def distance(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def move(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self, canvas):
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y + self.r, fill=self.color)

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

def appStarted(app):
    app.rows = 20
    app.cols = 20
    app.mapDims = (app.width, app.height)
    app.maxR = 30
    app.mode = "menu"
    app.countdownStart = None
    app.countdownNumber = 3
    # app.dotX = app.width/2
    # app.dotY = app.height/2
    app.velocity = (0,0)
    app.useCam = True
    app.timerDelay = 30
    app.myDot = MyDot(app.width/2, app.height/2, 40, -1, app.timerDelay, app.useCam)
    # app.mouseX = app.width/2
    # app.mouseY = app.height/2
    app.keyX = app.width/2
    app.keyY = app.height/2
    app.dots = createEnemies(app, 10) + [app.myDot]
    if app.useCam:
        app.cap = cv2.VideoCapture(0)

def createEnemies(app, count):
    enemyDots = []
    for i in range(count):
        enemyDots.append(Dot(random.randrange(0, app.mapDims[0]),random.randrange(0,app.mapDims[1]),random.randrange(1,app.maxR), i, app.timerDelay))
    return enemyDots

def getOverlapping(dots):
    overlapping = []
    for i in range(len(dots)):
        dot = dots[i]
        for j in range(i, len(dots)):
            dot2 = dots[j]
            if dot.distance(dot.x, dot.y, dot2.x, dot2.y) < dot.r + dot2.r: 
                overlapping.append([dot, dot2])
    return overlapping

def getColorMask(img, minHue, maxHue):
    # cv2.cvtColor from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/
    # py_gui/py_video_display/py_video_display.html
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if minHue > maxHue:
        minHSV = np.array([0,180,100])
        maxHSV = np.array([maxHue,255,255])
        mask1 = cv2.inRange(hsv, minHSV, maxHSV)
        minHSV = np.array([minHue,180,100])
        maxHSV = np.array([179,255,255])
        mask2 = cv2.inRange(hsv, minHSV, maxHSV)
        mask = cv2.bitwise_or(mask1,mask2)
    else:
        minHSV = np.array([minHue,180,100])
        maxHSV = np.array([maxHue,255,255])
        mask = cv2.inRange(hsv, minHSV, maxHSV)
    return mask

def getPositionFromVideo(cap):
    # if statement header from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/
    # py_gui/py_video_display/py_video_display.html
    # if cap is None or not cap.isOpened():

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    redMask = getColorMask(frame, 170, 10)
    maxContour, contourImg = getContours(redMask, frame)
    contourImgWithCenter = drawCenterOfCountour(maxContour, contourImg)
    dims = frame.shape
    return getCenterOfContour(maxContour, (dims[0]/2, dims[1]/2)), dims, contourImgWithCenter

# def displayFrame(contour, contourImg):
#     print("hello")
#     contourImgWithCenter = drawCenterOfCountour(contour, contourImg)
#     cv2.imshow('frame', contourImgWithCenter)

def drawCenterOfCountour(contour, contourImg):
    dims = contourImg.shape
    center = getCenterOfContour(contour, (int(dims[0]/2), int(dims[1]/2)))
    if center is None:
        return contourImg
    else:
        contourImg = cv2.circle(contourImg, center, 10, (255,0,0), -1)
        return contourImg

def getCenterOfContour(contour, default):
    if len(contour) != 0:
        M = cv2.moments(contour)
        #moments from https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return (cX, cY)
    return default

def getContours(mask, img=None):
    if img is None:
        dims = (mask.shape[0],mask.shape[1],3)
        contourImg = np.zeros(dims)
    else:
        contourImg = img
    #findContours from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_
    #imgproc/py_contours/py_contours_begin/py_contours_begin.html
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return [], contourImg
    maxc = contours[0]
    for c in contours:
        if len(c) > len(maxc):
            maxc = c
    # takes image, array of contours, contour index (-1 for all), color, thickness
    cv2.drawContours(contourImg, [maxc], -1, (0,255,0), 3)
    return maxc, contourImg

def timerFired(app):
    # print([(d.x,d.y) for d in app.dots])
    if len(app.dots) == 1 or app.myDot not in app.dots:
        app.mode = "gameover"
    if app.mode == "countdown":
        if app.countdownNumber > 0:
            app.countdownNumber = 3 - int(time.time()-app.countdownStart)
        else:
            app.mode = "game"
    if app.mode == "game":
        for dot in app.dots:
            if dot == app.myDot:
                if app.useCam:
                    dot.update((app.width, app.height), app.cap) 
                else:
                    dot.move((app.keyX, app.keyY))
            else:
                dot.update((app.width, app.height))
        if app.useCam == False:
            app.myDot.move(app.keyX, app.keyY)
        overlapping = getOverlapping(app.dots)
        for overlap in overlapping:
            if overlap[0].r < overlap[1].r:
                app.dots.remove(overlap[0])
                Dot.allDots.remove(overlap[0])
            elif overlap[0].r > overlap[1].r:
                app.dots.remove(overlap[1])
                Dot.allDots.remove(overlap[1])

# def mouseMoved(app, event):
#     app.mouseX = event.x
#     app.mouseY = event.y

def keyPressed(app, event):
    if app.useCam == False:
        if event.key == "Up":
            app.keyY -= 20
        elif event.key == "Down":
            app.keyY += 20
        elif event.key == "Left":
            app.keyX -= 20
        elif event.key == "Right":
            app.keyX += 20
        
def getCellBounds(app, row, col):
    gridWidth  = 2*app.width
    gridHeight = 2*app.height
    x0 = gridWidth * col / app.cols
    x1 = gridWidth * (col+1) / app.cols
    y0 = gridHeight * row / app.rows
    y1 = gridHeight * (row+1) / app.rows
    return (x0, y0, x1, y1)

def drawGrid(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, fill='white')

def getVelocity(app):
    center = (app.width/2, app.height/2)
    if center != (app.dotX, app.dotY):
        mag = ((app.dotX-center[0])**2 + (app.dotY-center[1])**2)**0.5
        angle = math.atan((abs(app.dotY - center[1]))/(abs(app.dotX - center[0])))
        # angleY = math.asin((center[0] - app.dotY)/mag)
        velX = mag * math.cos(angle)
        velY = mag * math.sin(angle)
        if app.dotX < center[0]:
            velX = -velX
        if app.dotY < center[1]:
            velY = -velY   
        return velX, velY

def drawDots(app, canvas):
    for dot in app.dots:
        dot.draw(canvas)

def mousePressed(app, event):
    if app.mode == "menu":
        cx, cy = app.width/3, app.height/2
        if ((cx-50 <= event.x <= cx+50) and
            (cy-10 <= event.y <= cy+10)):
            app.useCam = True
            app.mode = "countdown"
            app.countdownStart = time.time()
        cx, cy = 2*app.width/3, app.height/2
        if ((cx-50 <= event.x <= cx+50) and
            (cy-10 <= event.y <= cy+10)):
            app.useCam = False
            app.mode = "countdown"
            app.countdownStart = time.time()
        
def drawMenu(app, canvas): # buttons from https://piazza.com/class/ke208q10xpk75w?cid=3791
    cx, cy = app.width/3, app.height/2
    canvas.create_rectangle(cx-50, cy-10, cx+50, cy+10, fill='cyan')
    canvas.create_text(cx, cy, text='Click me!')
    canvas.create_text(cx, cy+50,
                       text='OpenCV Mode',
                       font='Arial 30 bold')
    cx, cy = 2*app.width/3, app.height/2
    canvas.create_rectangle(cx-50, cy-10, cx+50, cy+10, fill='cyan')
    canvas.create_text(cx, cy, text='Click me!')
    canvas.create_text(cx, cy+50,
                       text='Arrow keys Mode',
                       font='Arial 30 bold')

def drawCountdown(app, canvas):
    cx, cy = app.width/2, app.height/2
    canvas.create_text(cx, cy, text=app.countdownNumber)

def drawGameOver(app, canvas):
    cx, cy = app.width/2, app.height/2
    if app.myDot not in app.dots:
        canvas.create_text(cx, cy+50,
                        text=f'You Lose!',
                        font='Arial 30 bold')
    else:
        canvas.create_text(cx, cy+50,
                        text=f'You Win!',
                        font='Arial 30 bold')

def redrawAll(app, canvas):
    if app.mode == "menu":
        drawMenu(app, canvas)
    elif app.mode == "countdown":
        drawCountdown(app, canvas)
    elif app.mode == "gameover":
        drawGameOver(app, canvas)
    else:
        drawGrid(app, canvas)
    # if app.useCam:
    #     text = "Webcam not available"
    #     canvas.create_text(app.width/2, app.height - 20, text = text)
        drawDots(app, canvas)
        if app.useCam:
            canvas.create_image(app.width, app.height, anchor = SE, image = app.myDot.frame)

    # print(getVelocity(app))

def main():
    runApp(width = 1280, height = 720)
    # "/Users/carterweaver/Desktop/redhat.MOV"

main()
