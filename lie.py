import serial
import serial.tools.list_ports
import time

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description:  # "CH340" is common for many Arduino clones
            return port.device
    return None

# Detect Arduino port
arduino_port = find_arduino_port()

if arduino_port is None:
    print("Arduino not found. Please check the connection.")
else:
    print(f"Arduino found on port: {arduino_port}")

    # Configure the serial port
    ser = serial.Serial(port=arduino_port, baudrate=115200)  

    # Give some time to establish the serial connection
    time.sleep(2)

    # Function to send PWM command
    def send_wheel_command(move1, move2):
        command = f"MOVE {move1} {move2}\n"
        print(f"Sending command: {command.strip()}")
        ser.write(command.encode())  # Send the command to the Arduino

    # Main loop to continuously ask for user input and send commands
    try:
        while True:
            user_input = input("Enter MOVE values (format: move1 move2) or type 'exit' to quit: ")

            if user_input.lower() == 'exit':
                break

            try:
                # Split the input into two values
                pwm_value1, pwm_value2 = map(int, user_input.split())
                
                # Send the PWM command to the Arduino
                send_wheel_command(pwm_value1, pwm_value2)
            except ValueError:
                print("Invalid input. Please enter two integer values separated by a space.")

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

    finally:
        # Close the serial connection
        ser.close()
        print("Serial connection closed.")