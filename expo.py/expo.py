# import cv2
# import numpy as np
# import serial
# import time
# import threading
# import qrcode

# # Initialize serial communication with Arduino
# arduino = serial.Serial(port='COM5', baudrate=115200, timeout=5)  # Increase timeout
# time.sleep(2)  # Give some time for the serial connection to initialize

# speed = 0  # Initial speed value
# stopped = False  # Flag to indicate if the robot should remain stopped
# initial_qr_reached = False  # Flag to indicate if the initial QR is detected

# # Global variables to store state
# qr_detected = False
# destination_detected = None
# movement_command = "MOVE_FORWARD"  # Initial movement command

# # Placeholder dictionary to store destination QR file paths
# fixed_destination_qr_data = {
#     "Destination_1": "destination1.png",
#     "Destination_2": "destination2.png"
# }

# initial_qr_data = "INITIAL_POINT"
# initial_qr_filename = "initial_point.png"

# def send_command(command, speed):
#     if command == "STOP":
#         command_str = "MOVE 0 0\n"
#     elif command == "REVERSE":
#         command_str = f"MOVE {-speed} {-speed}\n"  # Adjusted reverse command
#     else:
#         command_str = f"MOVE {speed} {speed}\n"  # Adjusted to send speed in both directions
#     try:
#         arduino.write(command_str.encode())
#         print(f"Sent command: {command_str.strip()}")
#         time.sleep(0.05)  # Small delay to ensure the command is processed
#     except serial.SerialTimeoutException as e:
#         print(f"Failed to send command: {command_str.strip()} with error: Write timeout")
#     except Exception as e:
#         print(f"Failed to send command: {command_str.strip()} with error: {e}")

# def region_of_interest(img, vertices):
#     mask = np.zeros_like(img)
#     match_mask_color = 255
#     cv2.fillPoly(mask, vertices, match_mask_color)
#     masked_image = cv2.bitwise_and(img, mask)
#     return masked_image

# def draw_the_lines(img, lines):
#     img = np.copy(img)
#     blank_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
 
#     if lines is not None:
#         for line in lines:
#             for x1, y1, x2, y2 in line:
#                 cv2.line(blank_image, (x1, y1), (x2, y2), (0, 255, 0), thickness=10)

#     img = cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)
#     return img

# def process(image):
#     if image is None:
#         return None, None
#     height, width = image.shape[:2]
#     region_of_interest_vertices = [
#         (0, height),
#         (width // 2, height // 2),
#         (width, height)
#     ]
    
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     canny_image = cv2.Canny(gray_image, 100, 120)
#     cropped_image = region_of_interest(canny_image, np.array([region_of_interest_vertices], np.int32))
    
#     lines = cv2.HoughLinesP(cropped_image,
#                             rho=2,
#                             theta=np.pi/180,
#                             threshold=50,
#                             lines=np.array([]),
#                             minLineLength=40,
#                             maxLineGap=100)
    
#     image_with_lines = draw_the_lines(image, lines)
#     return image_with_lines, lines

# def determine_movement(lines):
#     global speed
#     if lines is None:
#         return "STOP"
    
#     left_count = 0
#     right_count = 0
#     for line in lines:
#         for x1, y1, x2, y2 in line:
#             if x2 - x1 == 0:  # Prevent division by zero
#                 continue
#             slope = (y2 - y1) / (x2 - x1)
#             if slope < 0:
#                 left_count += 1
#             else:
#                 right_count += 1
    
#     if left_count > right_count:
#         movement = "MOVE_LEFT"
#     elif right_count > left_count:
#         movement = "MOVE_RIGHT"
#     else:
#         movement = "MOVE_FORWARD"

#     # Set speed to 4 if any lines are detected
#     if left_count > 0 or right_count > 0:
#         speed = 4

#     return movement

# def extract_destination_from_qr(data):
#     try:
#         print(f"Extracting destination from QR data: {data}")
#         segments = data.split('|')
#         for segment in segments:
#             if segment.lower().startswith('destination_'):
#                 return segment.strip()
#     except Exception as e:
#         print(f"Error extracting destination: {e}")
#     return None

# def generate_qr(data, filename):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
    
#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(filename)
#     print(f"QR code saved as {filename}")

# def generate_object_qr():
#     name = input("Enter object name: ")
#     quantity = input("Enter object quantity: ")
#     destination = input("Enter object destination: ")
#     data = f"name:{name}|quantity:{quantity}|destination:{destination}"
#     filename = f"{name}.png"
#     generate_qr(data, filename) 
#     print(f"QR code generated for {name} and saved as {filename}")

# def generate_fixed_destination_qr():
#     destination = input("Enter fixed destination name: ")
#     data = destination
#     filename = f"{destination}.png"
#     generate_qr(data, filename)
#     print(f"Fixed QR code generated for {destination} and saved as {filename}")

# def generate_initial_qr():
#     generate_qr(initial_qr_data, initial_qr_filename)
#     print(f"Initial QR code generated and saved as {initial_qr_filename}")

# def camera_thread():
#     global stopped, speed, qr_detected, destination_detected, movement_command, initial_qr_reached
#     camera_id = 0
#     delay = 1
#     window_name = 'OpenCV QR Code and Line Detection'

#     qcd = cv2.QRCodeDetector()
#     cap = cv2.VideoCapture(camera_id)

#     # Reduce frame size to decrease processing load
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size to minimize delay

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to capture image")
#             break
        
#         if stopped:
#             cv2.imshow(window_name, frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#             continue

#         frame, lines = process(frame)
#         if frame is None:
#             print("Failed to process image")
#             break

#         ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
#         qr_detected = False
#         destination_detected = None
#         if ret_qr:
#             for s, p in zip(decoded_info, points):
#                 s = s.strip()  # Strip any extraneous characters
#                 print(f"Decoded QR data: {s}")  # Debug print statement
#                 destination = extract_destination_from_qr(s)
#                 if destination in fixed_destination_qr_data:
#                     print(f"Detected destination: {destination}")
#                     qr_detected = True
#                     destination_detected = destination
#                     stopped = True  # Stop the robot
#                     movement_command = "STOP"
#                     # Highlight QR code with green box
#                     points = points[0].astype(int).reshape((-1, 2))
#                     for j in range(len(points)):
#                         pt1 = tuple(points[j])
#                         pt2 = tuple(points[(j + 1) % len(points)])
#                         cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
#                     print("You have reached your destination")

#                     # Stop the robot before reversing
#                     send_command("STOP", 0)

#                     # Pause for 10 seconds
#                     print("Paused for 10 seconds")
#                     time.sleep(20)  # Delay for 10 seconds

#                     # Start reversing the robot
#                     print("Reversing the robot")
#                     send_command("REVERSE", 4)

#                     while not initial_qr_reached:
#                         ret, frame = cap.read()
#                         if not ret:
#                             print("Failed to capture image while reversing")
#                             break
#                         ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
#                         if ret_qr:
#                             for s, p in zip(decoded_info, points):
#                                 s = s.strip()
#                                 if s == initial_qr_data:
#                                     print("Detected initial QR code while reversing, stopping the robot permanently")
#                                     initial_qr_reached = True
#                                     send_command("STOP", 0)
#                                     stopped = True
#                                     # Highlight initial QR code with red box
#                                     points = points[0].astype(int).reshape((-1, 2))
#                                     for j in range(len(points)):
#                                         pt1 = tuple(points[j])
#                                         pt2 = tuple(points[(j + 1) % len(points)])
#                                         cv2.line(frame, pt1, pt2, (0, 0, 255), 3)
#                                     break
#                     break

#                 elif s == initial_qr_data:
#                     print("Detected initial QR code, stopping the robot permanently")
#                     qr_detected = True
#                     initial_qr_reached = True
#                     stopped = True
#                     movement_command = "STOP"
#                     send_command("STOP", 0)
#                     # Highlight initial QR code with red box
#                     points = points[0].astype(int).reshape((-1, 2))
#                     for j in range(len(points)):
#                         pt1 = tuple(points[j])
#                         pt2 = tuple(points[(j + 1) % len(points)])
#                         cv2.line(frame, pt1, pt2, (0, 0, 255), 3)
#                     print("Robot stopped at initial point permanently")
#                 else:
#                     # Highlight QR code text in green
#                     print(f"Ignored QR code: {s}")
#                     cv2.putText(frame, s, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

#         if not qr_detected and not initial_qr_reached:
#             movement_command = determine_movement(lines)
        
#         cv2.imshow(window_name, frame)
#         key = cv2.waitKey(delay) & 0xFF
#         if key == ord('q'):
#             stopped = True
#             movement_command = "STOP"
#             break
#         elif key == ord('w'):
#             speed = min(speed + 1, 10)
#             print(f"Speed increased to: {speed}")
#         elif key == ord('s'):
#             speed = max(speed - 1, 0)
#             print(f"Speed decreased to: {speed}")
#         elif key == ord('p'):
#             stopped = True
#             movement_command = "STOP"
#             print("Movement paused")

#     cap.release()
#     cv2.destroyAllWindows()

# def arduino_thread():
#     global stopped, movement_command
#     while True:
#         if stopped:
#             send_command("STOP", 0)
#         else:
#             send_command(movement_command, speed)
#         time.sleep(0.01)  # Adjust delay as needed

# # Generate QR codes for objects based on user input
# num_objects = int(input("Enter the number of objects to generate QR codes for: "))
# for _ in range(num_objects):
#     generate_object_qr()

# # Generate fixed destination QR codes based on user input
# num_destinations = int(input("Enter the number of fixed destinations to generate QR codes for: "))
# for _ in range(num_destinations):
#     generate_fixed_destination_qr()

# # Generate initial QR code
# generate_initial_qr()

# # Start threads
# camera_thread_obj = threading.Thread(target=camera_thread)
# arduino_thread_obj = threading.Thread(target=arduino_thread)

# camera_thread_obj.start()
# arduino_thread_obj.start()

# # Join threads (wait for them to finish if needed)
# camera_thread_obj.join()
# arduino_thread_obj.join()

# # Close serial connection
# arduino.close()



import cv2
import numpy as np
import serial
import time
import threading
import qrcode

# Initialize serial communication with Arduino
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=5)  # Increase timeout
time.sleep(2)  # Give some time for the serial connection to initialize

speed = 0  # Initial speed value
stopped = False  # Flag to indicate if the robot should remain stopped
initial_qr_reached = False  # Flag to indicate if the initial QR is detected

# Global variables to store state
qr_detected = False
destination_detected = None
movement_command = "MOVE_FORWARD"  # Initial movement command

# Placeholder dictionary to store destination QR file paths
fixed_destination_qr_data = {
    "Destination_1": "destination1.png",
    "Destination_2": "destination2.png"
}

initial_qr_data = "INITIAL_POINT"
initial_qr_filename = "initial_point.png"

def send_command(command, speed):
    if command == "STOP":
        command_str = "MOVE 0 0\n"
    elif command == "REVERSE":
        command_str = f"MOVE {-speed} {-speed}\n"  # Adjusted reverse command
    else:
        command_str = f"MOVE {speed} {speed}\n"  # Adjusted to send speed in both directions
    try:
        arduino.write(command_str.encode())
        print(f"Sent command: {command_str.strip()}")
        time.sleep(0.05)  # Small delay to ensure the command is processed
    except serial.SerialTimeoutException as e:
        print(f"Failed to send command: {command_str.strip()} with error: Write timeout")
    except Exception as e:
        print(f"Failed to send command: {command_str.strip()} with error: {e}")

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
    global speed
    if lines is None:
        return "STOP"
    
    left_count = 0
    right_count = 0
    for line in lines:

        
        for x1, y1, x2, y2 in line:
            if x2 - x1 == 0:  # Prevent division by zero
                continue
            slope = (y2 - y1) / (x2 - x1)
            if slope < 0:
                left_count += 1
            else:
                right_count += 1
    
    if left_count > right_count:
        movement = "MOVE_LEFT"
    elif right_count > left_count:
        movement = "MOVE_RIGHT"
    else:
        movement = "MOVE_FORWARD"

    # Set speed to 4 if any lines are detected
    if left_count > 0 or right_count > 0:
        speed = 4

    return movement

def extract_destination_from_qr(data):
    try:
        print(f"Extracting destination from QR data: {data}")
        segments = data.split('|')
        for segment in segments:
            if segment.lower().startswith('destination_'):
                return segment.strip()
    except Exception as e:
        print(f"Error extracting destination: {e}")
    return None

def generate_qr(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"QR code saved as {filename}")

def generate_object_qr():
    name = input("Enter object name: ")
    quantity = input("Enter object quantity: ")
    destination = input("Enter object destination: ")
    data = f"name:{name}|quantity:{quantity}|destination:{destination}"
    filename = f"{name}.png"
    generate_qr(data, filename) 
    print(f"QR code generated for {name} and saved as {filename}")

def generate_fixed_destination_qr():
    destination = input("Enter fixed destination name: ")
    data = destination
    filename = f"{destination}.png"
    generate_qr(data, filename)
    print(f"Fixed QR code generated for {destination} and saved as {filename}")

def generate_initial_qr():
    generate_qr(initial_qr_data, initial_qr_filename)
    print(f"Initial QR code generated and saved as {initial_qr_filename}")

def camera_thread():
    global stopped, speed, qr_detected, destination_detected, movement_command, initial_qr_reached
    camera_id = 0
    delay = 1
    window_name = 'OpenCV QR Code and Line Detection'

    qcd = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(camera_id)

    # Reduce frame size to decrease processing load
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size to minimize delay

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

        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
        qr_detected = False
        destination_detected = None
        if ret_qr:
            for s, p in zip(decoded_info, points):
                s = s.strip()  # Strip any extraneous characters
                print(f"Decoded QR data: {s}")  # Debug print statement
                destination = extract_destination_from_qr(s)
                if destination in fixed_destination_qr_data:
                    print(f"Detected destination: {destination}")
                    qr_detected = True
                    destination_detected = destination
                    stopped = True  # Stop the robot
                    movement_command = "STOP"
                    # Highlight QR code with green box
                    points = points[0].astype(int).reshape((-1, 2))
                    for j in range(len(points)):
                        pt1 = tuple(points[j])
                        pt2 = tuple(points[(j + 1) % len(points)])
                        cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
                    print(f"You have reached your destination: {destination}")

                    # Stop the robot before reversing
                    send_command("STOP", 0)

                    # Pause for 10 seconds
                    print("Paused for 10 seconds")
                    time.sleep(20)  # Delay for 10 seconds

                    # Start reversing the robot
                    print("Reversing the robot")
                    send_command("REVERSE", 4)

                    while not initial_qr_reached:
                        ret, frame = cap.read()
                        if not ret:
                            print("Failed to capture image while reversing")
                            break
                        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
                        if ret_qr:
                            for s, p in zip(decoded_info, points):
                                s = s.strip()
                                if s == initial_qr_data:
                                    print("Detected initial QR code while reversing, stopping the robot permanently")
                                    initial_qr_reached = True
                                    send_command("STOP", 0)
                                    stopped = True
                                    # Highlight initial QR code with red box
                                    points = points[0].astype(int).reshape((-1, 2))
                                    for j in range(len(points)):
                                        pt1 = tuple(points[j])
                                        pt2 = tuple(points[(j + 1) % len(points)])
                                        cv2.line(frame, pt1, pt2, (0, 0, 255), 3)
                                    break
                    break

                elif s == initial_qr_data:
                    print("Detected initial QR code, stopping the robot permanently")
                    qr_detected = True
                    initial_qr_reached = True
                    stopped = True
                    movement_command = "STOP"
                    send_command("STOP", 0)
                    # Highlight initial QR code with red box
                    points = points[0].astype(int).reshape((-1, 2))
                    for j in range(len(points)):
                        pt1 = tuple(points[j])
                        pt2 = tuple(points[(j + 1) % len(points)])
                        cv2.line(frame, pt1, pt2, (0, 0, 255), 3)
                    print("Robot stopped at initial point permanently")
                else:
                    # Highlight QR code text in green
                    print(f"Ignored QR code: {s}")
                    cv2.putText(frame, s, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        if not qr_detected and not initial_qr_reached:
            movement_command = determine_movement(lines)
        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(delay) & 0xFF
        if key == ord('q'):
            stopped = True
            movement_command = "STOP"
            break
        elif key == ord('w'):
            speed = min(speed + 1, 10)
            print(f"Speed increased to: {speed}")
        elif key == ord('s'):
            speed = max(speed - 1, 0)
            print(f"Speed decreased to: {speed}")
        elif key == ord('p'):
            stopped = True
            movement_command = "STOP"
            print("Movement paused")
        elif key == ord('r'):
            print("Reversing the robot")
            send_command("REVERSE", 4)

    cap.release()
    cv2.destroyAllWindows()

def arduino_thread():
    global stopped, movement_command
    while True:
        if stopped:
            send_command("STOP", 0)
        else:
            send_command(movement_command, speed)
        time.sleep(0.01)  # Adjust delay as needed

# Generate QR codes for objects based on user input
num_objects = int(input("Enter the number of objects to generate QR codes for: "))
for _ in range(num_objects):
    generate_object_qr()

# Generate fixed destination QR codes based on user input
num_destinations = int(input("Enter the number of fixed destinations to generate QR codes for: "))
for _ in range(num_destinations):
    generate_fixed_destination_qr()

# Generate initial QR code
generate_initial_qr()

# Start threads
camera_thread_obj = threading.Thread(target=camera_thread)
arduino_thread_obj = threading.Thread(target=arduino_thread)

camera_thread_obj.start()
arduino_thread_obj.start()

# Join threads (wait for them to finish if needed)
camera_thread_obj.join()
arduino_thread_obj.join()

# Close serial connection
arduino.close()
