import time

import PySimpleGUI as Sg
from config import min_vibration_layout_config as layout_config
from .window import Window
from config import arduino_config, NUM_VIBRATION
from typing import List
from src.arduino.SerialCommunication import SerialCommunication
import numpy as np


class MinVibrationWindow(Window):

    def __init__(self, title="min_vibration_window"):
        super().__init__(title)
        self.minimum_vibrations = [0] * NUM_VIBRATION
        self.serial_interface = SerialCommunication(NUM_VIBRATION)
        self.min_collection_finished = False
        self.start_main_exp_pressed = False

    def generate_layout(self) -> List:
        self.start_btn = Sg.Button(
            "Start Calibration",
            font=layout_config["font_small"],
            size=(20, 2),
            key="START_MIN",
        )
        self.feel_btn = Sg.Button(
            "I feel the vibration right NOW!",
            font=layout_config["font_small"],
            size=(40, 2),
            key="FEEL_VIB",
            disabled=True,
        )
        button_row = Sg.Column(
            [[self.start_btn, self.feel_btn]],
            element_justification="center",
            pad=(0, 20),
        )
        layout = [[button_row]]
        self.action_keys += ["START_MIN", "FEEL_VIB"]
        return layout

    def create_window(self, hide=True):
        super().create_window(hide)
        return self.window

    def disable(self):
        self.serial_interface.stop_listening()
        self.serial_interface.close()
        self.window.hide()

    def close(self):
        super().close()

    def START_MIN_handler(self, window, event, value):
        self.start_btn.update(disabled=True)
        self.feel_btn.update(disabled=False)

        self.serial_interface.connect(
            arduino_config["port"],
            arduino_config["baudrate"],
        )
        self.serial_interface.start_listening()
        self.test_min_vibrations()

    def test_min_vibrations(self):
        min_selected = np.zeros((5, 3))
        min_selected_idx = np.random.permutation(15)
        for idx in min_selected_idx:
            motor = idx // 3
            rep = idx % 3
            start_time = time.time()
            while True:
                window, event, values = Sg.read_all_windows(timeout=100)
                intensity = int((time.time() - start_time) * 3)
                if intensity > 255:
                    intensity = 255
                self._send_vibration(motor, intensity)
                if event == "FEEL_VIB":
                    min_selected[motor, rep] = intensity
                    break
        print("The selected vibrations are: ")
        print(min_selected)
        self.minimum_vibrations = np.max(min_selected, axis=1)
        self.all_min_vibrations = min_selected
        self.feel_btn.update(text="Start familiarization")

    def _send_vibration(self, index, value):
        vibration_list = [0] * NUM_VIBRATION
        vibration_list[index] = value
        self.serial_interface.send_value(vibration_list)

    def FEEL_VIB_handler(self, window, event, value):
        self.start_main_exp_pressed = True
