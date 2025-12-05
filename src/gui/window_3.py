import time

import PySimpleGUI as sg
from config import window_3_layout_config as layout_config
from config import (
    arduino_config,
    NUM_VIBRATION,
    USER_FILE_PATH,
    SAMPLES_BEFORE_REST,
    REST_DURATION_SECONDS,
    MINIMUM_VIB_TIME,
)
from .window import Window
from typing import List
from src.utils import (
    create_vibration_patterns,
    save_experiment_data,
    read_user_file,
    CustomTimer,
)
from src.arduino.SerialCommunication import SerialCommunication
import numpy as np


class MainExperimentWindow(Window):
    def __init__(self, title="main_experiment"):
        self.minimum_vibrations = [100] * NUM_VIBRATION
        self.all_min_vibrations = np.zeros((5, 3))
        self.experiment_resume = False
        self.vibration_patterns = create_vibration_patterns()
        super().__init__(title)
        self.vibration_number = 0
        self.serial_interface = SerialCommunication(NUM_VIBRATION)
        self.graph_last_click = {"coordinate": None, "id": None, "time": None}
        self.user_data = {}
        self.interval_timer = CustomTimer()
        self.interval_timer.start()
        self.interval_timer.pause()

    def adjust_level(self, pattern: List[float]):
        pattern = list(pattern)
        for i, item in enumerate(pattern):
            min_int = self.minimum_vibrations[i]
            max_int = 255
            middle_int = (255 + min_int) / 2
            intensity_map = {0: 0, 85: min_int, 170: middle_int, 255: max_int}
            pattern[i] = intensity_map[item]
        return pattern

    def generate_layout(self) -> List:
        self.graph = sg.Graph(
            canvas_size=layout_config["graph_size"],
            graph_bottom_left=(-layout_config["graph_size"][0] / 2, 0),
            graph_top_right=(
                layout_config["graph_size"][0] / 2,
                layout_config["graph_size"][1],
            ),
            # Define the graph area
            change_submits=True,  # mouse click events
            drag_submits=False,  # mouse move events
            background_color="#fefefe",
            key="GRAPH",
            pad=0,
        )

        self.rem_vib_txt = sg.Text(
            f"Remaining: {len(self.vibration_patterns)}",
            font=layout_config["font_medium"],
            key="rem_vib_txt",
        )
        self.time_txt = sg.Text("", font=layout_config["font_medium"], key="time_txt")

        text_section = sg.Column(
            [[self.rem_vib_txt], [self.time_txt]],
            element_justification="left",
            pad=(10, 0),
        )
        self.start_btn = sg.Button(
            "Start",
            font=layout_config["font_large"],
            size=(15, 1),
            key="START_BTN",
            button_color=layout_config["btn_color"],
        )
        self.next_vib_btn = sg.Button(
            "Next Vibration",
            font=layout_config["font_large"],
            size=(15, 1),
            key="NEXT_VIB_BTN",
            button_color=layout_config["btn_color"],
            disabled=True,
        )

        button_section = sg.Column(
            [[self.next_vib_btn], [self.start_btn]],
            element_justification="right",
            pad=(0, 0),
        )

        bottom_section = sg.Column(
            [
                [
                    button_section,
                    sg.VerticalSeparator(color="#7f7f7f", pad=(0, 0)),
                    text_section,
                ]
            ],
            element_justification="space-between",
            expand_x=True,
        )
        radio_names = ["Very Low", "Low", "Medium", "High", "Very High"]
        self.radios = [
            sg.Radio(
                text,
                k=text,
                group_id="conf-radio",
                font=layout_config["font_medium"],
            )
            for text in radio_names
        ]
        radio_section = [
            sg.Text("Confidence?", font=layout_config["font_medium"])
        ] + self.radios
        layout = [
            [self.graph],
            radio_section,
            [sg.HorizontalSeparator(color="#7f7f7f", pad=(0, 0))],
            [bottom_section],
        ]
        self.action_keys = ["GRAPH", "START_BTN", "NEXT_VIB_BTN"]
        return layout

    @staticmethod
    def draw_graph_base(sg_graph: sg.Graph, n_arcs=36, n_abs=10):
        sg_graph.erase()
        small_rad = layout_config["radius"] / 10
        main_rad = layout_config["radius"]
        offset = layout_config["offset"]

        def custom_arc(extent, radius, color, fill_color=None):
            sg_graph.draw_arc(
                top_left=(-radius, radius + offset),
                bottom_right=(radius, -radius + offset),
                start_angle=0,
                extent=extent,
                line_width=1,
                arc_color=color,
                fill_color=fill_color,
            )

        for j in range(1, n_abs + 1):
            for i in range(n_arcs + 1):
                angle = 180 * i / n_arcs
                custom_arc(angle, j / n_abs * main_rad, "#7f7f7f")

        custom_arc(180, small_rad, "#7f7f7f", fill_color="#fefefe")
        custom_arc(180, main_rad, "#2f2f2f")

    def create_window(self, hide=True):
        super().create_window(hide)
        self.draw_graph_base(self.graph)
        return self.window

    def disable(self):
        self.serial_interface.stop_listening()
        self.serial_interface.close()

    def close(self):
        super().close()

    @property
    def experiment_completed(self) -> bool:
        return self.vibration_number >= len(self.vibration_patterns)

    def on_experiment_completed(self):
        sg.popup("Experiment completed.", title="Completion")
        # HERE, it tries to load what has been saved in the user info window so that it can store
        # it with the experiment data together.
        users_info = read_user_file(USER_FILE_PATH)
        user_info = users_info[-1]
        save_experiment_data(
            user_info,
            self.user_data,
            self.minimum_vibrations,
            self.all_min_vibrations.tolist(),
        )
        # Waiting for the last responses from arduino
        time.sleep(0.5)
        # CLOSING THE SERIAL CONNECTION
        self.serial_interface.stop_listening()
        self.serial_interface.close()
        # CLOSING THE WINDOW USING MANAGER
        self.window.write_event_value("-EXIT-", 0)

    def check_resting_phase(self, window, event, value):
        if self.vibration_number % SAMPLES_BEFORE_REST == 0:
            # assuming experiment is resumed. therefore we pause it:
            if self.experiment_resume:
                self.START_BTN_handler(window, event, value)
            timer = CustomTimer()
            timer.start()
            while timer.get_elapsed_time() < REST_DURATION_SECONDS:
                self.start_btn.update(
                    text="REST PHASE", disabled=True, button_color="red"
                )

                self.next_vib_btn.update(text="REST PHASE", button_color="red")
                self.time_txt.update(
                    value="remaining time: {}".format(
                        int(REST_DURATION_SECONDS - timer.get_elapsed_time())
                    )
                )
                self.window.refresh()
            timer.reset()
            self.start_btn.update(
                text="Start", button_color=layout_config["btn_color"], disabled=False
            )
            self.next_vib_btn.update(
                text="Next Vibration", button_color=layout_config["btn_color"]
            )
            self.time_txt.update(value="")
            self.window.refresh()
            self.window.read(timeout=1)
            self.START_BTN_handler(window, event, value)

    def GRAPH_handler(self, window, event, value) -> None:
        if not self.experiment_resume:  # checking if paused.
            return
        # if there is a selected point, it will be deleted first.
        if self.graph_last_click["id"] is not None:
            self.graph.delete_figure(self.graph_last_click["id"])
        # fetching the selected x y coordinates.
        x, y = value["GRAPH"]
        point_id = self.graph.draw_circle(
            (x, y), radius=5, fill_color="black", line_color="black"
        )
        self.graph_last_click["id"] = point_id
        self.graph_last_click["coordinate"] = (x, y)

        self.graph_last_click["time"] = self.interval_timer.get_elapsed_time()

    def START_BTN_handler(self, window, event, value):
        if not self.experiment_resume:
            # Resuming the timer
            self.interval_timer.resume()
            self.experiment_resume = True
            # Changing GUI visuals
            # self.start_btn.update(text="Pause")
            self.start_btn.update(disabled=True, visible=False)
            self.next_vib_btn.update(disabled=False)
            # Connecting to Arduino
            self.serial_interface.connect(
                arduino_config["port"], arduino_config["baudrate"]
            )
            self.serial_interface.start_listening()
            # Send the current set of vibrations to the Arduino
            vibration_pattern = self.vibration_patterns[
                self.vibration_number % len(self.vibration_patterns)
            ]
            adjusted_vib = self.adjust_level(vibration_pattern)
            self.serial_interface.send_value(adjusted_vib)
        else:
            # Pausing the timer
            self.interval_timer.pause()
            self.experiment_resume = False
            # Changing GUI visuals
            self.start_btn.update(text="Start")
            self.next_vib_btn.update(disabled=True)
            # Send [0, 0, 0, 0, 0] to the Arduino
            self.serial_interface.send_value([0, 0, 0, 0, 0])
            # Closing the connection
            self.serial_interface.stop_listening()
            self.serial_interface.close()

    def get_confidence_level(self, value):
        confidence = None
        for radio in self.radios:
            key = radio.key
            if value[key]:
                confidence = key
                break
        return confidence

    def next_page(self):
        # Resetting the confidence radio buttons
        for element in self.radios:
            element.update(value=False)
        # Remove the previous point on the graph
        self.graph.delete_figure(self.graph_last_click["id"])
        # Reset last clicked point
        self.graph_last_click = {"coordinate": None, "id": None, "time": None}
        # Send the vibration pattern to Arduino
        vibration_pattern = self.vibration_patterns[
            self.vibration_number % len(self.vibration_patterns)
        ]
        self.serial_interface.send_value([0, 0, 0, 0, 0])
        # turning off motors for 1 second after each sample
        start_t = time.time()
        while time.time() - start_t < 1:
            window, event, values = sg.read_all_windows(timeout=100)

        adjusted_vib = self.adjust_level(vibration_pattern)
        self.serial_interface.send_value(adjusted_vib)
        self.interval_timer.reset()
        self.interval_timer.start()

    def NEXT_VIB_BTN_handler(self, window, event, value) -> None:
        if not self.experiment_resume:  # check if experiment is paused
            return
        if self.graph_last_click["id"] is None:
            sg.popup(
                "Error: Please click on the graph before proceeding.",
                title="Input Error",
            )
            return
        confidence = self.get_confidence_level(value)
        if confidence is None:
            sg.popup(
                "Error: Please set your confidence before proceeding.",
                title="Input Error",
            )
            return
        if self.interval_timer.get_elapsed_time() < MINIMUM_VIB_TIME:
            sg.popup("Error: No Rush!", title="Input Error")
            return
        # Store in dictionary
        self.user_data[self.vibration_number] = {
            "vibration_pattern": self.vibration_patterns[
                self.vibration_number % len(self.vibration_patterns)
            ],
            "graph_point": self.graph_last_click["coordinate"],
            "confidence_level": confidence,
            "graph_time": self.graph_last_click["time"],
            "interval_time": self.interval_timer.get_elapsed_time(),
        }
        # Increment vibration number
        self.vibration_number += 1
        self.rem_vib_txt.update(
            value=f"Remaining: {(len(self.vibration_patterns) - self.vibration_number)}"
        )
        # Check completion
        if self.experiment_completed:
            self.on_experiment_completed()
        else:
            self.check_resting_phase(window, event, value)
            self.next_page()
