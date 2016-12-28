import cv2
import numpy as np
import math
import serial

j = 0

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    ret, img = cap.read()
    cv2.rectangle(img, (300, 300), (100, 100), (0, 255, 0), 0)
    crop_img = img[100:300, 100:300]
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cv2.imshow('Thresholded', thresh1)

    (version, _, _) = cv2.__version__.split('.')

    if version is '3':
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                                                      cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    elif version is '2':
        contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, \
                                               cv2.CHAIN_APPROX_NONE)

    cnt = max(contours, key=lambda x: cv2.contourArea(x))

    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(crop_img, (x, y), (x + w, y + h), (0, 0, 255), 0)
    hull = cv2.convexHull(cnt)
    drawing = np.zeros(crop_img.shape, np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
    hull = cv2.convexHull(cnt, returnPoints=False)
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

    ####################################################################to transfer output through serial port to hardware
    # import serial

    # ser = serial.Serial(port='COM7',baudrate=9600,parity=serial.PARITY_ODD,stopbits=serial.STOPBITS_TWO,bytesize=serial.EIGHTBITS)  # define what is required
    ser = serial.Serial(port='COM4',baudrate=9600)  # port name is visible in device manager, take baudrate same everywhere
    #####################################################################


    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
        if angle <= 90:
            count_defects += 1
            cv2.circle(crop_img, far, 1, [0, 0, 255], -1)
        # dist = cv2.pointPolygonTest(cnt,far,True)
        cv2.line(crop_img, start, end, [0, 255, 0], 2)
        # cv2.circle(crop_img,far,5,[0,0,255],-1)
    if count_defects == 3:
        cv2.putText(img, "3", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        j = 3;
        # write the data
        # ser.write(b'1')
    elif count_defects == 2:
        cv2.putText(img, "2", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        if j == 3:
            print('2')
            j = j + 1
        # write the data
        ser.write(b'2')
    elif count_defects == 1:
        cv2.putText(img, "1", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        if j == 3:
            print('1')
            j = j + 1
        # write the data
        ser.write(b'1')
    elif count_defects == 4:
        cv2.putText(img, "4", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        if j == 3:
            print('4')
            j = j + 1
            # write the data
        ser.write(b'4')
    else:
        cv2.putText(img, "5", (50, 50), \
                    cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        if j == 3:
            print('5')
            j = j + 1
            # write the data
        ser.write(b'5')

    # cv2.imshow('drawing', drawing)
    # cv2.imshow('end', crop_img)
    cv2.imshow('Gesture', img)
    all_img = np.hstack((drawing, crop_img))
    cv2.imshow('Contours', all_img)
    k = cv2.waitKey(10)
    if k == 27:
        break
