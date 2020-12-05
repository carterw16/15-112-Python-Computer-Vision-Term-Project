from cmu_112_graphics import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import math, time, random
from dotclasses import *
from videofiltering import *
from kdtree import *

""" 
git status
git add ___
git commit -m "___"
git push origin main

TODO:
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
    app.gridWidth = 2*app.width
    app.gridHeight = 2*app.height
    app.cellWidth = app.gridWidth / app.cols
    app.cellHeight = app.gridHeight / app.rows
    # app.mapDims = (app.width, app.height)
    app.maxR = 50
    app.minR = 20
    app.gameCenter = (app.width/2, app.height/2)
    # app.mode = "menu"
    app.mode = "game"
    app.countdownStart = None
    app.countdownNumber = 3
    # app.dotX = app.width/2
    # app.dotY = app.height/2
    app.velocity = (0,0)
    app.useCam = True
    app.timerDelay = 5
    # app.myDot = MyDot(app.width/2, app.height/2, 30, -1, app.timerDelay, app.useCam)
    app.myDot = MyDot(0, 0, 30, -1, app.timerDelay, app.useCam)
    # app.mouseX = app.width/2
    # app.mouseY = app.height/2
    app.keyX = app.width/2
    app.keyY = app.height/2
    app.foodList = [GameObject(random.randrange(-app.gridWidth/2, 
    app.gridWidth/2),random.randrange(-app.gridHeight/2,app.gridHeight/2),5) for i in range(70)]
    app.enemyDots = createEnemies(app, 15)
    app.dots = app.enemyDots + [app.myDot]
    app.gameObjectTree = KDTree(app.dots + app.foodList)
    app.targetDist = 300
    if app.useCam:
        app.cap = cv2.VideoCapture(0)

def createEnemies(app, count):
    enemyDots = []
    for i in range(count):
        enemyDots.append(Dot(random.randrange(-app.gridWidth/2, app.gridWidth/2), 
        random.randrange(-app.gridHeight/2,app.gridHeight/2),
        random.randrange(app.minR,app.maxR), i, app.timerDelay))
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
    # # print([(d.x,d.y) for d in app.dots])
    # print("gamecenter", app.gameCenter)
    # print("myDot", app.myDot.x, app.myDot.y)
    if len(app.dots) == 1 or app.myDot not in app.dots:
        app.mode = "gameover"
    if app.mode == "countdown":
        if app.countdownNumber > 0:
            app.countdownNumber = 3 - int(time.time()-app.countdownStart)
        else:
            app.mode = "game"
    if app.mode == "game":
        start = time.time()
        app.gameObjectTree = KDTree(app.dots + app.foodList)
        print("updatetree=", time.time()-start)
        for i, dot in enumerate(app.dots):
            if dot == app.myDot:
                if app.useCam:
                    # closestDots = app.gameObjectTree.findObjectsWithinDist(dot, app.targetDist)
                    # print(closestDots)
                    # print(app.gameObjectTree)
                    dot.update((app.gridWidth, app.gridHeight), app.cap) 
                    app.gameCenter = (app.width/2 - dot.x, app.height/2 - dot.y)
                else:
                    dot.move(app.keyX, app.keyY)
            else:
                closestDots = app.gameObjectTree.findObjectsWithinDist(dot, app.targetDist)
                closestDots.remove((dot, 0))
                # if i == 0:
                    # print(closestDots)
                # allCloseDots.append(closestDots)
                dot.update(closestDots, (app.gridWidth, app.gridHeight))
        overlapping = getOverlapping(app.dots + app.foodList)
        for overlap in overlapping:
            overlap = sorted(overlap, key = lambda x: x.r)
            try:
                if isinstance(overlap[1], Dot) and overlap[0] in app.foodList:
                    overlap[1].grow(overlap[0].r, True)
                    app.foodList.remove(overlap[0])
                    # app.gameObjectTree.delete(overlap[0])
                    newFood = GameObject(random.randrange(-app.gridWidth/2, app.gridWidth/2),random.randrange(-app.gridHeight/2,app.gridHeight/2),5)
                    # app.gameObjectTree.insert(newFood)
                    app.foodList.append(newFood)
                elif overlap[0].r < overlap[1].r and overlap[0] in app.dots:
                    overlap[1].grow(overlap[0].r, False)
                    app.dots.remove(overlap[0])
                    # Dot.allDots.remove(overlap[0])
                    # app.gameObjectTree.delete(overlap[0])
                    newDot = Dot(random.randrange(-app.gridWidth/2, app.gridWidth/2), 
                             random.randrange(-app.gridHeight/2,app.gridHeight/2),
                             random.randrange(app.minR,app.maxR), i, app.timerDelay)
                    # app.gameObjectTree.insert(newDot)
                    app.dots.append(newDot)
            except:
                print(overlapping)
                raise

# def updateDot(app, dot):
#     closestDots = app.gameObjectTree.findObjectsWithinDist(dot, app.targetDist)
#     if len(closestDots) > 0:


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

# def splitDot(app, dot):
#     newR = dot.r // 2
#     dot = SplitDot([])
        
def getCellBounds(app, row, col, xOffset, yOffset):
    gridWidth = app.gridWidth
    gridHeight = app.gridHeight
    x0 = gridWidth * col / app.cols + xOffset
    x1 = gridWidth * (col+1) / app.cols + xOffset
    y0 = gridHeight * row / app.rows + yOffset
    y1 = gridHeight * (row+1) / app.rows +yOffset
    return (x0, y0, x1, y1)

def drawGrid(app, canvas, xOffset=0, yOffset=0):
    for row in range(-1, app.rows+1):
        for col in range(-1, app.cols + 1):
            # col += xOffset
            # row += yOffset
            (x0, y0, x1, y1) = getCellBounds(app, row, col, xOffset, yOffset)
            canvas.create_rectangle(x0, y0, x1, y1, fill='white')

def drawDots(app, canvas):
    # shiftX = app.myDot.x + app.width/2
    # shiftY = app.myDot.y + app.height/2
    for dot in app.dots:
        dot.draw(canvas, app.gameCenter)
    for food in app.foodList:
        food.draw(canvas, app.gameCenter)

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

def drawBorder(app, canvas):
    canvas.create_rectangle(-app.gridWidth/2, -app.gridHeight/2, app.gridWidth/2, app.gridHeight/2, width=5)

def redrawAll(app, canvas):
    if app.mode == "menu":
        drawMenu(app, canvas)
    elif app.mode == "countdown":
        drawCountdown(app, canvas)
    elif app.mode == "gameover":
        drawGameOver(app, canvas)
    else:
        xOffset = - app.myDot.x % app.cellWidth
        yOffset = - app.myDot.y % app.cellHeight
        # print(xOffset, yOffset)
        print("*"*10)
        start = time.time()
        drawGrid(app, canvas, xOffset, yOffset)
        drawBorder(app, canvas)
        print("drawgrid=", time.time()-start)
    # if app.useCam:
    #     text = "Webcam not available"
    #     canvas.create_text(app.width/2, app.height - 20, text = text)
        print("*"*10)
        start = time.time()
        drawDots(app, canvas)
        print("drawdots=", time.time()-start)
        if app.useCam:
            canvas.create_image(app.width, app.height, anchor = SE, image = app.myDot.frame)

    # print(getVelocity(app))

def main():
    runApp(width = 1280, height = 720)
    # "/Users/carterweaver/Desktop/redhat.MOV"

main()
