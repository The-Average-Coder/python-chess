import threading, time

START_TIME = 180

class Timer:
    def __init__(self):
        self.time = START_TIME
        self.timer_stop = threading.Event()
        self.timer_stop.set()
        self.start_time = 0

    def start_timer(self):
        if self.timer_stop.is_set():
            self.timer_stop.clear()
            self.start_time = time.perf_counter()
            threading.Timer(1, self.tick_timer).start()
    
    def tick_timer(self):
        if not self.timer_stop.is_set() and time.perf_counter() - self.start_time > 0.95:
            self.time -= 1
            threading.Timer(1, self.tick_timer).start()
    
    def stop_timer(self):
        self.timer_stop.set()