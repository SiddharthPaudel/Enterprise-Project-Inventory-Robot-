import cv2
import numpy as np
import serial
import time

# Initialize serial communication with Arduino
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)  # Replace 'COM5' with your Arduino port
time.sleep(2)  # Give some time for the serial connection to initialize

speed = 5  # Initial speed value
stopped = False  # Flag to indicate if the robot should remain stopped
valid_qr_codes = ["destination_1", "destination_2", "destination_3"]  # List of valid QR codes

def send_command(command, speed):
    if command == "STOP":
        command_str = "MOVE 0 0\n"
    else:
        command_str = f"MOVE {speed} {speed}\n"  # Adjusted to send speed in both directions
    arduino.write(command_str.encode())
    print(f"Sent command: {command_str.strip()}")

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_the_lines(img, lines):
    img = np.copy(img)
    blank_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
 
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(blank_image, (x1, y1), (x2, y2), (0, 255, 0), thickness=10)

    img = cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)
    return img

def process(image):
    if image is None:
        return None, None

    height, width = image.shape[:2]
    region_of_interest_vertices = [
        (0, height),
        (width // 2, height // 2),
        (width, height)
    ]
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    canny_image = cv2.Canny(gray_image, 100, 120)
    cropped_image = region_of_interest(canny_image, np.array([region_of_interest_vertices], np.int32))
    
    lines = cv2.HoughLinesP(cropped_image,
                            rho=2,
                            theta=np.pi/180,
                            threshold=50,
                            lines=np.array([]),
                            minLineLength=40,
                            maxLineGap=100)
    
    image_with_lines = draw_the_lines(image, lines)
    return image_with_lines, lines

def determine_movement(lines):
    if lines is None:
        return "STOP"
    
    left_count = 0
    right_count = 0
    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = (y2 - y1) / (x2 - x1)
            if slope < 0:
                left_count += 1
            else:
                right_count += 1
    
    if left_count > right_count:
        return "MOVE_LEFT"
    elif right_count > left_count:
        return "MOVE_RIGHT"
    else:
        return "MOVE_FORWARD"

def decode_qr(image):
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    if bbox is not None:
        print(f"QR Code Data: {data}")
        return data
    return None

cap = cv2.VideoCapture(0)  # Open default camera (usually webcam)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Check for QR codes in the frame
    qr_data = decode_qr(frame)
    if qr_data:
        if qr_data in valid_qr_codes:  # Check if the QR code is valid
            send_command("STOP", 0)
            stopped = True
            print(f"Valid QR Code detected ({qr_data}), robot stopped")
        else:
            print(f"Ignored QR Code: {qr_data}")
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        continue

    if stopped:
        # If the robot is stopped, do not process the frame or send movement commands
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        continue

    frame, lines = process(frame)
    if frame is None:
        break

    command = determine_movement(lines)
    print(f"Detected command: {command}")
    send_command(command, speed)
    
    cv2.imshow('frame', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Stop the program
        send_command("STOP", 0)
        break
    elif key == ord('w'):  # Increase speed
        speed = min(speed + 1, 10)
        print(f"Speed increased to: {speed}")
    elif key == ord('s'):  # Decrease speed
        speed = max(speed - 1, 0)
        print(f"Speed decreased to: {speed}")
    elif key == ord('p'):  # Pause movement
        send_command("STOP", 0)
        stopped = True
        print("Movement paused")

cap.release()
cv2.destroyAllWindows()
arduino.close()