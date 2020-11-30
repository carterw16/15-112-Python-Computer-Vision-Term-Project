from cmu_112_graphics import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import math, time, random
from dotclasses import *
from videofiltering import *

""" TODO:
    1. fix grow function
    2. fix speed function
    3. moving screen
    5. improve AI algorithm (k-d tree)
    7. multiplayer
    8. UI
        a. calibration
    9. splitting into smaller dots
"""

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
    app.foodList = [GameObject(random.randrange(0, app.mapDims[0]),random.randrange(0,app.mapDims[1]),5) for i in range(10)]
    app.dots = createEnemies(app, 10) + [app.myDot]
    if app.useCam:
        app.cap = cv2.VideoCapture(0)

def createEnemies(app, count):
    enemyDots = []
    for i in range(count):
        enemyDots.append(Dot(random.randrange(0, app.mapDims[0]),random.randrange(0,app.mapDims[1]),random.randrange(6,app.maxR), i, app.timerDelay))
    return enemyDots

def getOverlapping(dots):
    overlapping = []
    for i in range(len(dots)):
        dot = dots[i]
        for j in range(i+1, len(dots)):
            dot2 = dots[j]
            if dot.distance(dot.x, dot.y, dot2.x, dot2.y) < dot.r + dot2.r: 
                overlapping.append([dot, dot2])
    return overlapping

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
                    dot.move(app.keyX, app.keyY)
            else:
                dot.update((app.width, app.height))
        overlapping = getOverlapping(app.dots + app.foodList)
        for overlap in overlapping:
            overlap = sorted(overlap, key = lambda x: x.r)
            try:
                if type(overlap[0]) == GameObject and overlap[0] in app.foodList:
                    overlap[1].grow(overlap[0].r, True)
                    app.foodList.remove(overlap[0])
                elif overlap[0].r < overlap[1].r and overlap[0] in app.dots:
                    overlap[1].grow(overlap[0].r, False)
                    app.dots.remove(overlap[0])
                    Dot.allDots.remove(overlap[0])
            except:
                print(overlapping)
                raise

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

# def getVelocity(app):
#     center = (app.width/2, app.height/2)
#     if center != (app.dotX, app.dotY):
#         mag = ((app.dotX-center[0])**2 + (app.dotY-center[1])**2)**0.5
#         angle = math.atan((abs(app.dotY - center[1]))/(abs(app.dotX - center[0])))
#         # angleY = math.asin((center[0] - app.dotY)/mag)
#         velX = mag * math.cos(angle)
#         velY = mag * math.sin(angle)
#         if app.dotX < center[0]:
#             velX = -velX
#         if app.dotY < center[1]:
#             velY = -velY   
#         return velX, velY

def drawDots(app, canvas):
    for dot in app.dots:
        dot.draw(canvas)
    for food in app.foodList:
        food.draw(canvas)

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
