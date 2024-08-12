# import cv2
# import numpy as np
# import serial
# import time

# # Initialize serial communication with Arduino
# arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)  # Replace 'COM5' with your Arduino port
# time.sleep(2)  # Give some time for the serial connection to initialize

# speed = 5  # Initial speed value
# stopped = False  # Flag to indicate if the robot should remain stopped
# shelf_qr_data = "Shelf_A"  # Data content of the shelf QR code

# def send_command(command, speed):
#     command_str = f"MOVE {0 if command == 'STOP' else speed} {0 if command == 'STOP' else speed}\n"
#     arduino.write(command_str.encode())
#     print(f"Sent command: {command_str.strip()}")

# def region_of_interest(img, vertices):
#     mask = np.zeros_like(img)
#     cv2.fillPoly(mask, vertices, 255)
#     return cv2.bitwise_and(img, mask)

# def draw_the_lines(img, lines):
#     blank_image = np.zeros_like(img)
#     if lines is not None:
#         for line in lines:
#             for x1, y1, x2, y2 in line:
#                 cv2.line(blank_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
#     return cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)

# def process(image):
#     if image is None:
#         return None, None

#     height, width = image.shape[:2]
#     roi_vertices = [(0, height), (width // 2, height // 2), (width, height)]
    
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     canny_image = cv2.Canny(gray_image, 100, 120)
#     cropped_image = region_of_interest(canny_image, np.array([roi_vertices], np.int32))
    
#     lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 50, minLineLength=40, maxLineGap=100)
#     return draw_the_lines(image, lines), lines

# def determine_movement(lines):
#     return "MOVE_FORWARD" if lines is not None else "STOP"

# def extract_destination_from_qr(data):
#     try:
#         segments = data.split('|')
#         for segment in segments:
#             if segment.startswith('Destination:'):
#                 return segment.split(':')[1].strip()
#     except:
#         return None
#     return None

# camera_id = 0
# delay = 1
# window_name = 'OpenCV QR Code and Line Detection'

# qcd = cv2.QRCodeDetector()
# cap = cv2.VideoCapture(camera_id)

# # Reduce frame size to decrease processing load
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to capture image")
#         break
    
#     if stopped:
#         cv2.imshow(window_name, frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         continue

#     frame, lines = process(frame)
#     if frame is None:
#         print("Failed to process image")
#         break

#     ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
#     qr_detected = False
#     if ret_qr:
#         for s, p in zip(decoded_info, points):
#             s = s.strip()  # Strip any extraneous characters
#             destination = extract_destination_from_qr(s)
#             if destination == shelf_qr_data:
#                 print("Shelf QR code detected")
#                 color = (0, 255, 0)  # Green for valid QR
#                 qr_detected = True
#                 stopped = True  # Stop the robot
#                 send_command("STOP", 0)  # Immediately send stop command
#             else:
#                 print("Ignored QR code detected")
#                 color = (0, 0, 255)  # Red for invalid QR
#                 cv2.putText(frame, "Not Shelf QR!", (int(p[0][0]), int(p[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
#             frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)

#     if not qr_detected:
#         command = determine_movement(lines)
#         print(f"Detected command: {command}")
#         send_command(command, speed)
    
#     cv2.imshow(window_name, frame)
#     key = cv2.waitKey(delay) & 0xFF
#     if key == ord('q'):
#         send_command("STOP", 0)
#         break
#     elif key == ord('w'):
#         speed = min(speed + 1, 10)
#         print(f"Speed increased to: {speed}")
#     elif key == ord('s'):
#         speed = max(speed - 1, 0)
#         print(f"Speed decreased to: {speed}")
#     elif key == ord('p'):
#         send_command("STOP", 0)
#         stopped = True
#         print("Movement paused")

# cap.release()
# cv2.destroyAllWindows()
# arduino.close()





#obj and obj wala code

# import cv2
# import numpy as np
# import serial
# import time
# import qrcode  # Import QR code library

# # Initialize serial communication with Arduino
# arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)  # Replace 'COM5' with your Arduino port
# time.sleep(2)  # Give some time for the serial connection to initialize

# speed = 5  # Initial speed value
# stopped = False  # Flag to indicate if the robot should remain stopped

# def send_command(command, speed):
#     command_str = f"MOVE {0 if command == 'STOP' else speed} {0 if command == 'STOP' else speed}\n"
#     arduino.write(command_str.encode())
#     print(f"Sent command: {command_str.strip()}")

# def region_of_interest(img, vertices):
#     mask = np.zeros_like(img)
#     cv2.fillPoly(mask, vertices, 255)
#     return cv2.bitwise_and(img, mask)

# def draw_the_lines(img, lines):
#     blank_image = np.zeros_like(img)
#     if lines is not None:
#         for line in lines:
#             for x1, y1, x2, y2 in line:
#                 cv2.line(blank_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
#     return cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)

# def process(image):
#     if image is None:
#         return None, None

#     height, width = image.shape[:2]
#     roi_vertices = [(0, height), (width // 2, height // 2), (width, height)]
    
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     canny_image = cv2.Canny(gray_image, 100, 120)
#     cropped_image = region_of_interest(canny_image, np.array([roi_vertices], np.int32))
    
#     lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 50, minLineLength=40, maxLineGap=100)
#     return draw_the_lines(image, lines), lines

# def determine_movement(lines):
#     return "MOVE_FORWARD" if lines is not None else "STOP"

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

# # Generate QR code for object
# object_id = "object1"
# object_qr_filename = f"{object_id}.png"
# generate_qr(object_id, object_qr_filename)

# # Generate QR code for another object
# another_object_id = "object2"
# another_object_qr_filename = f"{another_object_id}.png"
# generate_qr(another_object_id, another_object_qr_filename)

# camera_id = 0
# delay = 1
# window_name = 'OpenCV QR Code and Line Detection'

# qcd = cv2.QRCodeDetector()
# cap = cv2.VideoCapture(camera_id)

# # Reduce frame size to decrease processing load
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to capture image")
#         break
    
#     if stopped:
#         cv2.imshow(window_name, frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         continue

#     frame, lines = process(frame)
#     if frame is None:
#         print("Failed to process image")
#         break

#     ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
#     qr_detected = False
#     if ret_qr:
#         for s, p in zip(decoded_info, points):
#             s = s.strip()  # Strip any extraneous characters
#             # Compare detected QR code with object QR codes
#             if s == object_id:
#                 print(f"Detected QR code: {s}")
#                 color = (0, 255, 0)  # Green for valid QR
#                 qr_detected = True
#                 stopped = True  # Stop the robot
#                 send_command("STOP", 0)  # Immediately send stop command
#             elif s == another_object_id:
#                 print(f"Detected QR code: {s}")
#                 color = (0, 255, 0)  # Green for valid QR
#                 qr_detected = True
#                 stopped = True  # Stop the robot
#                 send_command("STOP", 0)  # Immediately send stop command
#             else:
#                 print(f"Ignored QR code: {s}")
#                 color = (0, 0, 255)  # Red for invalid QR
#                 cv2.putText(frame, "Unknown QR!", (int(p[0][0]), int(p[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
#             frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)

#     if not qr_detected:
#         command = determine_movement(lines)
#         print(f"Detected command: {command}")
#         send_command(command, speed)
    
#     cv2.imshow(window_name, frame)
#     key = cv2.waitKey(delay) & 0xFF
#     if key == ord('q'):
#         send_command("STOP", 0)
#         break
#     elif key == ord('w'):
#         speed = min(speed + 1, 10)
#         print(f"Speed increased to: {speed}")
#     elif key == ord('s'):
#         speed = max(speed - 1, 0)
#         print(f"Speed decreased to: {speed}")
#     elif key == ord('p'):
#         send_command("STOP", 0)
#         stopped = True
#         print("Movement paused")

# cap.release()
# cv2.destroyAllWindows()
# arduino.close()








# #CORRECT ONE
# import cv2
# import numpy as np
# import serial
# import time
# import threading
# import qrcode

# # Initialize serial communication with Arduino
# arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)  # Replace 'COM5' with your Arduino port
# time.sleep(2)  # Give some time for the serial connection to initialize

# speed = 5  # Initial speed value
# stopped = False  # Flag to indicate if the robot should remain stopped

# # Global variables to store state
# qr_detected = False
# destination_detected = None
# movement_command = "MOVE_FORWARD"  # Initial movement command

# # Placeholder dictionary to store destination QR file paths
# fixed_destination_qr_data = {
#     "Destination_1": "destination1.png",
#     "Destination_2": "destination2.png"
# }

# def send_command(command, speed):
#     global arduino
#     command_str = f"MOVE {0 if command == 'STOP' else speed} {0 if command == 'STOP' else speed}\n"
#     arduino.write(command_str.encode())
#     print(f"Sent command: {command_str.strip()}")

# def region_of_interest(img, vertices):
#     mask = np.zeros_like(img)
#     cv2.fillPoly(mask, vertices, 255)
#     return cv2.bitwise_and(img, mask)

# def draw_the_lines(img, lines):
#     blank_image = np.zeros_like(img)
#     if lines is not None:
#         for line in lines:
#             for x1, y1, x2, y2 in line:
#                 cv2.line(blank_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
#     return cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)

# def process(image):
#     if image is None:
#         return None, None

#     height, width = image.shape[:2]
#     roi_vertices = [(0, height), (width // 2, height // 2), (width, height)]
    
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     canny_image = cv2.Canny(gray_image, 100, 120)
#     cropped_image = region_of_interest(canny_image, np.array([roi_vertices], np.int32))
    
#     lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 50, minLineLength=40, maxLineGap=100)
#     return draw_the_lines(image, lines), lines

# def determine_movement(lines):
#     return "MOVE_FORWARD" if lines is not None else "STOP"

# def extract_destination_from_qr(data):
#     try:
#         segments = data.split('|')
#         for segment in segments:
#             if segment.startswith('destination_'):
#                 return segment.strip()
#         return data.strip()  # To handle fixed destinations that are just the name
#     except Exception as e:
#         print(f"Error extracting destination: {e}")
#         return None

# def camera_thread():
#     global stopped, speed, qr_detected, destination_detected, movement_command
#     camera_id = 0
#     delay = 1
#     window_name = 'OpenCV QR Code and Line Detection'

#     qcd = cv2.QRCodeDetector()
#     cap = cv2.VideoCapture(camera_id)

#     # Reduce frame size to decrease processing load
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

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

#         data, points, _ = qcd.detectAndDecode(frame)
#         qr_detected = False
#         destination_detected = None
#         if data:
#             s = data.strip()  # Strip any extraneous characters
#             destination = extract_destination_from_qr(s)
#             if destination and destination in fixed_destination_qr_data:
#                 print(f"Detected destination: {destination}")
#                 qr_detected = True
#                 destination_detected = destination
#                 stopped = True  # Stop the robot
#                 movement_command = "STOP"
                
#                 # Draw green box around detected QR code
#                 points = np.int32(points)
#                 if points is not None:
#                     cv2.polylines(frame, [points], True, (0, 255, 0), 3)
                
#                 # Display dialog
#                 cv2.putText(frame, "Correct QR Code Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#                 cv2.imshow(window_name, frame)
#                 cv2.waitKey(1)
                
#                 # Wait for 30 seconds
#                 time.sleep(30)
#                 stopped = False  # Resume movement after waiting
#                 print("You have reached your destination.")
#             else:
#                 # Draw red box around ignored QR code
#                 points = np.int32(points)
#                 if points is not None:
#                     cv2.polylines(frame, [points], True, (0, 0, 255), 3)
                
#                 # Display dialog
#                 cv2.putText(frame, "Incorrect QR Code", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
#                 print(f"Ignored QR code: {s}")

#         if not qr_detected:
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

# # Function to take user input for object details and generate QR code
# def generate_object_qr():
#     name = input("Enter object name: ")
#     quantity = input("Enter object quantity: ")
#     destination = input("Enter object destination: ")
#     data = f"name:{name}|quantity:{quantity}|destination:{destination}"
#     filename = f"{name}.png"
#     generate_qr(data, filename) 
#     print(f"QR code generated for {name} and saved as {filename}")

# # Function to take user input for fixed destination QR codes
# def generate_fixed_destination_qr():
#     destination = input("Enter fixed destination name: ")
#     data = destination
#     filename = f"{destination}.png"
#     generate_qr(data, filename)
#     print(f"Fixed QR code generated for {destination} and saved as {filename}")

# # Generate QR codes for objects based on user input
# num_objects = int(input("Enter the number of objects to generate QR codes for: "))
# for _ in range(num_objects):
#     generate_object_qr()

# # Generate fixed destination QR codes based on user input
# num_destinations = int(input("Enter the number of fixed destinations to generate QR codes for: "))
# for _ in range(num_destinations):
#     generate_fixed_destination_qr()

# # Start threads
# camera_thread = threading.Thread(target=camera_thread)
# arduino_thread = threading.Thread(target=arduino_thread)

# camera_thread.start()
# arduino_thread.start()

# # Join threads (wait for them to finish if needed)
# camera_thread.join()
# arduino_thread.join()

# # Close serial connection
# arduino.close()


