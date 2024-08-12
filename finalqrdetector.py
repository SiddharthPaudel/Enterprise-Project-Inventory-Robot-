import cv2
from pyzbar.pyzbar import decode
import serial

# Initialize serial communication with Arduino if needed
# ser = serial.Serial('COM1', 9600)  # Example port and baud rate

# Function to detect QR codes
def detect_qr(image_path):
    image = cv2.imread(image_path)
    barcodes = decode(image)
    
    for barcode in barcodes:
        qr_data = barcode.data.decode('utf-8')
        print("Detected QR code:", qr_data)
        return qr_data  # Return first detected QR code

    return None  # Return None if no QR code detected

# Example usage:
object_qr_path = "object1.png"
detected_qr = detect_qr(object_qr_path)

# Compare detected QR with destination QR
if detected_qr == destination_qr:
    print("Destination reached. Stopping the robot.")
    # Code to stop the robot
else:
    print("Searching for destination. Continue following the line.")
    # Code to continue following the line

# Close serial communication if opened
# ser.close()
