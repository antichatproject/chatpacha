#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
import pprint
import sys

import antichat_config

log_handler = None
default_level = logging.INFO
verbose_logging = "--verbose" in sys.argv
debug_mode = "--debug" in sys.argv

def get_logger(prefix):
  global log_handler
  global verbose_logging
  global debug_mode
  global default_level
  logger = logging.getLogger(prefix)
  level = default_level
  if verbose_logging:
    level = logging.DEBUG
  logger.setLevel(level)
  if log_handler is None:
    format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
    script_file = os.path.basename(sys.argv[0])
    if script_file != "daemon.py" or debug_mode:
      logging.basicConfig(level=level, format = format_string)
    else:
      if not os.path.isdir(antichat_config.log_path):
        os.mkdir(antichat_config.log_path)
      log_file = os.path.join(antichat_config.log_path, "{}.log".format(os.path.splitext(script_file)[0]))
      log_handler = logging.handlers.TimedRotatingFileHandler(log_file, when="D", backupCount=14)
      my_formatter = logging.Formatter(format_string)
      log_handler.setFormatter(my_formatter)
  if log_handler != None:
    logger.addHandler(log_handler)
  return logger

if __name__ == "__main__":
  logger1 = get_logger("Prefix1")
  logger1.debug("Message log debug")
  logger1.info("Message log info")
  logger1.error("Message log error")
  logger2 = get_logger("Prefix2")
  logger2.debug("Message log debug")
  logger2.info("Message log info")
  logger2.error("Message log error")
  logger1.debug("Message log debug")
  logger1.info("Message log info")
  logger1.error("Message log error")
