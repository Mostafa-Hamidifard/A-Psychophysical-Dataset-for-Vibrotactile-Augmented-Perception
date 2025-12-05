# from src.gui.window import Window_manager
from src.gui.window import Window_manager, Window
from src.gui.window_1 import InfoWindow
from src.gui.window_2 import FamiliarizationWindow
from src.gui.window_3 import MainExperimentWindow
from .min_vibration_window import MinVibrationWindow
from typing import List
from config import USER_FILE_PATH


# Vibration Experiment Manager
class VEManager(Window_manager):

    def min_vibration_window2familiarization_check(self):
        min_vib_window = self.current_window
        if not hasattr(min_vib_window, "start_main_exp_pressed"):
            raise AttributeError("No attribute with name of 'start_main_exp_pressed'.")
        if min_vib_window.start_main_exp_pressed:
            return True
        else:
            return False

    def min_vibration_window2familiarization_action(self, id) -> None:
        if not hasattr(self.current_window, "minimum_vibrations"):
            raise AttributeError("No attribute with name of 'minimum_vibrations'.")
        self.windows[id].minimum_vibrations = self.current_window.minimum_vibrations
        self.windows[id].all_min_vibrations = self.current_window.all_min_vibrations

        self.current_window.disable()
        future_window = self.windows[id]
        future_window.window.un_hide()

    def subject_info2min_vibration_window_check(self) -> bool:
        subject_info_window = self.current_window
        if not hasattr(subject_info_window, "user_info_saved"):
            raise AttributeError("No attribute with name of 'user_info_saved'.")
        if subject_info_window.user_info_saved:
            # user_info has been saved and We are ready to go to the familiarization window
            return True
        else:
            return False

    def subject_info2min_vibration_window_action(self, id) -> None:
        self.current_window.close()
        future_window = self.windows[id]
        future_window.window.un_hide()

    def familiarization2main_experiment_check(self) -> bool:
        fam_window = self.current_window
        if not hasattr(fam_window, "start_main_exp_pressed"):
            raise AttributeError("No attribute with name of 'start_main_exp_pressed'.")
        if fam_window.start_main_exp_pressed:
            return True
        else:
            return False

    def familiarization2main_experiment_action(self, id) -> None:
        if not hasattr(self.current_window, "minimum_vibrations"):
            raise AttributeError("No attribute with name of 'minimum_vibrations'.")
        self.windows[id].minimum_vibrations = self.current_window.minimum_vibrations
        self.windows[id].all_min_vibrations = self.current_window.all_min_vibrations

        self.current_window.disable()
        future_window = self.windows[id]
        future_window.window.un_hide()

    def create_windows(self) -> List[Window]:
        window1 = InfoWindow(user_info_path=USER_FILE_PATH, title="subject_info")
        window1.create_window()
        min_vib_window = MinVibrationWindow(title="min_vibration_window")
        min_vib_window.create_window()
        window2 = FamiliarizationWindow(title="familiarization")
        window2.create_window()
        window3 = MainExperimentWindow(title="main_experiment")
        window3.create_window()
        return [window1, min_vib_window, window2, window3]
