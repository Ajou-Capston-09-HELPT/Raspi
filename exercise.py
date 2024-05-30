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

class Bandvent:
    def __init__(self, model, frame):
        self.model = model
        self.frame = frame
        self.comparator = PoseComparator(model, frame)

    ############# 운동 전 자세 확인 #############
    
    def check_foot(self):
        # print("model pose pose landmarks", self.model.pose_landmarks) 
        if self.frame.pose_landmarks is not None:
            foot_state = self.comparator.return_similarity(
                self.model.pose_landmarks.landmark[23:33],
                self.frame.pose_landmarks.landmark[23:33]
            )
            print("foot state is", foot_state)
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
            print("body state is", body_angle_state)
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
            print("hand state is", hand_state)
            if hand_state > 0.7:
                network.send_state = 'handcheckend'
                time.sleep(0.5)
            else:
                network.send_state = 'standby'
        else:
            network.send_state = 'notfound'

            
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
        accuracy = int(accuracy)
        total_accuracy.append(accuracy)
        return str(accuracy)

    def make_report():
        average_accuracy = sum(total_accuracy) / len(total_accuracy)
        counter = Counter(average_tilt)
        # 가장 카운트가 많은 값을 찾음
        most_common_value, most_common_count = counter.most_common(1)[0]
        
        return
