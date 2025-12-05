import PySimpleGUI as sg
from typing import Dict
from abc import ABC, abstractmethod
from typing import Union, List


# Todo: Develop a feature to talk between windows
class Window(ABC):
    def __init__(self, window_title):
        self.action_keys = []
        self.element_keys = []
        self.title = window_title
        self.layout = self.generate_layout()
        self.handlers = self._action_handlers()

    def loop_check_handler(self, window, event, values):
        """

        it checks if any of events relating to action keys is called and executes its corresponding handler.

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
        dict
            {"window_title": title of the window, "event": the event, "answer": the handler's answer}

        """
        return_dict = {"window_title": self.title, "event": None, "answer": None}
        if event in self.action_keys:
            answer = self.handlers[event](window, event, values)
            return_dict["event"] = event
            return_dict["answer"] = answer
        return return_dict

    def generate_layout(self):
        """define window layout and fill the action_keys and element_keys"""
        raise NotImplementedError()

    def _action_handlers(self) -> Dict:
        handlers = dict()
        for key in self.action_keys:
            handler_name = f"{key}_handler"
            if hasattr(self, handler_name):
                handlers[key] = getattr(self, handler_name)
            else:
                NotImplementedError(f"Handler for key '{key}' is not implemented")
        return handlers

    def create_window(self, hide=True):
        self.window = sg.Window(self.title, self.layout, finalize=True)
        if hide:
            self.window.hide()
        return self.window

    def get_key_list(self):
        return self.element_keys + self.action_keys

    def close(self):
        if hasattr(self, "window"):
            self.window.close()
        else:
            print("Wrong attempt to close the window before creating.")


class Window_manager(ABC):
    # def __init__(self, windows_list: List[Window]):
    def __init__(self):
        self.current_window = None
        # for window in windows_list:
        #     if not isinstance(window, Window):
        #         raise TypeError("Some items in the windows_list are not of class window")
        #     window.window.hide()
        # self.windows = list(windows_list)

    @abstractmethod
    def create_windows(self) -> List[Window]:
        """This method must be implemented by child classes and returns the list of windows after creation"""
        pass

    def start(self, start_id):
        self.windows = self.create_windows()
        self.windows[start_id].window.un_hide()
        self.current_window = self.windows[start_id]
        while True:
            window, event, values = sg.read_all_windows(timeout=100)
            if event == sg.WIN_CLOSED or event == "-EXIT-":
                self.current_window.close()
                break
            self.current_window.loop_check_handler(window, event, values)
            transition_id = self.check_transition()
            if transition_id != None:
                self.transit_window(transition_id)
        for window in self.windows:
            window.close()
        del self.windows

    def check_transition(self) -> Union[None, int]:
        """
        It is expected that a custom window manager subclass is defined which has functions with
        the format of {window1_title}2{window2_title}_check() and it tries to check if the trantions is
        possible or not.

        Returns
        -------
        Union[None, int]
            If the transition is possible, the id number of target window is returned; otherwise, None is returned.
        """
        transition_window_id = None
        if self.current_window == None:
            return transition_window_id
        for i, window in enumerate(self.windows):
            func_name = self.current_window.title + "2" + window.title + "_check"
            if hasattr(self, func_name):
                transition_available = getattr(self, func_name)()
                if transition_available:
                    return i
        return None

    def transit_window(self, id):
        """
        It is expected that a custom window manager subclass is defined which has functions with
        the format of {window1_title}2{window2_title}_action() and it tries to perform the transition.

        Parameters
        ----------
        id : TYPE
            id of the target window in the windows_list.

        Raises
        ------
        NotImplementedError
            if the ID corresponds to a window that does not have any transition method from the current window.

        Returns
        -------
        None.

        """
        future_window = self.windows[id]
        func_name = self.current_window.title + "2" + future_window.title + "_action"
        if hasattr(self, func_name):
            # performing the transition
            getattr(self, func_name)(id)
            self.current_window = future_window
        else:
            raise NotImplementedError()
