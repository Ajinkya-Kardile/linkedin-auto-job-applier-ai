#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

import logging
import os
from datetime import datetime

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure the logger
logger = logging.getLogger("LinkedInBot")
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(f"logs/log_{datetime.now().strftime('%Y-%m-%d')}.txt", encoding='utf-8')

# Set logging level for handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(log_format)
file_handler.setFormatter(log_format)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def print_lg(*args, **kwargs):
    """Backward compatibility for your old print_lg calls"""
    message = " ".join([str(arg) for arg in args])
    logger.info(message)


def critical_error_log(context, exception):
    """Log critical errors with stack trace"""
    logger.error(f"CRITICAL ERROR in {context}: {str(exception)}", exc_info=True)
