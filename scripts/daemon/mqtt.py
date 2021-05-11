#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import asyncio
import pprint
import time
import gmqtt
import sys

sys.path.append('..')

import antichat_config
import logger_helper

ENABLED_TOPIC = "antichat/enabled"
STATE_TOPIC = "antichat/state"
CAT_DETECTED_TOPIC = "antichat/cat"

class MQTT:
  def __init__(self, server = "127.0.0.1", loop = None):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.loop = loop or asyncio.get_event_loop()
    self.server = server
    self.client = gmqtt.Client("antichat")
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.on_disconnect = self.on_disconnect
    self.client.on_subscribe = self.on_subscribe
    self.on_enabled = None
    self.last_cat_notification = None
    self.cat_notification_counter = 0
    self.enabled = True

  def on_connect(self, client, flags, rc, properties):
    self.publish_state()
    self.client.subscribe(ENABLED_TOPIC)

  def on_message(self, client, topic, payload, qos, properties):
    try:
      self.logger.info("On message {} {}".format(pprint.pformat(topic), pprint.pformat(payload)))
      payload_string = payload.decode('utf-8')
      if topic == ENABLED_TOPIC:
        self.enabled = payload_string != "0"
        if self.on_enabled:
          self.on_enabled(self.enabled)
        self.publish_state()
    except:
      self.logger.exception("On message {} {}".format(pprint.pformat(topic), pprint.pformat(payload)))

  def on_disconnect(self, client, packet, exc=None):
    pass

  def on_subscribe(self, client, mid, qos, properties):
    pass

  def publish_state(self):
    state_string = "1" if self.enabled else "0"
    self.logger.info("Publish state {}, {}".format(self.enabled, state_string))
    self.client.publish(STATE_TOPIC, state_string, qos = 1, retain = True)

  async def run(self):
    while True:
      try:
        self.logger.error("Try to connect")
        await self.client.connect(self.server)
        break
      except:
        self.logger.exception("Fail to connect")
      try:
        await asyncio.sleep(2)
      except:
        break

  async def decrease_cat_notification_counter(self):
    await asyncio.sleep(antichat_config.cat_notification_limit_decount_period)
    if self.cat_notification_counter == 0:
      self.logger.error("Already cat_notification_counter 0")
      return
    self.cat_notification_counter -= 1
    if self.cat_notification_counter > 0:
      self.loop.create_task(self.decrease_cat_notification_counter())
    else:
      self.logger.error("cat_notification_counter 0")

  def cat_detected(self):
    try:
      if not self.enabled:
        return
      if (self.last_cat_notification is None or (time.time() - self.last_cat_notification > antichat_config.cat_notification_delay)) and self.cat_notification_counter < antichat_config.cat_notification_limit_count:
        self.logger.info("Send cat notification {}".format(self.cat_notification_counter))
        self.last_cat_notification = time.time()
        self.client.publish(CAT_DETECTED_TOPIC, str(time.time()), qos = 1)
        if self.cat_notification_counter == 0:
          self.loop.create_task(self.decrease_cat_notification_counter())
        self.cat_notification_counter += 1
    except:
      self.logger.exception("Fail to send message")
