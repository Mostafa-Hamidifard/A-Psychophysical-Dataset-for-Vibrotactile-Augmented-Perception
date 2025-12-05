from src.gui.window_1 import InfoWindow
from config import USER_FILE_PATH
import PySimpleGUI as sg


def test_info_window():
    info_window = InfoWindow(USER_FILE_PATH)
    window1 = info_window.create_window(hide=False)
    while True:
        window, event, values = sg.read_all_windows(timeout=100)
        info_window_answer = info_window.loop_check_handler(window, event, values)
        if info_window_answer["answer"] != None and info_window_answer["answer"]:
            break
        if event == sg.WIN_CLOSED or event == "-EXIT-":
            break

    window1.close()
