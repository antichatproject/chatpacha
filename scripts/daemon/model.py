#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

class Model:
  def __init__(self):
    self.logger = logger_helper.get_logger(self.__class__.__name__)
    self.img_width = antichat_config.img_width
    self.img_height = antichat_config.img_height
    self.class_names =  antichat_config.class_names
    self.load()

  def load(self):
    self.logger.info("Load")
    self.model =  tf.keras.models.load_model(antichat_config.model_path)

  def evaluate(self, image_path):
    image = keras.preprocessing.image.load_img(image_path, target_size=(self.img_height, self.img_width))
    img_array = keras.preprocessing.image.img_to_array(image)
    img_array = tf.expand_dims(img_array, 0) # Create a batch
    predictions = self.model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    result = (self.class_names[np.argmax(score)], float(np.max(score)))
    self.logger.info("{} {} {}".format(image_path, result[0], int(result[1] * 100)))
    return result

if __name__ == "__main__":
  model = Model()
  result = model.evaluate(sys.argv[1])
  print(sys.argv[1])
  pprint.pprint(result)
