import cv2
import sys

vs = cv2.VideoCapture(3)
vs.set(3,1280)
vs.set(4,800)
ret, frame = vs.read()
cv2.imwrite('photo{0}.jpg'.format(str(sys.argv)), frame)
