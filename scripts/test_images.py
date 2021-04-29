#!/usr/bin/env python3
# test_images.py <dir>

#import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf
import pathlib
import pprint
import sys
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import antichat_config

def test_image(model, image_path, img_width, img_height, class_names):
  img = keras.preprocessing.image.load_img(image_path, target_size=(img_height, img_width))
  img_array = keras.preprocessing.image.img_to_array(img)
  img_array = tf.expand_dims(img_array, 0) # Create a batch
  predictions = model.predict(img_array)
  score = tf.nn.softmax(predictions[0])
  #print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))
  return (class_names[np.argmax(score)], 100 * np.max(score))

model = tf.keras.models.load_model(antichat_config.model_path)
test_dir = pathlib.Path(sys.argv[1])
chat_test = sorted(list(test_dir.glob('*.jpg')))
for image_path in chat_test:
  class_name, score = test_image(model, image_path, antichat_config.img_width, antichat_config.img_height, antichat_config.class_names)
  pprint.pprint([class_name, int(score), os.path.basename(image_path)])
