"""
Production logging configuration for Finance App.

Provides JSON structured logging for easy parsing and aggregation.

Import in main.py:
    from deployment.logging_config import setup_logging
    setup_logging()
"""

import json
import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO"):
    """
    Configure structured JSON logging for production.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # JSON format for stdout (stdout for container/systemd)
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setLevel(getattr(logging, log_level))
    
    # JSON formatter with custom fields
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s %(filename)s %(lineno)d'
    )
    json_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_handler)
    
    # Application logger
    app_logger = logging.getLogger("finance_app")
    app_logger.setLevel(getattr(logging, log_level))
    
    # SQLAlchemy logger (reduce noise)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Uvicorn logger configuration
    logging.getLogger("uvicorn").setLevel(getattr(logging, log_level))
    logging.getLogger("uvicorn.access").setLevel(getattr(logging, log_level))
    
    return app_logger


# Example JSON log output:
# {
#   "timestamp": "2026-08-25T10:30:45.123Z",
#   "level": "INFO",
#   "name": "finance_app.application.use_cases.auth.auth_use_cases",
#   "message": "User registered successfully",
#   "filename": "auth_use_cases.py",
#   "lineno": 42,
#   "user_id": "abc-123",
#   "email": "user@example.com"
# }
#
# To add custom fields to logs:
#   logger = logging.getLogger("finance_app")
#   logger.info("User action", extra={"user_id": "abc-123", "action": "login"})
