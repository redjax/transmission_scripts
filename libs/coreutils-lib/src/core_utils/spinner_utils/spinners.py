import logging

log = logging.getLogger(__name__)

import itertools
import sys
import threading
import time
import contextlib

__all__ = ["SimpleSpinner"]


class SimpleSpinner(contextlib.ContextDecorator):
    def __init__(self, message="Processing"):
        self.message = message
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.stop_event = threading.Event()
        self.spinner_thread = None

        self.logger: logging.Logger | None = None

    def spin(self):
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)

    def __enter__(self):
        self.logger = log.getChild("SimpleSpinner")
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        self.spinner_thread.join()
        sys.stdout.write("\r")
        sys.stdout.flush()
        if exc_type is None:
            self.logger.info(f"\r{self.message} Complete!")
        else:
            self.logger.error(f"\r{self.message} Failed!")
