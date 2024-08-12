import serial
import serial.tools.list_ports

# List all available ports
ports = serial.tools.list_ports.comports()
available_ports = [port.device for port in ports]
print(f"Available ports: {available_ports}")

# Attempt to open the port
try:
    ser = serial.Serial('COM3', 115200, timeout=1)
    time.sleep(2)  # Wait for the serial connection to initialize
    print("Successfully connected to COM3")
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()
