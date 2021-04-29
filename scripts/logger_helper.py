#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
import pprint
import sys

log_handler = None
verbose_logging = "--verbose" in sys.argv
debug_mode = verbose_logging or "--debug-mode" in sys.argv

def get_logger(prefix):
  global log_handler
  global verbose_logging
  global debug_mode
  logger = logging.getLogger(prefix)
  if log_handler is None:
    format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
    if verbose_logging:
      logging.basicConfig(level=logging.DEBUG, format = format_string)
    else:
      script_file = os.path.basename(sys.argv[0])
      log_file = "/var/log/jet/{}.log".format(os.path.splitext(script_file)[0])
      log_handler = logging.handlers.TimedRotatingFileHandler(log_file, when="D", backupCount=14)
      my_formatter = logging.Formatter(format_string)
      log_handler.setFormatter(my_formatter)
  if debug_mode:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)
  if not verbose_logging:
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
