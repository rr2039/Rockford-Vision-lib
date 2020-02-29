import cv2 as cv
import numpy as np

vs = cv.VideoCapture(0)
hsvLimitLower = np.array([70, 90, 60])  # (H,S,V) #243
hsvLimitUpper = np.array([100, 255, 255])
visionProperties = {"areaMin": 3,
                    "widthMin": 10,
                    "widthMax": 1003,
                    "heightMin": 2,
                    "heightMax": 1003,
                    "vertexMin": 0,
                    "vertexMax": 1000000,
                    "ratioMin": 1,
                    "ratioMax": 1000,
                    "solidityMin": 5,
                    "solidityMax": 48}


def filterContours(contours):
    output = []
    global visionProperties
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if (w < visionProperties["widthMin"] or w > visionProperties["widthMax"]):
            continue
        if (h < visionProperties["heightMin"] or h > visionProperties["heightMax"]):
            continue
        area = cv.contourArea(contour)
        if area < visionProperties["areaMin"]:
            continue
        hull = cv.convexHull(contour)
        solid = 100 * area / cv.contourArea(hull)
        if (solid < visionProperties["solidityMin"]) or (solid > visionProperties["solidityMax"]):
            continue
        if (len(contour) < visionProperties["vertexMin"] or len(contour) > visionProperties["vertexMax"]):
            continue
        ratio = (float)(w) / h
        if (ratio < visionProperties["ratioMin"] or ratio > visionProperties["ratioMax"]):
            continue
        output.append(contour)
    return output


def isoTarget(dt):
    global vs
    global hsvLimitLower
    global hsvLimitUpper
    retval, frame = vs.read()
    # frame = cv.imread(r"9ft.png")
    cv.imshow('frame', frame)
    kernel = np.ones((5, 5), np.uint8)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, hsvLimitLower, hsvLimitUpper)
    cv.imshow('mask', mask)
    contours, hierarchy = cv.findContours(mask, 1, 2)
#   cnt = contours[0]
    backdrop = np.zeros((480, 640, 3))  # Backdrop to display the contours

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
        rect = cv.rectangle(backdrop, (x, y),
                            ((x + w), (y + h)), (255, 0, 0), 10)
        print(rect)
    except:
        pass
    cv.imshow('processed', cv.drawContours(backdrop,
              filteredContours, -1, (0, 255, 0), 3))

if __name__ == '__main__':
    while True:
        isoTarget(None)
        if cv.waitKey(1) == ord('\x1b'): # Escape Keycode
            break
    cv.destroyAllWindows()
