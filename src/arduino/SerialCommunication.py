import serial
import time
import threading


class SerialCommunication:
    def __init__(self, n_vibrations):
        self.n_vibrations = n_vibrations
        self.listening = False
        self.listener_thread = None
        self.connected = False

    def connect(self, serial_port, baud_rate):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        try:
            self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
        except:
            print("Serial communication not stablished.")
            print("Please check the wires and arduino board.")
            return
        time.sleep(2)
        # Check if the serial connection is established
        if self.ser.is_open:
            print("Serial connection established.")
        else:
            print("Serial connection failed.")
            inp = input("Attempt again? (y)")
            if inp == "y" or inp == "Y":
                self.connect(serial_port, baud_rate)
            else:
                print("Connection wasn't established. try using connect manually...")

    def send_value(self, vibration_list):
        if not hasattr(self, "ser"):
            print("Serial communication has not been initialized.")
            return
        """list contains the vibration intensities of motors ranging from 0 to 255"""
        # Create a comma-separated string from the list of values
        input_string = ",".join(map(str, vibration_list)) + "\n"
        # Send the string to the Arduino
        self.ser.write(input_string.encode())
        print(f"Sent from computer : {input_string}")

    def receive_data_thread_func(self):
        while self.listening:
            response = self.ser.readline().decode().strip()
            if response:
                print(f"Arduino response: {response}")

    def start_listening(self):
        if not hasattr(self, "ser"):
            print("Serial communication has not been initialized.")
            return
        if not self.listening:
            self.listening = True
            self.listener_thread = threading.Thread(target=self.receive_data_thread_func, daemon=True)
            self.listener_thread.start()

    def stop_listening(self):
        if not hasattr(self, "ser"):
            print("Serial communication has not been initialized.")
            return
        time.sleep(0.5)
        if self.listening:
            self.listening = False
            if self.listener_thread:
                self.listener_thread.join(timeout=0.5)

    def close(self):
        if hasattr(self, "ser"):
            self.send_value([0, 0, 0, 0, 0])
            self.stop_listening()
            self.ser.close()
        else:
            print("Serial communication has not been initialized.")
