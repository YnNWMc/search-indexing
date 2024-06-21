import os
import logging
import json
import logstash

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'where': record.__dict__.get('where', os.path.basename(record.pathname)),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'filename': record.filename,
            'funcName': record.funcName,
            'lineno': record.lineno,
        }
        return json.dumps(log_record)

class CustomLogger:
    def __init__(self, log_folder, log_file='application.log', logstash_host='localhost', logstash_port=5044):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        self.log_folder = log_folder
        self.log_file = log_file

        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

        self.file_handler = self._get_file_handler(self.log_file)
        self.logger.addHandler(self.file_handler)

        self.logstash_handler = self._get_logstash_handler(logstash_host, logstash_port)
        self.logger.addHandler(self.logstash_handler)

    def _get_file_handler(self, filename):
        file_path = os.path.join(self.log_folder, filename)
        handler = logging.FileHandler(file_path)
        handler.setLevel(logging.DEBUG)
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        return handler

    def _get_logstash_handler(self, host, port):
        handler = logstash.LogstashHandler(host, port, version=1)
        handler.setLevel(logging.DEBUG)
        return handler

    def error_log(self, message, where="Unknown"):
        self.logger.error(message, extra={'where': where})

    def info_log(self, message, where="Unknown"):
        self.logger.info(message, extra={'where': where})

    def debug_log(self, message, where="Unknown"):
        self.logger.debug(message, extra={'where': where})

    def warning_log(self, message, where="Unknown"):
        self.logger.warning(message, extra={'where': where})

    def trace_log(self, message, where="Unknown"):
        self.logger.log(logging.NOTSET, message, extra={'where': where})

    def critical_log(self, message, where="Unknown"):
        self.logger.critical(message, extra={'where': where})