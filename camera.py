import cv2

def list_available_cameras(max_cameras=10):
    available_cameras = []
    for camera_index in range(max_cameras):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            available_cameras.append(camera_index)
            cap.release()
    return available_cameras

available_cameras = list_available_cameras()

if available_cameras:
    print("Available cameras:")
    for camera_index in available_cameras:
        print(f"Camera index {camera_index} is available.")
else:
    print("No cameras are available.")

# You can also open a camera and display a frame to verify:
if available_cameras:
    cap = cv2.VideoCapture(available_cameras[0])
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera Frame', frame)
            print(f"Showing frame from camera index {available_cameras[0]}")
            cv2.waitKey(0)
        cap.release()
    cv2.destroyAllWindows()
