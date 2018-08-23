# coding: utf-8

import numpy as np
import cv2
import sys


from collections import deque
from imutils.video import VideoStream
import imutils
import argparse

# Create a VideoCapture object
cap1 = cv2.VideoCapture(1)
 
# Check if camera opened successfully
if (cap1.isOpened() == False): 
  print("Unable to read camera feed")


print('width: {0}, height: {1}'.format(cap1.get(3),cap1.get(4)))



# callback함수
def find_edge(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(color,(x,y), 100,(255,0,0),-1)
        temp=x,y
        print(temp)



ret,color = cap1.read()
color = np.array(color, dtype=np.uint8)
cv2.imshow("image", color)
cv2.setMouseCallback('image', find_edge)


while(1):
    ret,color = cap1.read()
    color = np.array(color, dtype=np.uint8)
    cv2.imshow("image", color)
    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

cap1.release()
cv2.destroyAllWindows()