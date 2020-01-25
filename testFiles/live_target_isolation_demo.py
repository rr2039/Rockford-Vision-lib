import cv2 as cv
import numpy as np
from statistics import median
from imutils.video import VideoStream

def filterContours(contours):
    output = []
    min_area = 3
    min_width = 10
    max_width = 1003
    min_height = 2
    max_height = 1003
    min_vertex = 0
    max_vertex = 1000000
    min_ratio = 1
    max_ratio = 1000
    min_solidity = 5
    max_solidity = 48

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if (w < min_width or w > max_width):
            continue
        if (h < min_height or h > max_height):
            continue
        area = cv.contourArea(contour)
        if area < min_area:
            continue
        hull = cv.convexHull(contour)
        solid = 100 * area / cv.contourArea(hull)
        if (solid < min_solidity) or (solid > max_solidity):
            continue
        if (len(contour) < min_vertex or len(contour) > max_vertex):
            continue
        ratio = (float)(w) / h
        if (ratio < min_ratio or ratio > max_ratio):
            continue
        output.append(contour)
    return output


def hsvFilter(hsv_img):
    lower_hsv_limits = np.array([70, 90, 60])  # (H,S,V) #243
    upper_hsv_limits = np.array([100, 255, 255])
    return cv.inRange(hsv_img, lower_hsv_limits, upper_hsv_limits)

def main():
    vs = VideoStream(src=2).start()
    while True:
        frame = vs.read()
        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):
            break
        kernel = np.ones((5, 5), np.uint8)

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = hsvFilter(hsv)
        cv.imshow('mask', mask)
        contours, hierarchy = cv.findContours(mask, 1, 2)
#        cnt = contours[0]
        backdrop = np.zeros((480, 640, 3))  # Creating a black backdrop to display the contours on

        frame_and_target_contour = frame
        filteredContours = filterContours(contours)
        try:
            cnt = filteredContours[0]
            M = cv.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            print(cx)
            print(cy)
        except:
            pass
        try:
            x, y, w, h = cv.boundingRect(filteredContours[0])
            rect = cv.rectangle(backdrop, (x, y), ((x + w), (y + h)), (255, 0, 0), 10)
            print(rect)
        except:
            pass

        cv.imshow('processed',  cv.drawContours(backdrop, filteredContours, -1, (0,255,0),3))


main()
cv.destroyAllWindows()
