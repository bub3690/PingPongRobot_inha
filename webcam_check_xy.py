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

"""
1번째 카메라
 640 , 480 화소로 x,y 좌표 구하기.
 네트의 중앙이 (0,0)
화면의 가로 =640px , 탁구대의 세로일부 =  ??~~최대 2.74m
화면의 세로 =480px : 탁구대의 가로모두=1.525m  --> 1픽셀당 
"""
cam1_pixel_horizontal=cap1.get(3)
cam1_pixel_vertical=cap1.get(4)

cam1_pixel_per_meter_horizontal=2.74/cam1_pixel_horizontal
cam1_pixel_per_meter_vertical= 1.525/cam1_pixel_vertical

greenLower = (0, 75, 204)
greenUpper = (32, 255, 247)



pts = deque(maxlen=64)


gtime=0
while True:

    gtime=gtime+1
    ret,color = cap1.read()
    color = np.array(color, dtype=np.uint8)

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

    if center:
        x1=-x1+320;y1=-y1+240;
        x1=x1*cam1_pixel_per_meter_horizontal
        y1=y1*cam1_pixel_per_meter_vertical
        temp=x1,y1
        print(temp," ",gtime)

    cv2.imshow("color", color)



    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

cap.release()

sys.exit(0)


