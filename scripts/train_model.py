#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import json
import pprint
import os
import PIL
import tensorflow as tf
import pathlib
import time

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import antichat_config

total_start_time = time.time()

data_dir = pathlib.Path(antichat_config.generated_images_path)

start_time = time.time()
image_count = len(list(data_dir.glob('*/*.jpg')))
print(image_count)

cat = list(data_dir.glob(antichat_config.cat_class_name + "/*." + antichat_config.picture_extension))
no_cat = list(data_dir.glob(antichat_config.no_cat_class_name + "/*." + antichat_config.picture_extension))

batch_size = 32

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split = antichat_config.validation_split,
  subset="training",
  seed=123,
  image_size=(antichat_config.img_height, antichat_config.img_width),
  batch_size=batch_size)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split = antichat_config.validation_split,
  subset="validation",
  seed=123,
  image_size=(antichat_config.img_height, antichat_config.img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
print(class_names)

for image_batch, labels_batch in train_ds:
  print(image_batch.shape)
  print(labels_batch.shape)
  break

loading_time = time.time() - start_time
start_time = time.time()

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixels values are now in `[0,1]`.
print(np.min(first_image), np.max(first_image))

num_classes = len(class_names)
processing_time = time.time() - start_time
start_time = time.time()

model = Sequential([
  layers.experimental.preprocessing.Rescaling(1./255, input_shape=(antichat_config.img_height, antichat_config.img_width, 3)),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
compiling_time = time.time() - start_time

model.summary()
stringlist = []
model.summary(print_fn=lambda x: stringlist.append(x))
model_summary = "\n".join(stringlist)

start_time = time.time()
epochs=10
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)
training_time = time.time() - start_time

model.save(antichat_config.model_path)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')

plt.savefig(os.path.join(antichat_config.website_training_path, "training.png"))

total_time = time.time() - total_start_time

total_picture_count = len(cat) + len(no_cat)
data = {
  "picture_count": {
    antichat_config.cat_class_name: len(cat),
    antichat_config.no_cat_class_name: len(no_cat),
    "traning": int(total_picture_count * (1 - antichat_config.validation_split)),
    "validation": int(total_picture_count * antichat_config.validation_split),
  },
  "image_size": [ antichat_config.img_width, antichat_config.img_height],
  "training_time": training_time,
  "loading_time": loading_time,
  "total_time": total_time,
  "model_summary": model_summary,
  "processing_time": processing_time,
  "compiling_time": compiling_time,
}
json_path = os.path.join(antichat_config.website_training_path, "data.json")
pprint.pprint(json_path)
pprint.pprint(data)
with open(json_path, "w") as output:
  json.dump(data, output)

