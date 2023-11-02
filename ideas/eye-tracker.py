import cv2
import mediapipe as mp

cam = cv2.VideoCapture(9)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

while True:
    _, frame = cam.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    # print(landmark_points)

    frame_height, frame_width, _ = frame.shape

    if landmark_points:
        for landmark in landmark_points[0].landmark[474:478]:
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            cv2.circle(frame, (x, y),  2, (0, 255, 0))
            # print(x, y)

    cv2.imshow("Test", frame)
    cv2.waitKey(1)
