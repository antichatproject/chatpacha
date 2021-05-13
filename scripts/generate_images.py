#!/usr/bin/env python3
# create_images.py <dir with mkv list> <destination> [ <scale> ]

import os
import pprint
import subprocess
import sys

import antichat_config

def create_thumbnail(origin, filename, file_format):
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

def copy_images(origin, destination, file_format, scale = None):
  for filename in os.listdir(origin):
    copy_image(origin, filename, destination, file_format, scale)
    create_thumbnail(destination, filename, file_format)

def copy_all_class_images(origin, destination, file_format, scale = None):
  for filename in os.listdir(origin):
    copy_images(os.path.join(origin, filename), os.path.join(destination, filename), file_format, scale)

def create_dir_if_needed(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)

if __name__ == "__main__":
  image_source = antichat_config.classified_images_path
  destination = antichat_config.generated_images_path
  if False:
    scale = "scale=320:-1"
  else:
    scale = None
  file_format = antichat_config.picture_extension
  create_dir_if_needed(os.path.join(destination, antichat_config.cat_class_name))
  create_dir_if_needed(os.path.join(destination, antichat_config.no_cat_class_name))
  copy_all_class_images(image_source, destination, file_format, scale)
