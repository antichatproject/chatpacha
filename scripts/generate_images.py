#!/usr/bin/env python3
# create_images.py <dir with mkv list> <destination> [ <scale> ]

import os
import pprint
import subprocess
import sys

import antichat_config

def create_thumbnail(origin, filename, file_format, destination = None):
  if destination == None:
    destination = os.path.join(origin, "thumbnails")
  if not os.path.exists(destination):
    os.makedirs(destination)
  copy_image(origin, filename, destination, file_format, "scale=320:-1")

def copy_image(origin, filename, destination, file_format, scale):
  image_name = os.path.splitext(filename)[0]
  input_filename = os.path.join(origin, filename)
  output_filename = os.path.join(destination, image_name + "." + file_format)
  if os.path.exists(output_filename):
    print("Already done " + output_filename)
    return False
  command = [ "ffmpeg", "-hide_banner", "-i", input_filename ]
  vf_args = []
  if scale is not None:
    vf_args = vf_args + [ scale ]
  if len(vf_args) > 0:
    command = command + [ "-vf", ",".join(vf_args) ]
  command.append(output_filename)
  print("Copy " + input_filename + " " + output_filename + ", scale: " + pprint.pformat(scale))
  subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  print(output_filename)
  if not os.path.exists(output_filename):
    print(output_filename + " doesn't exist.")
    exit(-1)
  return True

def create_dir_if_needed(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)

def create_thumbnails(origin, class_names, destination, file_format, scale = None):
  for class_name in class_names:
    origin_class_path = os.path.join(origin, class_name)
    destination_class_path = os.path.join(destination, class_name)
    create_dir_if_needed(destination_class_path)
    for filename in os.listdir(origin_class_path):
      image_path = os.path.join(origin_class_path, filename)
      create_thumbnail(origin_class_path, filename, antichat_config.picture_extension, destination_class_path)

if __name__ == "__main__":
  image_source = antichat_config.classified_images_path
  thumbnail_destination = antichat_config.classified_thumbnails_path
  if False:
    scale = "scale=320:-1"
  else:
    scale = None
  file_format = antichat_config.picture_extension
  create_dir_if_needed(os.path.join(thumbnail_destination, antichat_config.cat_class_name))
  create_dir_if_needed(os.path.join(thumbnail_destination, antichat_config.no_cat_class_name))
  create_thumbnails(antichat_config.classified_images_path, antichat_config.class_names, thumbnail_destination, file_format, scale)
