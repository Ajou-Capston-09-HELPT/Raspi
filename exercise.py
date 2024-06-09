import numpy as np
import mediapipe as mp
import cv2 as cv
import time
import constant
from sports import PoseComparator
from collections import Counter
import network


mp_pose = mp.solutions.pose

total_accuracy = []
total_tilt = []
accuracy_max = -100

class Bandvent:
    def __init__(self, model, frame):
        self.model = model
        self.frame = frame
        self.comparator = PoseComparator(model, frame)
    
    def check_foot(self):
        # print("model pose pose landmarks", self.model.pose_landmarks) 
        if self.frame.pose_landmarks is not None:
            foot_state = self.comparator.return_similarity(
                self.model.pose_landmarks.landmark[23:33],
                self.frame.pose_landmarks.landmark[23:33]
            )
            if foot_state > 0.6:
                network.send_state = 'footcheckend'
            else:
                network.send_state = 'standby'
                
        else:
            network.send_state = 'notfound'

    def check_body_angle(self):
        if self.frame.pose_landmarks is not None:
            body_angle_state = self.comparator.return_body_similarity(
                self.model.pose_landmarks.landmark,
                self.frame.pose_landmarks.landmark
            )
            if body_angle_state > 0.03:
                network.send_state = 'bodycheckend'
            else:
                network.send_state = 'standby'
        else:
            network.send_state = 'notfound'

    def check_hand(self):
        if self.frame.pose_landmarks is not None:
            hand_state = self.comparator.return_similarity(
                self.model.pose_landmarks.landmark[11:21],
                self.frame.pose_landmarks.landmark[11:21]
            )
            if hand_state > 0.7:
                network.send_state = 'handcheckend'
                time.sleep(0.5)
            else:
                network.send_state = 'standby'
        else:
            network.send_state = 'notfound'


class OneArm:
    def __init__(self, model, frame):
        self.model = model
        self.frame = frame
        self.comparator = PoseComparator(model, frame)
        
    def check_arm(self):
        print("check arm start")
        if self.frame.pose_landmarks is not None:
            arm_state = self.comparator.return_similarity(
                self.model.pose_landmarks.landmark[11:17],
                self.frame.pose_landmarks.landmark[11:17]
            )
            if arm_state > 0.5:
                network.send_state = 'armcheckend'
            else:
                network.send_state = 'standby'
                
        else:
            network.send_state = 'notfound'
            
class DumbelFront:
    def __init__(self, model, frame):
        self.model = model
        self.frame = frame
        self.comparator = PoseComparator(model, frame)
        
    def check_arm(self):
        print("check arm start")
        if self.frame.pose_landmarks is not None:
            arm_state = self.comparator.return_similarity(
                self.model.pose_landmarks.landmark[11:17],
                self.frame.pose_landmarks.landmark[11:17]
            )
            print("arm state is >>>", arm_state)
            if arm_state > 0.5:
                network.send_state = 'armcheckend'
            else:
                network.send_state = 'standby'
                
        else:
            network.send_state = 'notfound'
       
       
class Run:
    def __init__(self, model, frame, frameimg):
        self.model = model
        self.frame = frame
        self.frameimg = frameimg
        self.comparator = PoseComparator(model, frame)
    
    ############# 운동 중 축 확인 #############
    
    def tilt_check(self): # 운동 중 확인
        global total_tilt
        
        state = None
        
        if self.frame.pose_landmarks is None or self.model.pose_landmarks is None:
            print("Error: Pose landmarks not detected.")
            return "e"

        frame_landmarks = self.frame.pose_landmarks.landmark
        model_landmarks = self.model.pose_landmarks.landmark

        frame_tilt = self.comparator.calculate_tilt(frame_landmarks)
        model_tilt = self.comparator.calculate_tilt(model_landmarks)

        tilt_difference = abs(frame_tilt - model_tilt)

        if tilt_difference < 0.1:  # Adjust threshold as needed for sensitivity
            state = "n"
        elif frame_tilt > model_tilt:
            state = "r"
        else:
            state = "l"
            
        total_tilt.append(state)
        return state
            
            
    def accuracy_check(self):
        global total_accuracy
        global accuracy_max
        
        if self.frame.pose_landmarks is None or self.model.pose_landmarks is None:
            print("Error: Pose landmarks not detected.")
            return "e"  # Default or error state

        frame_landmarks = self.frame.pose_landmarks.landmark
        model_landmarks = self.model.pose_landmarks.landmark

        accuracy = self.comparator.return_similarity(
            model_landmarks[11:33],
            frame_landmarks[11:33]
        )
        accuracy = accuracy * 100
        accuracy = 70 + (accuracy - 50) / 2 # scaling
        accuracy = int(accuracy)
        total_accuracy.append(accuracy)
        
        if accuracy > accuracy_max:
            accuracy_max = accuracy
            cv.imwrite('/home/pi/HELPT/topaccuracy.jpg', self.frameimg)
            
        return str(accuracy)

    def combined_check(self):
        tilt_state = self.tilt_check()
        accuracy_state = self.accuracy_check()
        if tilt_state == 'e' or accuracy_state == 'e':
            return "notfound"
        return tilt_state + accuracy_state
    
    def make_report(self):
        average_accuracy = sum(total_accuracy) / len(total_accuracy)
        average_accuracy = int(average_accuracy)
        counter = Counter(total_tilt)
        # 가장 카운트가 많은 값을 찾음
        most_common_value, most_common_count = counter.most_common(1)[0]
        end_state = most_common_value + str(average_accuracy)
        return end_state

