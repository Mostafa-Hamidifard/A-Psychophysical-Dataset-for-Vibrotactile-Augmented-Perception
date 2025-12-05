import PySimpleGUI as sg
from config import window_1_layout_config as layout_config
from .window import Window
from typing import List
from src.utils import is_float, save_user_info


class InfoWindow(Window):

    def __init__(self, user_info_path, title="subject_info"):
        super().__init__(title)
        self.personal_info = None
        self._info_path = user_info_path
        self.user_info_saved = False

    def generate_layout(self) -> List:
        def input_section(txt_name: str, font):
            key = txt_name.upper()
            self.element_keys.append(key)
            return [
                sg.Text(f"{txt_name}", size=(layout_config["text_size"], 1), font=font),
                sg.Input(key=key, font=font, expand_x=True),
            ]

        layout = [
            [
                sg.Text(
                    "Please enter your information", font=layout_config["font_large"]
                )
            ],
            input_section("First Name", layout_config["font_medium"]),
            input_section("Last Name", layout_config["font_medium"]),
            input_section("Education", layout_config["font_medium"]),
            input_section("Age", layout_config["font_medium"]),
            input_section("Weight", layout_config["font_medium"]),
            input_section("Height", layout_config["font_medium"]),
            input_section("Waist", layout_config["font_medium"]),
            input_section("Body fat percentage", layout_config["font_medium"]),
            input_section("Muscular? (0,1)", layout_config["font_medium"]),
            input_section("Being Ticklish? (0,1)", layout_config["font_medium"]),
            input_section(
                "Left Hand or Right Hand?(left:0 or right:1)",
                layout_config["font_medium"],
            ),
            input_section(
                "Are you currently being treated for depression?",
                layout_config["font_medium"],
            ),
            input_section(
                "Do you take any medication regularly?", layout_config["font_medium"]
            ),
            input_section(
                "What is the prescription for your left eye?",
                layout_config["font_medium"],
            ),
            input_section(
                "What is the prescription for your right eye?",
                layout_config["font_medium"],
            ),
            input_section(
                "Do you have any history of abdominal surgery?",
                layout_config["font_medium"],
            ),
            input_section(
                "Do you have any history of spinal surgery?",
                layout_config["font_medium"],
            ),
            [
                sg.Text(
                    "Have you ever been diagnosed with",
                    font=layout_config["font_large"],
                )
            ],
            input_section("a visual impairment?", layout_config["font_large"]),
            input_section("epilepsy?", layout_config["font_large"]),
            input_section("autism?", layout_config["font_large"]),
            input_section("ADHD?", layout_config["font_large"]),
            input_section(
                "any neurological or mental health conditions?",
                layout_config["font_large"],
            ),
            [
                sg.Button(
                    "Start Test", font=layout_config["font_medium"], key="START_TEST"
                ),
            ],
        ]
        self.action_keys.append("START_TEST")
        # self.action_keys.append("EXIT")

        return layout

    def START_TEST_handler(self, window, event, values) -> bool:
        """
        It checks user inputs and tries to store the user info upon being valid.

        Parameters
        ----------
        window : TYPE
            window from reading window.
        event : TYPE
            event from reading window.
        values : TYPE
            values from reading window.

        Returns
        -------
        bool
            True if storing was successful otherwise False.
        """

        user_info = {key: values[key] for key in self.element_keys}
        save_user_info(self._info_path, user_info)
        self.user_info_saved = True
        return True
