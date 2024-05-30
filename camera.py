import cv2 as cv
import mediapipe as mp
from exercise import Bandvent
import time
import network
import numpy as np

mp_pose = mp.solutions.pose

flag = 0

def pose_detect():
    fps = 5  # 2fps로 설정
    
    try:
        camera = cv.VideoCapture(0)
        if not camera.isOpened():
            print("Error: Could not open camera.")
            return
        
        ret = camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        ret = camera.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
        
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            model = cv.imread('/home/pi/HELPT/sample_shot/bandvent/frame/frame_0.jpg')
            if model is None:
                print("Error: Could not read model image.")
                return

            model = cv.resize(model, (640, 360))
            model_frame = cv.cvtColor(model, cv.COLOR_BGR2RGB)
            model = pose.process(model_frame)
            
            while True:
                ret, frame = camera.read()
                if not ret:
                    print("Error: Could not read frame from camera.")
                    break  # No more frames, break
                
                print(">>>>send state is", network.send_state)
                frame = cv.resize(frame, (640, 360))
                frame = cv.flip(frame, 0)  # Flip horizontally instead of vertically
                cv.imshow('frame', frame)
                if cv.waitKey(1) & 0xFF == ord('q'):  # Add a way to exit the loop
                    break

                rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                frame = pose.process(rgb_frame)

                bandvent_instance = Bandvent(model=model, frame=frame)

                if network.rec_state == 'bandventcheckstart':
                    bandvent_instance.check_foot()
                elif network.rec_state == 'bodycheckstart':
                    bandvent_instance.check_body_angle()
                elif network.rec_state == 'handcheckstart':
                    bandvent_instance.check_hand()
                elif network.send_state == 'handcheckend':
                    print("<<<<break>>>")
                    break
                else:
                    continue
                
                time.sleep(1/fps)  # Adjust sleep time for fps

            cv.destroyAllWindows()
            camera.release()
    except KeyboardInterrupt:
        print(">>>>>>>>>>>>>>>>>>>>>>>>Camera interrupt")

def exercise_detect():
    fps = 2  # 2fps로 설정
    
    frame_counter = -1
    try:
        camera = cv.VideoCapture(0)
        print(">>>>>>>exercise detect start>>>>>>>")
        if not camera.isOpened():
            print("Error: Could not open camera.")
            return
        
        ret = camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        ret = camera.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
        
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            start_time = time.time()

            while True:
                ret, frame = camera.read()
                frame_counter = frame_counter + 1
                if not ret:
                    print("Error: Could not read frame from camera.")
                    break  # No more frames, break
                
                frame = cv.resize(frame, (640, 360))
                frame = cv.flip(frame, 0)  # Flip horizontally instead of vertically
                # cv.imshow('frame', frame)
                if cv.waitKey(1) & 0xFF == ord('q'):  # Add a way to exit the loop
                    break

                rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                frame = pose.process(rgb_frame)
                
                model_path = f'/home/pi/HELPT/sample_shot/bandvent/frame/frame_{frame_counter}.jpg'
                model = cv.imread(model_path)
                
                if model is None:
                    print(f"Error: Could not read model image at {model_path}.")
                    break
            
                model = cv.resize(model, (640, 360))
                cv.imshow('model', model)
                rgb_model_frame = cv.cvtColor(model, cv.COLOR_BGR2RGB)
                model = pose.process(rgb_model_frame)
                
                bandvent_instance = Bandvent(model=model, frame=frame)

                if network.rec_state == 'bandventrunstart':
                    tilt_state = bandvent_instance.tilt_check()
                    accuracy = bandvent_instance.accuracy_check()
                    if tilt_state == "e" or accuracy == "e":
                        network.send_state = 'notfound'
                    else:
                        network.send_state = tilt_state + accuracy
                
                if network.rec_state == 'bandventend':
                    network.send_state = 'bandventalldone'
                    break
                
                print("frame counter", frame_counter, "network send", network.send_state)
                if frame_counter == 5:
                    frame_counter = 0
                    
                time.sleep(1)

            cv.destroyAllWindows()
            camera.release()
    except KeyboardInterrupt:
        print(">>>>>>>>>>>>>>>>>>>>>>>>Camera interrupt")

def main():
    global flag
    print(">>>>>>>main>>>>>>>>")
    while True:
        if network.rec_state == 'bandventcheckstart' and flag == 0:
            print("pose detect")
            flag = 1
            pose_detect()
            print("pose detect end")
        if network.rec_state == 'bandventrunstart':
            print("exercise detect")
            exercise_detect()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
