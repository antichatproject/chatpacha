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

sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "daemon"))

import antichat_config
import directory_evaluater
import file_mover
import logger_helper
import model
import mqtt

class Deamon:
  def __init__(self, loop = None):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.loop = loop or asyncio.get_event_loop()
    self.model =  model.Model()
    self.incoming_file_mover = file_mover.FileMover(antichat_config.ftp_snap_path, antichat_config.website_incoming_path)
    self.incoming_directory_evaluater = directory_evaluater.DirectoryEvaluater(self.model, antichat_config.website_incoming_path)
    self.incoming_directory_evaluater.on_new_picture = self.on_new_picture
    self.test_directory_evaluater = directory_evaluater.DirectoryEvaluater(self.model, antichat_config.website_test_path)
    self.mqtt = mqtt.MQTT()

  async def run(self):
    self.loop.create_task(self.incoming_directory_evaluater.run())
    self.loop.create_task(self.test_directory_evaluater.run())
    self.loop.create_task(self.incoming_file_mover.run())
    self.loop.create_task(self.mqtt.run())
    self.loop.create_task(self.get_feedback())

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
              self.remove_incoming_image(json_path, image_json)
      await asyncio.sleep(60 * 5)

  def remove_incoming_image(self, json_path, image_json):
    action = None
    action_path = os.path.join(antichat_config.website_incoming_path, image_json["name"] + ".action")
    thumbnail_path = os.path.join(antichat_config.website_incoming_path, image_json["thumbnail"])
    image_path = os.path.join(antichat_config.website_incoming_path, image_json["file"])
    if os.path.exists(action_path):
      with open(action_path, "r") as f:
        action = f.read()
    self.logger.info(image_json)
    self.logger.info(action)
    if action in antichat_config.class_names:
      destination_path = os.path.join(antichat_config.classified_images_path, action)
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

  def on_new_picture(self, image_path, data):
    try:
      if data["class"] == antichat_config.cat_class_name and data["score"] > antichat_config.cat_detection_threshold:
        self.mqtt.cat_detected()
    except:
      self.logger.exception("Send cat mqtt fail")

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  daemon = Deamon(loop)
  loop.create_task(daemon.run())
  loop.run_forever()
