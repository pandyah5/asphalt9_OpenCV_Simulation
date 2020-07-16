import cv2
import numpy as np
import math
import time
import ctypes

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

time.sleep(5)

cap = cv2.VideoCapture(0)
direct = "CENTER"
while(1):

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    width = cap.get(3)
    height = cap.get(4)

    lower_red = np.array([130,105,0])
    upper_red = np.array([179,255, 255])

    lower_green = np.array([37,117,119])
    upper_green = np.array([81,195,187])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_red, upper_red)
    mask1 = cv2.inRange(hsv, lower_green, upper_green)
#     # Bitwise-AND mask and original image
#     res = cv2.bitwise_and(frame,frame, mask= mask)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,'Asphalt 9: '+direct,(0,50), font, 1, (99,74,154), 3, cv2.LINE_AA)

    try:
        contours,hierarchy= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours, key = lambda x: cv2.contourArea(x))

        areacnt = cv2.contourArea(cnt)

        boxes = []
        for c in cnt:
            (x, y, w, h) = cv2.boundingRect(c)
            boxes.append([x,y, x+w,y+h])

        boxes = np.asarray(boxes)

        left = np.min(boxes[:,0])
        top = np.min(boxes[:,1])
        right = np.max(boxes[:,2])
        bottom = np.max(boxes[:,3])
        cv2.rectangle(frame, (left,top), (right,bottom), (255, 0, 0), 2)


        if ((left + right)/2 > 2*width/3):
            if ((left + right)/2 > 5*width/6):
                PressKey(0x4B)
                time.sleep(0.1)
                ReleaseKey(0x4B)
                direct = "EX_LEFT"
            else:
                PressKey(0x4B)
                time.sleep(0.05)
                ReleaseKey(0x4B)
                direct = "LEFT"


        elif ((left + right)/2 < width/3):
            if ((left + right)/2 < width/6):
                PressKey(0x4D)
                time.sleep(0.1)
                ReleaseKey(0x4D)
                direct = "EX_RIGHT"
            else:
                PressKey(0x4D)
                time.sleep(0.05)
                ReleaseKey(0x4D)
                direct = "RIGHT"

        else:
            direct = "CENTER"

        if areacnt < 5000:
            PressKey(0x39)
            time.sleep(0.01)
            ReleaseKey(0x39)
            PressKey(0x39)
            time.sleep(0.01)
            ReleaseKey(0x39)

        cont,hier= cv2.findContours(mask1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cntr = max(cont, key = lambda x: cv2.contourArea(x))

        areacnt_g = cv2.contourArea(cntr)

        if areacnt_g > 1500:
            PressKey(0x1C)
            time.sleep(0.01)
            ReleaseKey(0x1C)

    except:
        pass


    cv2.imshow('frame',frame)
    cv2.imshow('green mask',mask1)
    cv2.imshow('red mask',mask)
#     cv2.imshow('res',res)
    m = cv2.waitKey(5) & 0xFF
#     k = cv2.waitKey(5) & 0xFF

#     if k == 27: # Exit condition
#         break

    if m==32:
        print(areacnt_g)

cv2.destroyAllWindows()
cap.release()
