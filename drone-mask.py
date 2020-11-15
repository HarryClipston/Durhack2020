import time, cv2
from threading import Thread
from djitellopy import Tello
import os
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

img = False
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
model = load_model("mask_recog_ver2.1")

route = list()
def readRoute():
   # global route
    file = open(r"droneRoute.txt", "r")
    fileSplit = file.read().split("\n")[1:]
    prev = ""
    counter = 0
    for command in fileSplit:
        type,value = command.split(" ")
        if prev == type:
            if prev != "c":
                counter += int(value)
            else:
                counter += value
        else:
            if prev != "":
                route.append([prev,counter])
            prev = type
            if prev != "c":
                counter = int(value)
            else:
                counter = value
    route.append([prev, counter])
    totv,toth,totr = [0,0,0]
    # for command in route:
    #     if command[0] == "v":
    #         totv += command[1]
    #     elif command[0] == "h":
    #         toth += command[1]
    #     elif command[0] == "r":
    #         totr += command[1]
    # if toth != 0:
    #     route.append(["h", -toth])
    # if totv != 0:
    #     route.append(["v", -totv])
    # if totr != 0:
    #     route.append(["r", -totr])




readRoute()

tello = Tello()

tello.connect()
checking = False

maskP = 0
keepRecording = True
tello.streamon()

#frame_read = tello.get_frame_read()
#img = frame_read.frame

def videoRecorder():
    global maskP, img
    # create a VideoWrite object, recoring to ./video.avi
    frame_read = tello.get_frame_read()
    height, width, _ = frame_read.frame.shape


    video = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 25, (width, height))
    #out.write(img)    #writes frame to file

    while keepRecording:
        frame = frame_read.frame
      #  cv2.imshow('drone', img)
      #  video.write(img)
        #time.sleep(1 / 30)
     #   cv2.waitKey(3)
        if img:
            img = False
            cv2.imwrite("picture.png", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray,
                                              scaleFactor=1.1,
                                              minNeighbors=5,
                                              minSize=(60, 60),
                                              flags=cv2.CASCADE_SCALE_IMAGE)
        faces_list = []
        preds = []
        for (x, y, w, h) in faces:
            face_frame = frame[y:y + h, x:x + w]
            face_frame = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
            face_frame = cv2.resize(face_frame, (224, 224))
            face_frame = img_to_array(face_frame)
            face_frame = np.expand_dims(face_frame, axis=0)
            face_frame = preprocess_input(face_frame)
            faces_list.append(face_frame)
            if len(faces_list) > 0:
                preds = model.predict(faces_list)
            for pred in preds:
                (mask, withoutMask) = pred
            if checking:
                maskP += mask - withoutMask
            label = "Mask :)" if mask > withoutMask else "NO MASK"
            color = (0, 255, 0) if label == "Mask :)" else (0, 0, 255)
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            # Display the resulting frame
        cv2.imshow('Video', frame)
        video.write(frame)
        cv2.waitKey(40)

    #video.release()


# we need to run the recorder in a seperate thread, otherwise blocking options
#  would prevent frames from getting added to the video
recorder = Thread(target=videoRecorder)
tello.RESPONSE_TIMEOUT = 4
print(tello.get_battery())
recorder.start()
tello.takeoff()
time.sleep(5)
# tof = tello.get_distance_tof()
# time.sleep(5)
# print(tof)
tello.move_up(100)
time.sleep(5)
for command in route:
    time.sleep(5)
    if command[0] == "v":
        if command[1] > 0:
            tello.move_forward(command[1])
        else:
            tello.move_back(-command[1])
    elif command[0] == "h":
        if command[1] > 0:
            tello.move_right(command[1])
        else:
            tello.move_left(-command[1])
    elif command[0] == "r":
        command[1] == command[1] % 360
        while command[1] > 180:
            command[1] = -360 + command[1]
        if command[1] > 0:
            tello.rotate_clockwise(command[1])
        else:
            tello.rotate_counter_clockwise(-command[1])
    elif command[0] == "c":
        tello.move_down(50)
        time.sleep(5)
        maskP = 0
        checking = True
        time.sleep(2)
        if maskP < 0:
            print("No mask!!!")
            file = open(r"trig2.txt","w")
            file.write(command[1])
            file.close()
        checking = False
        tello.move_up(50)
        time.sleep(5)


# time.sleep(5)
# tello.move_up(110)
# time.sleep(5)
# tello.move_left(20)
# time.sleep(5)
# tello.move_right(20)
# time.sleep(5)



tello.land()

keepRecording = False
recorder.join()