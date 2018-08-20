# coding: utf-8

import numpy as np
import cv2
import sys
from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel

try:
    from pylibfreenect2 import OpenGLPacketPipeline
    pipeline = OpenGLPacketPipeline()
except:
    try:
        from pylibfreenect2 import OpenCLPacketPipeline
        pipeline = OpenCLPacketPipeline()
    except:
        from pylibfreenect2 import CpuPacketPipeline
        pipeline = CpuPacketPipeline()


from collections import deque
from imutils.video import VideoStream
import imutils

def callback(x):
    pass


print("Packet pipeline:", type(pipeline).__name__)

# Create and set logger
logger = createConsoleLogger(LoggerLevel.Debug)
setGlobalLogger(logger)

fn = Freenect2()
num_devices = fn.enumerateDevices()
if num_devices == 0:
    print("No device connected!")
    sys.exit(1)

serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial, pipeline=pipeline)

listener = SyncMultiFrameListener(
    FrameType.Color | FrameType.Ir | FrameType.Depth)

# Register listeners
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()

# NOTE: must be called after device.start()
registration = Registration(device.getIrCameraParams(),
                            device.getColorCameraParams())

undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

# Optinal parameters for registration
# set True if you need
need_bigdepth = False
need_color_depth_map = False

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
    if need_color_depth_map else None

cv2.namedWindow('image')

ilowH = 0
ihighH = 360

ilowS = 0
ihighS = 255
ilowV = 0
ihighV = 255

# create trackbars for color change
cv2.createTrackbar('lowH','image',ilowH,360,callback)
cv2.createTrackbar('highH','image',ihighH,360,callback)

cv2.createTrackbar('lowS','image',ilowS,255,callback)
cv2.createTrackbar('highS','image',ihighS,255,callback)

cv2.createTrackbar('lowV','image',ilowV,255,callback)
cv2.createTrackbar('highV','image',ihighV,255,callback)



while True:
    frames = listener.waitForNewFrame()

    color = frames["color"]
    ir = frames["ir"]
    depth = frames["depth"]

    # registration.apply(color, depth, undistorted, registered,
    #                    bigdepth=bigdepth,
    #                    color_depth_map=color_depth_map)

    
    frame2 = cv2.resize(color.asarray(),(int(1920 / 3), int(1080 / 3)))

    # get trackbar positions
    ilowH = cv2.getTrackbarPos('lowH', 'image')
    ihighH = cv2.getTrackbarPos('highH', 'image')
    ilowS = cv2.getTrackbarPos('lowS', 'image')
    ihighS = cv2.getTrackbarPos('highS', 'image')
    ilowV = cv2.getTrackbarPos('lowV', 'image')
    ihighV = cv2.getTrackbarPos('highV', 'image')

    hsv = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([ilowH, ilowS, ilowV])
    higher_hsv = np.array([ihighH, ihighS, ihighV])
    mask = cv2.inRange(hsv, lower_hsv, higher_hsv)

    frame2 = cv2.bitwise_and(frame2, frame2, mask=mask)


    # NOTE for visualization:
    # cv2.imshow without OpenGL backend seems to be quite slow to draw all
    # things below. Try commenting out some imshow if you don't have a fast
    # visualization backend.
    #cv2.imshow("ir", ir.asarray() / 65535.)
    #cv2.imshow("depth", depth.asarray() / 4500.)
    #cv2.imshow("color", cv2.resize(color.asarray(),(int(1920 / 3), int(1080 / 3))))

    cv2.imshow("image", frame2)


    #cv2.imshow("registered", registered.asarray(np.uint8))

    if need_bigdepth:
        cv2.imshow("bigdepth", cv2.resize(bigdepth.asarray(np.float32),
                                          (int(1920 / 3), int(1082 / 3))))
    if need_color_depth_map:
        cv2.imshow("color_depth_map", color_depth_map.reshape(424, 512))

    listener.release(frames)

    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

device.stop()
device.close()

sys.exit(0)