#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aionotify
import asyncio
import datetime
import json
import os
import pathlib
import pprint
import sys

import numpy as np
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

sys.path.append('..')

import antichat_config
import logger_helper
import model

class DirectoryEvaluater:
  def __init__(self, model, path, loop = None):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.model = model
    self.path = path
    self.loop = loop or asyncio.get_event_loop()
    self.thub_width = 320
    self.thub_height = 180
    self.watcher = aionotify.Watcher()
    self.watcher.watch(path = self.path, flags = aionotify.Flags.MOVED_TO | aionotify.Flags.CLOSE_WRITE)
    self.thumbnail_suffix = "_thub"
    self.valid_extensions = [ ".jpg" ]
    self.on_new_picture = None

  def should_process_image(self, path):
    name, extension = os.path.splitext(path)
    if os.path.exists(name + ".json"):
      return False
    return extension in self.valid_extensions and not name.endswith(self.thumbnail_suffix)

  async def run(self):
    self.logger.info("Run {}".format(self.path))
    await self.watcher.setup(self.loop)
    snap_dir = pathlib.Path(self.path)
    all_file_paths = list(snap_dir.glob('*'))
    for image_path in all_file_paths:
      if self.should_process_image(image_path):
        self.loop.create_task(self.process_image(image_path, datetime.datetime.now().timestamp(), False))
    while True:
      event = await self.watcher.get_event()
      self.logger.debug(pprint.pformat(event))
      name, extension = os.path.splitext(event.name)
      image_path = os.path.join(self.path, event.name)
      if self.should_process_image(image_path):
        self.loop.create_task(self.process_image(image_path, datetime.datetime.now().timestamp(), True))
    self.watcher.close()

  def get_timestamp(self, image_name, image_path):
    try:
      image_datetime = image_name.split("_")[1]
      mydate = datetime.datetime.strptime(image_datetime, "%Y%m%d-%H%M%S")
      return datetime.datetime.timestamp(mydate)
    except:
      self.logger.exception("Exception with {} {}".format(image_name, image_path))
      fname = pathlib.Path(image_path)
      self.logger.info(pprint.pformat(fname.stat()))
      return fname.stat().st_mtime

  def load_thubnail(self, image_path):
    return keras.preprocessing.image.load_img(image_path, target_size=(self.thub_height, self.thub_width))

  async def process_image(self, image_path, receive_timestamp, send_notification = False):
    try:
      filename = os.path.basename(image_path)
      path = os.path.dirname(image_path)
      self.logger.info("Process {}, ".format(filename, image_path))
      image_name, image_ext = os.path.splitext(filename)
      if not os.path.exists(image_path):
        self.logger.error("File doesn't exist {}".format(image_path))
        return
      thumbnail_name = image_name + self.thumbnail_suffix + image_ext
      thubnail = self.load_thubnail(image_path)
      result = self.model.evaluate(image_path)
      json_path = os.path.join(path, image_name + ".json")
      thumbnail_path = os.path.join(path, thumbnail_name)
      keras.preprocessing.image.save_img(thumbnail_path, thubnail)
      now_timestamp = datetime.datetime.now().timestamp()
      creation_image_timestamp = self.get_timestamp(image_name, image_path)
      data = { "name": image_name, "file": filename, "class": result[0], "score": result[1], "thumbnail": thumbnail_name, "timestamp": creation_image_timestamp, "ai_duration": now_timestamp - receive_timestamp, "latency": now_timestamp - creation_image_timestamp }
      with open(json_path, "w") as output:
        json.dump(data, output)
      if send_notification and self.on_new_picture:
        self.on_new_picture(image_path, data)
      self.logger.info("  Done processing {}, ai_duration {}, latency {}".format(filename, now_timestamp - receive_timestamp, now_timestamp - creation_image_timestamp))
    except:
      self.logger.exception("Exception with {}".format(image_path))

if __name__ == "__main__":
  model = model.Model()
  evaluater = DirectoryEvaluater(model, sys.argv[1])
  loop = asyncio.get_event_loop()
  loop.run_until_complete(evaluater.run())
  loop.stop()
  loop.close()
