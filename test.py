import cv2

# 파이카메라 객체 생성
cap = cv2.VideoCapture(0)

# 카메라가 올바르게 열렸는지 확인
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 카메라 프레임을 읽어와서 화면에 표시
while True:
    ret, frame = cap.read()  # 프레임 읽기

    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break
    
    frame = cv2.flip(frame, 0)
    cv2.imshow('Camera', frame)  # 프레임 화면에 표시

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 작업이 끝나면 객체와 창 닫기
cap.release()
cv2.destroyAllWindows()
