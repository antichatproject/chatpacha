#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aionotify
import asyncio
import os
import pathlib
import pprint
import shutil
import sys

sys.path.append('..')

import logger_helper

class FileMover:
  def __init__(self, origin_path, destination_path, loop = None):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.origin_path = origin_path
    self.destination_path = destination_path
    self.loop = loop or asyncio.get_event_loop()
    self.watcher = aionotify.Watcher()
    self.watcher.watch(path = self.origin_path, flags = aionotify.Flags.MOVED_TO | aionotify.Flags.CREATE)
    self.drop_files = False
    self.valid_extensions = [ ".jpg" ]

  async def run(self):
    self.logger.info("Run {} => {}".format(self.origin_path, self.destination_path))
    await self.watcher.setup(self.loop)
    snap_dir = pathlib.Path(self.origin_path)
    all_file_paths = list(snap_dir.glob('*'))
    for file_path in all_file_paths:
      self.loop.create_task(self.process_file(file_path))
    while True:
      event = await self.watcher.get_event()
      self.logger.debug("Event {}".format(pprint.pformat(event)))
      file_path = os.path.join(self.origin_path, event.name)
      self.logger.debug("Start task for {}".format(file_path))
      self.loop.create_task(self.process_file(file_path))
    self.watcher.close()

  async def process_file(self, file_path):
    _, extension = os.path.splitext(file_path)
    if not extension in self.valid_extensions:
      return False
    filename = os.path.basename(file_path)
    if not os.path.exists(file_path):
      self.logger.info("Disappeared {}".format(filename))
      return False
    if self.drop_files:
      self.logger.info("Remove {}".format(filename))
      os.remove(file_path)
      return True
    self.logger.debug("Need to move {}".format(file_path))
    full_destination_path = os.path.join(self.destination_path, filename)
    if os.path.exists(full_destination_path):
      self.logger.error("Exist {}".format(full_destination_path))
      os.remove(full_destination_path)
    self.logger.info("Move {} => {}".format(file_path, self.destination_path))
    shutil.move(str(file_path), str(self.destination_path))
    return True

if __name__ == "__main__":
  mover = FileMover(sys.argv[1], sys.argv[2])
  loop = asyncio.get_event_loop()
  loop.run_until_complete(mover.run())
  loop.stop()
  loop.close()
