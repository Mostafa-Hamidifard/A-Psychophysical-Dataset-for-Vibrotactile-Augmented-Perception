import json
import random
import numpy as np

from config import USER_FILE_PATH, USER_FINAL_DATA_PATH, USER_FINAL_MIN_VIB_PATH
import os
import shutil
from abc import ABC


def remove_pycache(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                print(f"Removing: {pycache_path}")
                shutil.rmtree(pycache_path)  # Remove the __pycache__ directory


def save_experiment_data(user_info, user_data, min_vibrations,all_min_vibrations):
    min_vibrations = {f"vib_{i}":vib for i, vib in enumerate(min_vibrations)}
    new_data = {"user_info": user_info, "user_data": user_data, "min_vibrations": min_vibrations,"calibration_data":all_min_vibrations}
    try:
        with open(USER_FINAL_DATA_PATH, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                data.append(new_data)
            else:
                data = [data, new_data]
    except FileNotFoundError:
        data = [new_data]

    with open(USER_FINAL_DATA_PATH, "w") as file1:
        json.dump(data, file1, indent=4)


def create_vibration_patterns():
    user_count = len(read_user_file(USER_FILE_PATH))
    np.random.seed(user_count)
    random.seed(user_count)
    vib_list = []
    for level1 in [255 / 3, 255 * 2 / 3, 255]:
        for level2 in [255 / 3, 255 * 2 / 3, 255]:
            for i in range(4):
                temp = [0] * 5
                temp[i] = level1
                temp[i + 1] = level2
                vib_list.append(temp)

    for level in [255 / 3, 255 * 2 / 3, 255]:
        for i in range(5):
            temp = [0] * 5
            temp[i] = level
            vib_list.append(temp)

    vib_list = vib_list * 5
    random.shuffle(vib_list)

    return vib_list


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def read_user_file(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as file:
        users = json.load(file)
    return users


def save_user_info(file_path, user_info):
    if not os.path.exists(file_path):
        users = []
    else:
        with open(file_path, "r") as file:
            users = json.load(file)
    users.append(user_info)
    with open(file_path, "w") as file:
        json.dump(users, file, indent=4)


import time
import threading


class CustomTimer(ABC):
    def __init__(self):
        self.start_time = None
        self.pause_time = None
        self.is_paused = False
        self.is_running = False
        self.elapsed_time = 0
        self.thread = None  # Store the thread reference here
        self.lock = threading.Lock()

    def start(self):
        """Start or resume the timer."""
        with self.lock:
            if not self.is_running:
                self.start_time = time.time() - self.elapsed_time
                self.is_running = True
                self.is_paused = False
                if self.thread is None or not self.thread.is_alive():
                    self._run()  # Create a thread only if none exists

    def _run(self):
        """Run the timer on a second thread."""

        def timer_thread():
            while self.is_running and not self.is_paused:
                with self.lock:
                    self.elapsed_time = time.time() - self.start_time
                time.sleep(0.1)  # Adjust the interval for precision

        self.thread = threading.Thread(target=timer_thread)
        self.thread.daemon = True
        self.thread.start()

    def pause(self):
        """Pause the timer."""
        with self.lock:
            if self.is_running and not self.is_paused:
                self.is_paused = True
                self.pause_time = time.time()
                self.elapsed_time = self.pause_time - self.start_time

    def resume(self):
        """Resume the timer after pause."""
        with self.lock:
            if self.is_paused:
                self.start_time = time.time() - self.elapsed_time
                self.is_paused = False
                if self.thread is None or not self.thread.is_alive():
                    self._run()  # Resume timer on the existing thread

    def reset(self):
        """Reset the timer."""
        with self.lock:
            self.start_time = None
            self.pause_time = None
            self.is_paused = False
            self.is_running = False
            self.elapsed_time = 0
            self.thread = None  # Clear the thread reference

    def stop(self):
        """Stop the timer."""
        with self.lock:
            self.is_running = False
            self.is_paused = False
            self.thread = None  # No new thread will be created

    def get_elapsed_time(self):
        """Get the elapsed time without stopping the timer."""
        with self.lock:
            if self.is_running and not self.is_paused:
                return time.time() - self.start_time
            return self.elapsed_time

    @staticmethod
    def _test():
        # Usage Example:
        timer = CustomTimer()
        # Start the timer
        print("timer after creatrion: ", timer.get_elapsed_time())
        timer.start()
        time.sleep(2)  # Simulate some work
        print("timer after start and 2s sleep", timer.get_elapsed_time())
        # Pause the timer
        timer.pause()
        time.sleep(1)  # Wait during pause (not counted)
        print("timer after pause and 1s sleep", timer.get_elapsed_time())
        # Resume the timer
        timer.resume()
        time.sleep(2)  # Simulate more work
        print("timer after resume and 2s sleep", timer.get_elapsed_time())
        # Get elapsed time
        print(f"Elapsed time: {timer.get_elapsed_time()} seconds")
        # Stop or reset the timer when done
        timer.stop()
        print(timer.get_elapsed_time())
