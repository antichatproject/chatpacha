#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import datetime
import pprint
import os
import subprocess
import sys
import time

sys.path.append('..')

import antichat_config
import logger_helper
import model

class VideoUploader:
  def __init__(self, antichat_config, loop = None):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.antichat_config = antichat_config
    self.loop = loop or asyncio.get_event_loop()
    self.upload_tool_path = antichat_config.antichat_dir_path + "/../youtube/upload.sh"
    self.video_sent = {}
    self.video_to_send = {}

  def video_path_for_datetime(self, mydatetime):
    filename = mydatetime.strftime("MDalarm_%Y%m%d_%H%M%S.mkv")
    path = os.path.join(antichat_config.ftp_record_path, filename)
    exists = os.path.exists(path)
    self.logger.info("Test video at path {}: {}".format(path, exists))
    if exists:
      return path
    return None

  def video_path_for_timestamp(self, mytimestamp):
    for i in range(4):
      mydatetime = datetime.datetime.fromtimestamp(mytimestamp + i)
      path = self.video_path_for_datetime(mydatetime)
      if path is not None:
        return path
    for i in range(120):
      mydatetime = datetime.datetime.fromtimestamp(mytimestamp - i)
      path = self.video_path_for_datetime(mydatetime)
      if path is not None:
        return path
    return None

  def upload(self, data):
    self.loop.create_task(self.upload_task(data))
  
  async def upload_task(self, data):
    await asyncio.sleep(60 * 5)
    video_path = self.video_path_for_timestamp(data["timestamp"])
    if video_path is None:
      self.logger.error("No video {}".format(pprint.pformat(data)))
    elif video_path in self.video_sent:
      self.logger.error("Video already sent {}".format(video_path))
    elif video_path in self.video_to_send:
      self.logger.info("Video already scheduled {}".format(video_path))
    else:
      self.video_to_send[video_path] = data

  async def run(self):
    self.logger.info("Run")
    while True:
      await asyncio.sleep(60)
      for video_path in self.video_to_send.copy():
        try:
          data = self.video_to_send[video_path]
          self.logger.info("Process video {}".format(video_path))
          if video_path in self.video_sent:
            del self.video_to_send[video_path]
            self.logger.error("Video already sent {}".format(video_path))
            continue
          last_modification = os.path.getmtime(video_path)
          if time.time() - last_modification < 60:
            self.logger.info("video not ready {}".format(video_path))
            continue
          del self.video_to_send[video_path]
          self.video_sent[video_path] = True
          thumbnail_path = os.path.join(antichat_config.website_incoming_path, data["file"])
          a = subprocess.run([self.upload_tool_path, video_path, "", thumbnail_path], capture_output=True)
          if a.returncode != 0:
            self.logger.error("Error to send video {}\ncode: {}\n{}\n{}".format(video_path, a.returncode, a.stdout, a.stderr))
          else:
            self.logger.info("video sent {} {}\ncode: {}\n{}".format(video_path, thumbnail_path, a.returncode, a.stdout))
        except:
          self.logger.exception("Exception with {}".format(video_path))
    self.logger.info("While done")
