import os
import sys
import json
import logging
import threading
from typing import Optional
from logging.handlers import TimedRotatingFileHandler

class JsonFormatter(logging.Formatter):
    def format(self, record):
        thread_id = threading.current_thread().name
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger_name': record.name,
            "thread_name": thread_id
        }
        if isinstance(record.msg, dict):
            log_data.update(record.msg)
        else:
            log_data['message'] = record.getMessage()

        return json.dumps(log_data, separators=(",", ":"))  # compact JSON


class CSVFormatter(logging.Formatter):
    def format(self, record):
        timestamp = self.formatTime(record)
        level = record.levelname
        logger_name = record.name
        thread_name = threading.current_thread().name

        if isinstance(record.msg, dict):
            event_type = record.msg.get("event", "UNKNOWN")
            keys = [k for k in record.msg.keys() if k != "event"]
            xs = [str(record.msg[k]) for k in keys]
            message = f'{event_type},{",".join(xs)}'
        else:
            message = str(record.getMessage())

        return f'{timestamp},{level},{logger_name},{thread_name},{message}'


class Log(logging.Logger):
    def __init__(
        self,
        formatter: logging.Formatter = JsonFormatter(),
        name: str = "asmac-backend",
        level: int = logging.DEBUG,
        path: str = "/asmac/backend",
        disabled: bool = False,
        console_handler_filter=lambda record: record.levelno == logging.DEBUG,
        file_handler_filter=lambda record: record.levelno == logging.INFO,
        console_handler_level: int = logging.DEBUG,
        file_handler_level: int = logging.INFO,
        error_log: bool = False,
        filename: Optional[str] = None,
        output_path: Optional[str] = None,
        error_output_path: Optional[str] = None,
        create_folder: bool = True,
        to_file: bool = True,
        when: str = "m",
        interval: int = 10
    ):
        super().__init__(name, level)

        if create_folder:
            os.makedirs(path, exist_ok=True)

        if not disabled:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(console_handler_level)
            console_handler.addFilter(console_handler_filter)
            self.addHandler(console_handler)

            # File handler
            if to_file:
                filehandler = TimedRotatingFileHandler(
                    filename=output_path or f"{path}/{filename or name}.log",
                    when=when,
                    interval=interval
                )
                filehandler.setFormatter(formatter)
                filehandler.setLevel(file_handler_level)
                filehandler.addFilter(file_handler_filter)
                self.addHandler(filehandler)

            # Error log handler
            if error_log:
                error_file_handler = logging.FileHandler(
                    filename=error_output_path or f"{path}/{filename or name}.error"
                )
                error_file_handler.setFormatter(formatter)
                error_file_handler.setLevel(logging.ERROR)
                error_file_handler.addFilter(lambda record: record.levelno == logging.ERROR)
                self.addHandler(error_file_handler)


def get_logger(name: str, ltype: str = "CSV", debug: bool = True, path: str = "/log") -> Log:
    if ltype.upper() == "CSV":
        return Log(
            formatter=CSVFormatter(),
            console_handler_filter=lambda x: debug,
            file_handler_filter=lambda x: x.levelno == logging.INFO,
            error_log=True,
            path=path,
            name=name
        )
    else:
        return Log(
            formatter=JsonFormatter(),
            console_handler_filter=lambda x: debug,
            error_log=True,
            path=path,
            name=name
        )
