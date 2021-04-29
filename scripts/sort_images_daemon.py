#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import datetime
import json
import logging
import logging.handlers
import os
import pathlib
import pprint
import shutil
import sys
import time

import numpy as np
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import antichat_config
import logger_helper

class Deamon:
  def __init__(self, loop = None):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.model =  tf.keras.models.load_model(antichat_config.model_path)
    self.img_width = antichat_config.img_width
    self.img_height = antichat_config.img_height
    self.thub_width = 320
    self.should_drop_images = None
    self.thub_height = 180
    self.class_names =  antichat_config.class_names
    self.loop = loop or asyncio.get_event_loop()

  def load_thubnail(self, image_path):
    return keras.preprocessing.image.load_img(image_path, target_size=(self.thub_height, self.thub_width))

  def evaluate_image(self, image_path):
    image = keras.preprocessing.image.load_img(image_path, target_size=(self.img_height, self.img_width))
    img_array = keras.preprocessing.image.img_to_array(image)
    img_array = tf.expand_dims(img_array, 0) # Create a batch
    predictions = self.model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    return (self.class_names[np.argmax(score)], 100 * np.max(score))

  def get_timestamp(self, image_name, image_path):
    try:
      self.logger.info("get {} {}".format(image_name, image_path))
      image_datetime = image_name.split("_")[1]
      mydate = datetime.datetime.strptime(image_datetime, "%Y%m%d-%H%M%S")
      return datetime.datetime.timestamp(mydate)
    except:
      self.logger.exception("Exception with {} {}".format(image_name, image_path))
      fname = pathlib.Path(image_path)
      self.logger.info(pprint.pformat(fname.stat()))
      return fname.stat().st_mtime

  def drop_image(self, filename):
    self.logger.info("Drop {}".format(filename))
    image_name, image_ext = os.path.splitext(filename)
    image_path = os.path.join(antichat_config.ftp_snap_path, filename)
    self.logger.info("Remove {}".format(filename))
    os.remove(image_path)

  async def process_image(self, filename):
    self.logger.info("Process {}".format(filename))
    image_name, image_ext = os.path.splitext(filename)
    image_path = os.path.join(antichat_config.ftp_snap_path, filename)
    if not os.path.exists(image_path):
      self.logger.error("File doesn't exist {}".format(image_path))
    thumbnail_name = image_name + "_thub" + image_ext
    thubnail = self.load_thubnail(image_path)
    result = self.evaluate_image(image_path)
    json_path = os.path.join(antichat_config.website_incoming_path, image_name + ".json")
    with open(json_path, "w") as output:
      data = { "name": image_name, "file": filename, "class": result[0], "score": result[1], "thumbnail": thumbnail_name, "timestamp": self.get_timestamp(image_name, image_path) }
      json.dump(data, output)
    thumbnail_path = os.path.join(antichat_config.website_incoming_path, thumbnail_name)
    keras.preprocessing.image.save_img(thumbnail_path, thubnail)
    destination_path = os.path.join(antichat_config.website_incoming_path, filename)
    try:
      shutil.move(image_path, destination_path)
    except:
      self.logger.exception("Process image")
      pass
    self.logger.info("  Done processing {}".format(filename))

  async def run(self):
    self.loop.create_task(self.get_feedback())
    snap_dir = pathlib.Path(antichat_config.ftp_snap_path)
    while True:
      pending_filename = list(snap_dir.glob('*.jpg'))
      self.update_state()
      for filename in pending_filename:
        if self.should_drop_images:
          self.drop_image(os.path.basename(filename))
        else:
          self.loop.create_task(self.process_image(os.path.basename(filename)))
      await asyncio.sleep(60)

  async def get_feedback(self):
    website_path = pathlib.Path(antichat_config.website_incoming_path)
    flush_path = os.path.join(antichat_config.website_incoming_path, "flush")
    flush_image = False
    while True:
      flush_image = os.path.exists(flush_path)
      if flush_image:
        os.remove(flush_path)
      for json_name in list(website_path.glob('*.json')):
        json_path = os.path.join(antichat_config.website_incoming_path, json_name)
        with open(json_path, "r") as f:
            image_json = json.load(f)
            if flush_image or time.time() - image_json["timestamp"] > 60 * 60 *24:
              self.logger.info("{} {}".format(json_path, time.time() - image_json["timestamp"]))
              self.remove_image(json_path, image_json)
      await asyncio.sleep(60 * 5)

  def update_state(self):
    new_should_drop_images = os.path.exists(antichat_config.website_stop_file_path)
    if self.should_drop_images != new_should_drop_images:
      self.should_drop_images = new_should_drop_images
      self.logger.info("Drop image {}".format(self.should_drop_images))

  def remove_image(self, json_path, image_json):
    action = None
    action_path = os.path.join(antichat_config.website_incoming_path, image_json["name"] + ".action")
    thumbnail_path = os.path.join(antichat_config.website_incoming_path, image_json["thumbnail"])
    image_path = os.path.join(antichat_config.website_incoming_path, image_json["file"])
    if os.path.exists(action_path):
      with open(action_path, "r") as f:
        action = f.read()
    self.logger.info(image_json)
    self.logger.info(action)
    if action in self.class_names:
      destination_path = os.path.join(antichat_config.extra_images_path, action)
      if os.path.exists(os.path.join(destination_path, image_json["file"])):
        os.remove(image_path)
      else:
        shutil.move(image_path, destination_path)
      self.logger.info(action)
    else:
      os.remove(image_path)
    os.remove(json_path)
    if action is not None:
      os.remove(action_path)
    os.remove(thumbnail_path)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  daemon = Deamon(loop)
  loop.create_task(daemon.run())
  loop.run_forever()
