import logging
import json
import sys
import os
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def format(self, record):
        logobj = {}
        
        # Include standard log record attributes
        logobj['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        logobj['level'] = record.levelname
        logobj['logger'] = record.name
        logobj['message'] = record.getMessage()
        
        # Include exception info if available
        if record.exc_info:
            logobj['exception'] = self.formatException(record.exc_info)
        
        # Include custom attributes set on the record
        for key, value in record.__dict__.items():
            if key not in ('args', 'asctime', 'created', 'exc_info', 'exc_text', 
                          'filename', 'funcName', 'id', 'levelname', 'levelno',
                          'lineno', 'module', 'msecs', 'message', 'msg', 'name',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'stack_info', 'thread', 'threadName'):
                logobj[key] = value
        
        return json.dumps(logobj)

def setup_logging(service_name='hockey_backend'):
    """Configure JSON logging for containerized environments"""
    logger = logging.getLogger(service_name)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Configure root logger - level based on environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level))
    
    # Create console handler and set formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)
    
    # Add file handler only in development (not in containers)
    if os.environ.get('ENVIRONMENT') != 'production':
        file_handler = logging.FileHandler("hockey_data.log")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    
    return logger