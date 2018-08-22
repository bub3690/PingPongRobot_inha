# coding: utf-8

import numpy as np
import cv2
import sys


from collections import deque
from imutils.video import VideoStream
import imutils
import argparse





# Create a VideoCapture object
cap = cv2.VideoCapture(0)
 
# Check if camera opened successfully
if (cap.isOpened() == False): 
  print("Unable to read camera feed")




greenLower = (0, 75, 204)
greenUpper = (32, 255, 247)



pts = deque(maxlen=64)


gtime=0
while True:

    gtime=gtime+1
    ret,color = cap.read()
    color = np.array(color, dtype=np.uint8)
    color = imutils.resize(color, width=1080)

    blurred = cv2.GaussianBlur(color, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)


    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None
 
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        x1 = int(M["m10"] / M["m00"])
        y1 = int(M["m01"] / M["m00"])
        # only proceed if the radius meets a minimum size
        if radius > 0:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(color, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(color, center, 5, (0, 0, 255), -1)

    pts.appendleft(center)
    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
 
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
        cv2.line(color, pts[i - 1], pts[i], (0, 0, 255), thickness)

    #if center:
    #    temp = 
    #    print(temp," ",gtime)

    cv2.imshow("color", color)



    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

cap.release()

sys.exit(0)

