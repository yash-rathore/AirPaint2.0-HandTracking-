'''
make airpaint wihtout using masking , but by using hand recognition model.

1 => detect hand , fingers and landmarks √
2 => detect which fingers are up √
    if only index alone:
        drawing mode: get (cx,cy) of index tip follow same as air paint 1.0
    if index+middle up:
        selection mode: get (cx,cy) of middle of both tips of index and middle follow same as air paint 1.0
'''
import cv2
import handtrackingmodule as htm
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

overlay = cv2.imread('overlay.PNG')
color = (0, 0, 0)
detector = htm.handdetector(maxhands=1)
xp,yp=0,0

brushthickness=5
eraserthickness=50

paintwindow=np.zeros((720,1280,3),np.uint8)

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # adding overlay image to frame
    h, w, c = overlay.shape
    frame[0:h, 0:w] = overlay
    frame = detector.findhands(frame=frame)
    lmlist = detector.findposition(frame=frame, draw=False)

    # counting which combination of fingers are up
    fingers = []

    # checking for index and middle fingers
    if len(lmlist) != 0:
        # drawing mode
        if lmlist[8][2] < lmlist[7][2] and lmlist[12][2] > lmlist[11][2]:  # only index is up
            cx1,cy1=lmlist[8][1], lmlist[8][2]
            cv2.circle(frame, (cx1,cy1), 8, color, -1)

            if xp==0 and yp==0:
                xp,yp=cx1,cy1
            cv2.line(frame,(xp,yp) ,(cx1,cy1), color, brushthickness)
            cv2.line(paintwindow,(xp,yp) ,(cx1,cy1), color, brushthickness)
            xp,yp=cx1,cy1

            if color==(0,0,0):
                cv2.line(frame, (xp, yp), (cx1, cy1), color, eraserthickness)
                cv2.line(paintwindow, (xp, yp), (cx1, cy1), color, eraserthickness)

        # selection mode
        elif lmlist[8][2] < lmlist[7][2] and lmlist[12][2] < lmlist[11][2]:  # index and middle is up
            xp, yp = 0, 0
            cx, cy = (lmlist[12][1] + lmlist[8][1]) // 2, (lmlist[12][2] + lmlist[11][2]) // 2
            if cy < 200:
                if cx >= 280 and cx <= 400:
                    color = (0, 0, 255)
                elif cx >= 500 and cx <= 615:
                    color = (0, 255, 0)
                elif cx >= 700 and cx <= 815:
                    color = (255, 0, 0)
                elif cx >= 890 and cx <= 1012:
                    color = (0, 255, 255)
                elif cx >= 1100 and cx <= 1280:
                    color=(0,0,0)
                else:
                    print("logo")
            cv2.circle(frame, (cx, cy), 10, color, -1)

    imggray=cv2.cvtColor(paintwindow,cv2.COLOR_BGR2GRAY)
    _,imginv=cv2.threshold(imggray,50,255,cv2.THRESH_BINARY_INV)
    imginv=cv2.cvtColor(imginv,cv2.COLOR_GRAY2BGR)
    frame=cv2.bitwise_and(frame,imginv)
    frame=cv2.bitwise_or(frame,paintwindow)

    cv2.imshow('live', frame)
    cv2.imshow('paintwindow', paintwindow)

    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
