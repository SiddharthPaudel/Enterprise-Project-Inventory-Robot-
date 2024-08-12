import cv2
import numpy as np
import serial
import time
import torch
from pyzbar.pyzbar import decode

# Initialize serial communication with Arduino
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)  # Replace 'COM5' with your Arduino port
time.sleep(2)  # Give some time for the serial connection to initialize

speed = 0  # Initial speed value
stopped = False  # Flag to indicate if the robot should remain stopped
shelf_qr_data = "Shelf_A"  # Data content of the shelf QR code
movements = []  # List to store movements

def send_command(command, speed):
    command_str = f"MOVE {0 if command == 'STOP' else speed} {0 if command == 'STOP' else speed}\n"
    arduino.write(command_str.encode())
    print(f"Sent command: {command_str.strip()}")
    if command != 'STOP':
        movements.append((command, speed))

def reverse_movements():
    print("Reversing movements")
    for command, speed in reversed(movements):
        if command == 'MOVE_FORWARD':
            reverse_command = 'MOVE_BACKWARD'
        elif command == 'MOVE_BACKWARD':
            reverse_command = 'MOVE_FORWARD'
        else:
            reverse_command = command  # For simplicity, assuming no other commands need reversing
        send_command(reverse_command, speed)
        time.sleep(1)  # Adjust this delay as necessary

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    return cv2.bitwise_and(img, mask)

def draw_the_lines(img, lines):
    blank_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(blank_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
    return cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)

def process(image):
    if image is None:
        return None, None

    height, width = image.shape[:2]
    roi_vertices = [(0, height), (width // 2, height // 2), (width, height)]
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    canny_image = cv2.Canny(gray_image, 100, 120)
    cropped_image = region_of_interest(canny_image, np.array([roi_vertices], np.int32))
    
    lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 50, minLineLength=40, maxLineGap=100)
    return draw_the_lines(image, lines), lines

def determine_movement(lines):
    return "MOVE_FORWARD" if lines is not None else "STOP"

def extract_destination_from_qr(data):
    try:
        segments = data.split('|')
        for segment in segments:
            if segment.startswith('Destination:'):
                return segment.split(':')[1].strip()
    except:
        return None
    return None

def is_valid_qr_code(x1, y1, x2, y2, frame_shape):
    # Calculate aspect ratio
    aspect_ratio = (x2 - x1) / (y2 - y1)
    # Define minimum and maximum expected sizes in pixels
    min_size = 50
    max_size = min(frame_shape) // 2
    # Adjust these thresholds based on your specific use case
    return aspect_ratio > 0.5 and aspect_ratio < 2.0 and (x2 - x1) > min_size and (y2 - y1) > min_size and (x2 - x1) < max_size and (y2 - y1) < max_size

camera_id = 0
delay = 1
window_name = 'OpenCV QR Code and Line Detection'

# Load YOLO model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

cap = cv2.VideoCapture(camera_id)

# Reduce frame size to decrease processing load
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break
    
    if stopped:
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    frame, lines = process(frame)
    if frame is None:
        print("Failed to process image")
        break

    # Use YOLO for QR code detection
    results = model(frame)
    labels, cords = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]

    qr_detected = False
    for label, cord in zip(labels, cords):
        if int(label) == 0:  # Assuming class 0 is QR code
            x1, y1, x2, y2, conf = cord
            if conf > 0.5 and is_valid_qr_code(x1, y1, x2, y2, frame.shape):  # Adjust confidence threshold and additional validation
                x1, y1, x2, y2 = int(x1 * frame.shape[1]), int(y1 * frame.shape[0]), int(x2 * frame.shape[1]), int(y2 * frame.shape[0])
                qr_data = decode(frame[y1:y2, x1:x2])
                if qr_data:
                    qr_data = qr_data[0].data.decode('utf-8')
                    destination = extract_destination_from_qr(qr_data)
                    if destination == shelf_qr_data:
                        print("Shelf QR code detected")
                        color = (0, 255, 0)  # Green for valid QR
                        qr_detected = True
                        stopped = True  # Stop the robot
                        send_command("STOP", 0)  # Immediately send stop command
                        reverse_movements()  # Reverse to the original position
                    else:
                        print("Ignored QR code detected")
                        color = (0, 0, 255)  # Red for invalid QR
                        cv2.putText(frame, "Not Shelf QR!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    if not qr_detected:
        command = determine_movement(lines)
        print(f"Detected command: {command}")
        send_command(command, speed)

    cv2.imshow(window_name, frame)
    key = cv2.waitKey(delay) & 0xFF
    if key == ord('q'):
        send_command("STOP", 0)
        break
    elif key == ord('w'):
        speed = min(speed + 1, 10)
        print(f"Speed increased to: {speed}")
    elif key == ord('s'):
        speed = max(speed - 1, 0)
        print(f"Speed decreased to: {speed}")
    elif key == ord('p'):
        send_command("STOP", 0)
        stopped = True
        print("Movement paused")

cap.release()
cv2.destroyAllWindows()
arduino.close()




