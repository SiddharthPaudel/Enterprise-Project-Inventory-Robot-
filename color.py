import cv2
import numpy as np
import serial
import time

# Initialize serial communication with Arduino
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)
time.sleep(2)

speed = 5
stopped = False

# Define colors and their corresponding destination names
color_destinations = {
    (255, 0, 0): "Shelf_A",   # Example: Red color for Shelf_A
    # (255, 0, 0): "Shelf_B",   # Example: Blue color for Shelf_B
    # Add more colors and their destinations as needed
}

def send_command(command, speed):
    command_str = f"MOVE {0 if command == 'STOP' else speed} {0 if command == 'STOP' else speed}\n"
    arduino.write(command_str.encode())
    print(f"Sent command: {command_str.strip()}")

def process_image(frame):
    if frame is None:
        return None

    # Convert BGR to HSV (Hue, Saturation, Value)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for each color destination
    for color in color_destinations:
        lower_color = np.array([color[0] - 10, 100, 100])
        upper_color = np.array([color[0] + 10, 255, 255])

        # Create a mask for the specified color range
        mask = cv2.inRange(hsv_frame, lower_color, upper_color)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Adjust area threshold as needed
                cv2.drawContours(frame, [contour], -1, color, 2)

                # Determine the destination based on the detected color
                detected_destination = color_destinations[color]
                print(f"Detected destination: {detected_destination}")

                # Stop the robot and send the command
                send_command("STOP", 0)
                return frame, detected_destination

    return frame, None

camera_id = 0
delay = 1
window_name = 'Color-Based Destination Detection'

cap = cv2.VideoCapture(camera_id)
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

    processed_frame, destination = process_image(frame)
    if destination is not None:
        stopped = True  # Stop further processing until resumed

    cv2.imshow(window_name, processed_frame)
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
