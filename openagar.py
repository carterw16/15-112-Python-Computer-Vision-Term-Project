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
    app.nextId = 0
    # app.mapDims = (app.width, app.height)
    app.maxR = 30
    app.minR = 20
    app.gameCenter = (app.width/2, app.height/2)
    # app.mode = "menu"
    app.mode = "menu"
    app.countdownStart = None
    app.countdownNumber = 3
    # app.dotX = app.width/2
    # app.dotY = app.height/2
    app.velocity = (0,0)
    app.useCam = True
    app.timerDelay = 5
    # app.myDot = MyDot(app.width/2, app.height/2, 30, -1, app.timerDelay, app.useCam)
    app.myDot = MyDot(0, 0, 25, -1, app.timerDelay, app.useCam)
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

def createEnemies(app, count=1):
    enemyDots = []
    for i in range(count):
        enemyDots.append(Dot(random.randrange(-app.gridWidth/2, app.gridWidth/2), 
        random.randrange(-app.gridHeight/2,app.gridHeight/2),
        random.randrange(app.minR,app.maxR), app.nextId, app.timerDelay))
        app.nextId += 1
    return enemyDots

def getAllSubDotsAndFood(dots, food=None):
    ret = []
    for dot in dots:
        if type(dot) == Dot or type(dot) == MyDot:
            
            for subDot in dot.subDotList:
                ret.append(subDot)
        elif type(dot) == GameObject:
            ret.append(dot)
    return ret


def getOverlapping(dots):
    overlapping = []
    allSubDots = getAllSubDotsAndFood(dots)
    for i in range(len(allSubDots)):
        dot = allSubDots[i]
        for j in range(i+1, len(dots)):
            dot2 = allSubDots[j]
            # if dot.distance(dot.x, dot.y, dot2.x, dot2.y) < dot.r + dot2.r: 
            #     overlapping.append([dot, dot2])
            if dot.isOverlapping(dot2):
                overlapping.append([dot,dot2])
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
        # print("updatetree=", time.time()-start)
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
        # print(overlapping)
        for overlap in overlapping:
            overlap = sorted(overlap, key = lambda x: x.r)
            # print(f"***** {type(overlap[0])} {type(overlap[1])}")
            try:
                if type(overlap[0]) == GameObject and type(overlap[1]) == GameObject:
                    app.foodList.remove(overlap[0])
                elif isinstance(overlap[1], SubDot) and type(overlap[0]) == GameObject:
                    overlap[1].parent.grow(overlap[0].r, True)
                    app.foodList.remove(overlap[0])
                    # app.gameObjectTree.delete(overlap[0])
                    newFood = GameObject(random.randrange(-app.gridWidth/2, app.gridWidth/2),random.randrange(-app.gridHeight/2,app.gridHeight/2),5)
                    # app.gameObjectTree.insert(newFood)
                    app.foodList.append(newFood)
                # elif overlap[0].r < overlap[1].r and overlap[0] in app.dots and overlap[0].id != overlap[1].id:
                elif overlap[0].r < overlap[1].r:
                    # print("overlap", overlap[0], overlap[1])
                    # if overlap[0].id == -1:
                    #     print("overlap=", overlap[0])
                    overlap[1].parent.grow(overlap[0].r, False)
                    overlap[0].parent.removeSubDot(overlap[0])
                    if len(overlap[0].parent.subDotList) == 0:
                        app.dots.remove(overlap[0].parent)
                    # app.dots += createEnemies(app)
                    # Dot.allDots.remove(overlap[0])
                    # app.gameObjectTree.delete(overlap[0])
                    
                    # app.gameObjectTree.insert(newDot)
            except:
                print(overlapping)


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
    if event.key == "Space":
        app.myDot.split()

# def splitDot(app, dot):
#     print("hello")
#     newR = dot.r // 2
#     if dot is app.myDot:
#         dotList = [MyDot(app.myDot.x-newR, app.myDot.y-newR, newR, -1, app.timerDelay, app.useCam),
#         MyDot(app.myDot.x+newR, app.myDot.y+newR, newR, -1, app.timerDelay, app.useCam)]
#         x = app.myDot.x
#         y = app.myDot.y
#         app.myDot = SplitDot(dotList, x, y)
        
# getCellBounds from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
# added xOffset and yOffset
def getCellBounds(app, row, col, xOffset, yOffset):
    gridWidth = app.gridWidth
    gridHeight = app.gridHeight
    x0 = gridWidth * col / app.cols + xOffset
    x1 = gridWidth * (col+1) / app.cols + xOffset
    y0 = gridHeight * row / app.rows + yOffset
    y1 = gridHeight * (row+1) / app.rows +yOffset
    return (x0, y0, x1, y1)

#from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
def drawGrid(app, canvas, xOffset=0, yOffset=0):
    for row in range(-1, app.rows+1):
        for col in range(-1, app.cols + 1):
            (x0, y0, x1, y1) = getCellBounds(app, row, col, xOffset, yOffset)
            canvas.create_rectangle(x0, y0, x1, y1, fill='white')

def drawBorder(app, canvas):
    x0 = app.gameCenter[0] - app.gridWidth / 2
    x1 = app.gameCenter[0] + app.gridWidth / 2
    y0 = app.gameCenter[1] - app.gridHeight / 2
    y1 = app.gameCenter[1] + app.gridHeight / 2
    canvas.create_rectangle(x0, y0, x1, y1, 
    outline="red", width="5")

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
        # print("*"*10)
        start = time.time()
        drawGrid(app, canvas, xOffset, yOffset)
        drawBorder(app, canvas)
        # print("drawgrid=", time.time()-start)
    # if app.useCam:
    #     text = "Webcam not available"
    #     canvas.create_text(app.width/2, app.height - 20, text = text)
        start = time.time()
        drawDots(app, canvas)
        # print("drawdots=", time.time()-start)
        if app.useCam:
            canvas.create_image(app.width, app.height, anchor = SE, image = app.myDot.frame)

    # print(getVelocity(app))

def main():
    runApp(width = 1280, height = 720)
    # "/Users/carterweaver/Desktop/redhat.MOV"

main()
