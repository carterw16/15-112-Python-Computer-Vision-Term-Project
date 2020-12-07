import cv2
import numpy as np

def getColorMask(img, hueRange, satRange=(180,255), valRange=(100,255)):
    # cv2.cvtColor from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/
    # py_gui/py_video_display/py_video_display.html
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    minH, maxH = hueRange[0], hueRange[1]
    minS, maxS = satRange[0], satRange[1]
    minV, maxV = valRange[0], valRange[1]
    if minH > maxH:
        minHSV = np.array([0,minS,minV])
        maxHSV = np.array([maxH,maxS,maxV])
        mask1 = cv2.inRange(hsv, minHSV, maxHSV)
        minHSV = np.array([minH,minS,minV])
        maxHSV = np.array([179,maxS,maxV])
        mask2 = cv2.inRange(hsv, minHSV, maxHSV)
        mask = cv2.bitwise_or(mask1,mask2)
    else:
        minHSV = np.array([minH,minS,minV])
        maxHSV = np.array([maxH,maxS,maxV])
        mask = cv2.inRange(hsv, minHSV, maxHSV)
    return mask

def calibrate(cap, x, y):
    frame = readCap(cap)
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pixelHSV = hsvFrame[int(y)][int(x)]
    hueRange = (pixelHSV[0] - 10, (pixelHSV[0] + 10) % 179)
    satRange = (pixelHSV[1] - 50, pixelHSV[1] + 50)
    valRange = (pixelHSV[2] - 50, pixelHSV[2] + 50)
    return hueRange, satRange, valRange


def readCap(cap):
    ret, frame = cap.read()
    return cv2.flip(frame, 1)

def getPositionFromVideo(cap, hueRange, satRange=(180,255), valRange=(100,255)):
    # if statement header from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/
    # py_gui/py_video_display/py_video_display.html
    # if cap is None or not cap.isOpened():
    frame = readCap(cap)
    mask = getColorMask(frame, hueRange, satRange, valRange)
    maxContour, contourImg = getContours(mask, frame)
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