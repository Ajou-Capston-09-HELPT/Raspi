import cv2
import mediapipe as mp

# MediaPipe 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 카메라 캡처 초기화
cap = cv2.VideoCapture(0)  # 카메라 인덱스를 적절히 설정

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("카메라로부터 프레임을 읽을 수 없습니다.")
        break
    
    frame = cv2.flip(frame, 0)
    
    # BGR에서 RGB로 변환
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Pose 검출
    results = pose.process(frame_rgb)
    
    # Landmark 검출 결과 확인
    if results.pose_landmarks:
        print("포즈 랜드마크가 검출되었습니다.")
        # 랜드마크 그리기
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    else:
        print("포즈 랜드마크를 검출하지 못했습니다.")
    
    # 결과 영상 표시
    cv2.imshow('Blazepose', frame)
    
    if cv2.waitKey(5) & 0xFF == 27:  # ESC 키로 종료
        break

cap.release()
cv2.destroyAllWindows()
