import cv2 as cv
import mediapipe as mp
from exercise import Bandvent, OneArm, Run, DumbelFront
import time
import network
import numpy as np

mp_pose = mp.solutions.pose

flag = 0
sports = None
state = None

def initialize_camera():
    camera = cv.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera.")
        return None
    # ret = camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    # ret = camera.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
    return camera

def process_model_image(pose, model_path):
    model = cv.imread(model_path)
    if model is None:
        print(f"Error: Could not read model image at {model_path}.")
        return None
    model = cv.resize(model, (640, 360))
    model_frame = cv.cvtColor(model, cv.COLOR_BGR2RGB)
    return pose.process(model_frame)

def process_frame(pose, frame):
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    return pose.process(rgb_frame)

def overlay_text(frame, text, position=(10, 30)):
    cv.putText(frame, text, position, cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)

def run_pose_detection(camera, pose, sports, model_path):
    model = process_model_image(pose, model_path)
    if model is None:
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame from camera.")
            break

        print(">>>>send state is", network.send_state)
        frame = cv.flip(frame, 0)
        
        # 오버레이 텍스트 추가
        overlay_text(frame, f"State: {network.send_state}", (10, 30))

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        frame = process_frame(pose, frame)
        if sports == 'bandvent':
            instance = Bandvent(model=model, frame=frame)
            if state == 'checkstart':
                instance.check_foot()
            elif state == 'bodycheckstart':
                instance.check_body_angle()
            elif state == 'handcheckstart':
                instance.check_hand()
            if network.send_state == 'handcheckend':
                network.send_state = 'checkend'
                time.sleep(0.3)
                break
        elif sports == 'onearm':
            instance = OneArm(model=model, frame=frame)
            if state == 'checkstart':
                instance.check_arm()
            if network.send_state == 'armcheckend':
                network.send_state = 'checkend'
                print(">>>>>>>checkend")
                time.sleep(0.3)
                break
            
        elif sports == 'dumbelfront':
            instance = DumbelFront(model=model, frame=frame)
            if state == 'checkstart':
                instance.check_arm()
            if network.send_state == 'armcheckend':
                network.send_state = 'checkend'
                print(">>>>>>>checkend")
                time.sleep(0.3)
                break
            
        else:
            break

        time.sleep(0.2)

    cv.destroyAllWindows()
    camera.release()

def pose_detect():
    try:
        camera = initialize_camera()
        if camera is None:
            return
        
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            model_path = f'/home/pi/HELPT/sample_shot/{sports}/frame/frame_0.jpg'
            run_pose_detection(camera, pose, sports, model_path)
            

    except KeyboardInterrupt:
        print(">>>>>>>>>>>>>>>>>>>>>>>>Camera interrupt")

def exercise_detect():
    try:
        camera = initialize_camera()
        if camera is None:
            return
        
        frame_counter = -1

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while True:
                ret, frame = camera.read()
                frame_counter = frame_counter + 1
                if not ret:
                    print("Error: Could not read frame from camera.")
                    break

                frame = cv.resize(frame, (640, 360))
                frame = cv.flip(frame, 0)
                
                # 오버레이 텍스트 추가
                overlay_text(frame, f"Frame: {frame_counter}", (10, 30))
                overlay_text(frame, f"State: {network.send_state}", (10, 60))

                cv.imshow('frame', frame)
                image_frame = frame
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

                frame = process_frame(pose, frame)
            
                model_path = f'/home/pi/HELPT/sample_shot/{sports}/frame/frame_{frame_counter}.jpg'

                model = cv.imread(model_path)
                
                if model is None:
                    print("Error: Could not read model image.")
                    return

                model = cv.resize(model, (640, 360))
                model_frame = cv.cvtColor(model, cv.COLOR_BGR2RGB)
                model = pose.process(model_frame)
                
                if model != None:

                    if state == 'runstart':
                        run_instance = Run(model=model, frame=frame, frameimg = image_frame)
                        network.send_state = run_instance.combined_check()
                        if network.send_state[0] == 'n':
                            time.sleep(1)

                    if state == 'end':
                        report = run_instance.make_report()
                        network.send_state = 'd' + report
                        print(network.send_state)
                        time.sleep(0.5)
                        break

                    print("frame counter", frame_counter, "network send", network.send_state)
                    if frame_counter == 5:
                        frame_counter = 0
                        
                elif sports == None:
                    continue
                
                if model is None:
                    break

                time.sleep(0.5)

            cv.destroyAllWindows()
            camera.release()
    except KeyboardInterrupt:
        print(">>>>>>>>>>>>>>>>>>>>>>>>Camera interrupt")

def main():
    global flag, state
    while True:
        if sports == 'bandvent' or sports == 'onearm' or sports == 'dumbelfront':
            flag = 1
        if state == 'checkstart' and flag == 1:
            pose_detect()
            flag = 2
            state = None
        elif state == 'runstart':
            exercise_detect()
            state = None
        time.sleep(0.1)

if __name__ == "__main__":
    main()
