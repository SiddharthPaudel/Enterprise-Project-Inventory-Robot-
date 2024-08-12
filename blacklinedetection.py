import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines(img, lines, color=[0, 255, 0], thickness=2):
    # Function to draw lines on the image
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def detect_black_lines(image):
    # Convert image to HSV color space (better for color detection)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define lower and upper bounds for black color in HSV
    lower_black = np.array([0, 0, 0], dtype=np.uint8)
    upper_black = np.array([180, 255, 30], dtype=np.uint8)
    
    # Threshold the HSV image to get only black colors
    mask = cv2.inRange(hsv, lower_black, upper_black)
    
    # Bitwise AND mask with original image to extract black lines
    black_lines = cv2.bitwise_and(image, image, mask=mask)
    
    # Convert to grayscale
    gray = cv2.cvtColor(black_lines, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blur, 50, 150)
    
    # Define region of interest (ROI)
    height, width = image.shape[:2]
    roi_vertices = np.array([[(0, height), (width/2, height/2), (width, height)]], dtype=np.int32)
    masked_edges = region_of_interest(edges, roi_vertices)
    
    # Perform Hough transform to detect lines
    lines = cv2.HoughLinesP(masked_edges, rho=2, theta=np.pi/180, threshold=50, minLineLength=100, maxLineGap=50)
    
    # Draw detected lines on the image
    line_image = np.zeros_like(image)
    if lines is not None:
        draw_lines(line_image, lines)
    
    # Overlay lines on the original image
    result = cv2.addWeighted(image, 0.8, line_image, 1.0, 0.0)
    
    return result

# Video capture from a file or camera
cap = cv2.VideoCapture('warehouse_video.mp4')  # Replace with your video file or camera index

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    processed_frame = detect_black_lines(frame)
    
    cv2.imshow('Warehouse Robot Line Detection', processed_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
