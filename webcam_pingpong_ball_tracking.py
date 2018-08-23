# coding: utf-8

#탁구대 규격 세로 2.74m , 높이 : 0.76 m, 가로: 1.525 m 네트높이 : 15.25cm --> 0.1525m 
#   x,y 좌표를 찾기 위한 2m 높이 카메라 코드 + z 축 카메라 찾기위한 정면 카메라
#  3 좌표 모두 잡히면 속도를 측정.


import numpy as np
import cv2
import sys


from collections import deque
from imutils.video import VideoStream
import imutils
import argparse



# Create a VideoCapture object
#카메라 두개 이용.

cap1 = cv2.VideoCapture(0)
cap2 =cv2.VideoCapture(1)
# Check if camera opened successfully
if (cap1.isOpened() == False): 
  print("첫번째 카메라가 열리지 않습니다.")

if (cap2.isOpened() == False): 
  print("두번째 카메라가 열리지 않습니다.")
  # 3은 width, 4는 height
print('width: {0}, height: {1}'.format(cap1.get(3),cap1.get(4)))
print('width: {0}, height: {1}'.format(cap2.get(3),cap2.get(4)))
"""
1번째 카메라
 640 , 480 화소로 x,y 좌표 구하기.
 네트의 중앙이 (0,0)
화면의 가로 =640px , 탁구대의 세로일부 =  ??~~최대 2.74m
화면의 세로 =480px : 탁구대의 가로모두=1.525m  --> 1픽셀당 
"""
cam1_pixel_horizontal=cap1.get(3)
cam1_pixel_vertical=cap1.get(4)

cam2_pixel_horizontal=cap2.get(3)
cam2_pixel_vertical=cap2.get(4)
"""
2번째 카메라
 640 , 480 화소로 y,z 좌표 구하기.
0.76m 중간 지점이 (0,0)
화면의 가로 =640px , 탁구대의 세로일부 =  ??~~최대 2.74m
화면의 세로 =480px : 탁구대의 높이+~~=약 1m  --> 1픽셀당 
"""



cam1_pixel_per_meter_horizontal=2.74/cam1_pixel_horizontal
cam1_pixel_per_meter_vertical= 1.525/cam1_pixel_vertical

cam2_pixel_per_meter_horizontal=2.74/cam2_pixel_horizontal
cam2_pixel_per_meter_vertical= 1.525/cam2_pixel_vertical




#화소 정하기
#cap.set(3,1080)
#cap.set(4,480)


greenLower = (0, 75, 204)
greenUpper = (32, 255, 247)


pts = deque(maxlen=64)
pts2 = deque(maxlen=64)

gtime=0
while True:

    gtime=gtime+1
    ret,color = cap1.read()
    color = np.array(color, dtype=np.uint8)

    ret2,color2 = cap2.read()
    color2 = np.array(color2, dtype=np.uint8)


    blurred = cv2.GaussianBlur(color, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    blurred2 = cv2.GaussianBlur(color2, (11, 11), 0)
    hsv2 = cv2.cvtColor(blurred2, cv2.COLOR_BGR2HSV)



    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    mask2 = cv2.inRange(hsv2, greenLower, greenUpper)
    mask2 = cv2.erode(mask2, None, iterations=2)
    mask2 = cv2.dilate(mask2, None, iterations=2)



    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None

    cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts2 = cnts2[0] if imutils.is_cv2() else cnts2[1]
    center2 = None




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



    if len(cnts2) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts2, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        x2 = int(M["m10"] / M["m00"])
        y2 = int(M["m01"] / M["m00"])
        # only proceed if the radius meets a minimum size
        if radius > 0:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(color, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(color, center, 5, (0, 0, 255), -1)

    pts2.appendleft(center2)
    # loop over the set of tracked points
    for i in range(1, len(pts2)):
        # if either of the tracked points are None, ignore
        # them
        if pts2[i - 1] is None or pts2[i] is None:
            continue
 
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
        cv2.line(color2, pts2[i - 1], pts2[i], (0, 0, 255), thickness)


    if center and center2:
        x1=-x1+320;y1=-y1+240;
        x1=x1*cam1_pixel_per_meter_horizontal
        y1=y1*cam1_pixel_per_meter_vertical
        temp=x1,y1
        print(temp," ",gtime)

    cv2.imshow("color", color)
    cv2.imshow("color2", color2)


    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

cap1.release()
cap2.release()
sys.exit(0)

