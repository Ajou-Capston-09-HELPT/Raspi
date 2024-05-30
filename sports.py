import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

class PoseComparator:
    def __init__(self, model, frame):
        self.model = model
        self.frame = frame
        self.state = None

    def calculate_angle(self, point1, point2, point3):
        """
        세 점의 좌표를 입력받아 각도를 계산합니다.
        """
        p1 = np.array([point1.x, point1.y, point1.z])
        p2 = np.array([point2.x, point2.y, point2.z])
        p3 = np.array([point3.x, point3.y, point3.z])
        
        vector1 = p1 - p2
        vector2 = p3 - p2
        
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)
        cos_angle = dot_product / (norm1 * norm2)
        
        angle = np.arccos(cos_angle)
        angle_degrees = np.degrees(angle)
        
        return angle_degrees

    def return_similarity(self, model_landmarks, frame_landmarks):
        """
        랜드마크 리스트를 입력받아 유사도를 계산합니다.
        """
        # 여기서는 간단한 예로 랜드마크 간의 유클리드 거리의 평균을 유사도로 사용합니다.
        distances = [np.linalg.norm(np.array([m.x, m.y, m.z]) - np.array([f.x, f.y, f.z]))
                     for m, f in zip(model_landmarks, frame_landmarks)]
        similarity = 1 / (1 + np.mean(distances))

        return similarity # 0.0~1.0, 높을수록 좋음
 
    def return_body_similarity(self, model_landmarks, frame_landmarks):
        angle = []
        for landmarks in [model_landmarks, frame_landmarks]:
            left_angle = self.calculate_angle(landmarks[11],
                                              landmarks[23],
                                              landmarks[25])
            right_angle = self.calculate_angle(landmarks[12],
                                               landmarks[24],
                                               landmarks[26])
            angle.append((left_angle + right_angle) / 2)
        
        angle_diff = abs(angle[0] - angle[1])
        similarity = 1 / (1 + angle_diff)
        
        return similarity

    def get_center(self, landmarks, index1, index2):
        x1, y1 = landmarks[index1].x, landmarks[index1].y
        x2, y2 = landmarks[index2].x, landmarks[index2].y
        return np.array([(x1 + x2) / 2, (y1 + y2) / 2])
    
    def calculate_tilt(self, frame_landmarks):
        left_shoulder = self.get_center(frame_landmarks, 11, 12)
        right_shoulder = self.get_center(frame_landmarks, 23, 24)
        shoulder_center = (left_shoulder + right_shoulder) / 2
        
        left_hip = self.get_center(frame_landmarks, 23, 24)
        right_hip = self.get_center(frame_landmarks, 25, 26)
        hip_center = (left_hip + right_hip) / 2
        
        vector = shoulder_center - hip_center
        angle = np.arctan2(vector[1], vector[0])  # y, x

        return angle