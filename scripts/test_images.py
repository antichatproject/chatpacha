#!/usr/bin/env python3
# test_images.py <dir> or <test.jpg>

import logging
import os
import pathlib
import pprint
import sys

sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "daemon"))

import antichat_config
import logger_helper
import model

def test_file(test_path, model):
  class_name, score = model.evaluate(test_path)
  pprint.pprint([class_name, int(score * 100), os.path.basename(test_path)])

logger_helper.default_level = logging.WARNING
model = model.Model()
test_path = pathlib.Path(sys.argv[1])
if os.path.isdir(test_path):
  chat_test = sorted(list(test_path.glob('*.jpg')))
  for image_path in chat_test:
    if os.path.splitext(image_path)[0].endswith("_thub"):
      continue
    test_file(image_path, model)
elif os.path.isfile(test_path):
  test_file(test_path, model)
