import cv2
import numpy as np


def loadImage(imgName):
    img = cv2.imread(f"/Users/carterweaver/Desktop/{imgName}")
    return img

def showImage(img, title=""):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def randArray(height=200, width=200):
    arr = np.random.rand(height, width, 3)
    return arr

def testShowImages():
    img = loadImage("barney-stinson-bro-code.jpg")
    showImage(img)
    arr = randArray()
    showImage(arr)

def getColorMask(img, minHue, maxHue):
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


def videoFilter(path):
    cap = cv2.VideoCapture(path)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        mask = getColorMask(frame, 170, 10)
        maxContour, contourImg = getContours(mask, frame)
        contourImgWithCenter = drawCenterOfCountour(maxContour, contourImg)

        # Display the resulting frame
        cv2.imshow('frame', contourImgWithCenter)
        if cv2.waitKey(1) & 0xFF == ord('\r'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def getContours(mask, img=None):
    if img is None:
        dims = (mask.shape[0],mask.shape[1],3)
        contourImg = np.zeros(dims)
    else:
        contourImg = img
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

def drawCenterOfCountour(contour, contourImg):
    center = getCenterOfContour(contour)
    if center == None:
        return contourImg
    else:
        contourImg = cv2.circle(contourImg, center, 10, (255,0,0), -1)
        return contourImg

def getCenterOfContour(contour):
    if len(contour) != 0:
        #moments from https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return (cX, cY)
    return None

def main():
    # img = loadImage("redball.jpeg")
    # redMask = getRedMask(img)
    # maxContour, contourImg = findContours(redMask)
    # contourImg = drawCenterOfCountour(maxContour, contourImg)
    # showImage(contourImg)

    videoFilter(0)
    # "/Users/carterweaver/Desktop/redhat.MOV"

main()