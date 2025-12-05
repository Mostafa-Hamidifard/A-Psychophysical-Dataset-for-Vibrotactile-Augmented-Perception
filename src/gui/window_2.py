import PySimpleGUI as sg
from .window import Window
from config import window_2_layout_config as layout_config
from config import arduino_config, NUM_VIBRATION
from typing import List, Union
from src.arduino.SerialCommunication import SerialCommunication
import numpy as np


class FamiliarizationWindow(Window):
    def __init__(self, title="familiarization"):
        super().__init__(title)
        self.resume = False
        self.serial_interface = SerialCommunication(NUM_VIBRATION)
        self.vibration_index = 0
        self.familiarization_finished = False
        self.start_main_exp_pressed = False
        self.minimum_vibrations = [85] * NUM_VIBRATION

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
            background_color="lightgrey",
            key="GRAPH",
            pad=0,
        )
        self.start_btn = sg.Button(
            "Start Familiarization",
            font=layout_config["font_small"],
            size=(20, 2),
            key="START_FAM",
        )
        self.next_btn = sg.Button(
            "Next Vibration",
            font=layout_config["font_small"],
            size=(20, 2),
            key="NEXT_VIB",
            disabled=True,
        )

        button_row = sg.Column(
            [[self.start_btn, self.next_btn]],
            element_justification="center",
            pad=(0, 20),
        )

        layout = [[self.graph], [button_row]]

        self.action_keys += ["START_FAM", "NEXT_VIB"]
        self.element_keys.append("GRAPH")
        return layout

    @staticmethod
    def draw_line_from_center(sg_graph: sg.Graph, level_index, motor_index):
        FamiliarizationWindow.draw_graph_base(sg_graph, layout_config["graph_size"])
        radius = layout_config["radius"]
        offset = layout_config["offset"]
        red_rad = radius * (level_index + 1) / 3
        red_extent = np.pi - np.pi * motor_index / (NUM_VIBRATION - 1)
        red_x = red_rad * np.cos(red_extent)
        red_y = red_rad * np.sin(red_extent)
        # sg_graph.draw_line((0, offset), (red_x, red_y + offset), color="red", width=10)
        sg_graph.draw_point((red_x, red_y + offset), size=20)

    @staticmethod
    def draw_graph_base(sg_graph: sg.Graph, GRAPH_SIZE, n_arcs=36, n_abs=10):
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
        self.draw_graph_base(self.graph, layout_config["graph_size"])
        return self.window

    def disable(self):
        self.serial_interface.stop_listening()
        self.serial_interface.close()
        self.window.hide()

    def close(self):
        super().close()

    def get_level(self, motor, index):
        min_int = self.minimum_vibrations[motor]
        max_int = 255
        middle_int = (255 + min_int) / 2
        intensities = [min_int, middle_int, max_int]
        return intensities[index]

    def _send_vibration(self, index=Union[int, None]):
        if index is None:
            vibration_list = [0] * NUM_VIBRATION
            self.serial_interface.send_value(vibration_list)
            self.draw_graph_base(self.graph, layout_config["graph_size"])
            return
        motor_index = index // 3  # Determine which motor to update
        level_index = index % 3  # Determine the level for the current motor
        vibration_list = [0] * NUM_VIBRATION
        if motor_index < len(vibration_list):
            vibration_list[motor_index] = self.get_level(motor_index, level_index)
            self.draw_line_from_center(self.graph, level_index, motor_index)
            self.serial_interface.send_value(vibration_list)

    def START_FAM_handler(self, window, event, value) -> bool:
        if not self.resume:  # starting or resuming
            self.resume = True
            self.start_btn.update(text="STOP")
            self.next_btn.update(disabled=False)
            self.serial_interface.connect(
                arduino_config["port"],
                arduino_config["baudrate"],
            )
            self.serial_interface.start_listening()
            if not self.familiarization_finished:
                self._send_vibration(self.vibration_index)  # turning vibrators on
        else:
            self._send_vibration(None)  # turning vibrators off
            self.resume = False
            self.start_btn.update(text="Start Familiarization")
            self.next_btn.update(disabled=True)
            self.serial_interface.stop_listening()
            self.serial_interface.close()
        return self.resume

    def NEXT_VIB_handler(self, window, event, value):
        if self.familiarization_finished:
            self.start_main_exp_pressed = True
            return
        self.vibration_index += 1
        if self.vibration_index < NUM_VIBRATION * 3:
            self._send_vibration(self.vibration_index)
        else:
            self.familiarization_finished = True
            self.start_btn.update(disabled=True)
            self._send_vibration(None)
            self.next_btn.update(text="Start Main Experiment")


if __name__ == "__main__":
    pass
