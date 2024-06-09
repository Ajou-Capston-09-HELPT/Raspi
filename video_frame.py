import cv2
import os

def save_frames(video_path, output_folder, num_frames):
    # 비디오 파일 로드
    cap = cv2.VideoCapture(video_path)
    
    # 비디오의 총 프레임 수와 FPS 가져오기
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # 저장할 프레임 간격 계산
    interval = total_frames // num_frames
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    frame_ids = [i * interval for i in range(num_frames)]
    
    for idx, frame_id in enumerate(frame_ids):
        # 비디오의 특정 프레임으로 이동
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        
        if ret:
            # 프레임 저장
            frame_filename = os.path.join(output_folder, f"frame_{idx+1}.jpg")
            cv2.imwrite(frame_filename, frame)
        else:
            print(f"Failed to capture frame at position {frame_id}")
    
    cap.release()
    print(f"{num_frames} frames have been saved in {output_folder}")

# 사용 예시
video_path = '/home/pi/HELPT/sample_shot/dumbelfront.mp4'
output_folder = '/home/pi/HELPT/sample_shot/dumbelfront'
num_frames = 6

save_frames(video_path, output_folder, num_frames)
