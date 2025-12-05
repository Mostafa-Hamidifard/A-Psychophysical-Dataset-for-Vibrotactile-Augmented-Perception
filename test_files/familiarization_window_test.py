from src.gui.window_2 import FamiliarizationWindow
import PySimpleGUI as sg


def test_familiarization_window():
    fam_window = FamiliarizationWindow()
    window2 = fam_window.create_window(hide=False)
    while True:
        window, event, values = sg.read_all_windows(timeout=100)
        info_window_answer = fam_window.loop_check_handler(window, event, values)
        if event == sg.WIN_CLOSED or event == "-EXIT-":
            break

    window2.close()
