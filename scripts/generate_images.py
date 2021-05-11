#!/usr/bin/env python3
# create_images.py <dir with mkv list> <destination> [ <scale> ]

import os
import pprint
import subprocess
import sys

import antichat_config

def get_all_videos(source):
  list = []
  for file_name in os.listdir(source):
    full_path = os.path.join(source, file_name)
    if not os.path.isfile(full_path) or os.path.splitext(full_path)[1] != ".mkv":
      continue
    list.append(full_path)
  return list

def create_snapshots(video_path, destination, file_format, scale = None, sort_with_category = False):
  zero_padding = 6
  video_name = os.path.splitext(os.path.basename(video_path))[0]
  cat_video = video_name.startswith("chat_")
  if sort_with_category:
    if cat_video:
      snapshot_path = os.path.join(destination, antichat_config.cat_class_name)
    else:
      snapshot_path = os.path.join(destination, antichat_config.no_cat_class_name)
  else:
    snapshot_path = os.path.join(destination, video_name)
  if not os.path.exists(snapshot_path):
    os.makedirs(snapshot_path)
  if os.path.exists(os.path.join(snapshot_path, video_name + "-" + ("0" * (zero_padding - 1)) + "1." + file_format)):
    print("  Already done")
  else:
    command = ["ffmpeg", "-hide_banner", "-i", video_path]
    time_code_path = os.path.splitext(video_path)[0] + ".txt"
    vf_args = []
    if scale is not None:
      vf_args = vf_args + [ scale ]
    if os.path.isfile(time_code_path):
      vf_args = vf_args + [ "fps=5"]
      f = open(time_code_path, "r")
      time_code = f.readline().strip().split(";")
      info = "From: "
      if time_code[0] != "":
        command.append("-ss")
        command.append(time_code[0]);
        info += time_code[0]
      else:
        info += "begining"
      if len(time_code) > 1 and time_code[1] != "":
        command.append("-t")
        command.append(time_code[1]);
        info += " to " + time_code[1]
    elif cat_video:
      print("  Cat without timecode file")
      return
    else:
      vf_args = vf_args + [ "fps=1"]
      info = "Process full video (no cat)"
    print("  " + info)
    command = command + [ "-vf", ",".join(vf_args) ]
    command.append(os.path.join(snapshot_path, video_name + "-%0" + str(zero_padding) + "d." + file_format))
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  counter = 1
  while True:
    number = ("0" * zero_padding) + str(counter)
    snapshot_filename = video_name + "-" + number[-zero_padding:] + "." + file_format
    print("Create thumbnail: " + snapshot_filename)
    if not os.path.exists(os.path.join(snapshot_path, snapshot_filename)):
      return
    create_thumbnail(snapshot_path, snapshot_filename, file_format)
    counter += 1

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
  video_source = antichat_config.keep_video_path
  image_source = antichat_config.classified_images_path
  destination = antichat_config.generated_images_path
  if False:
    scale = "scale=320:-1"
  else:
    scale = None
  file_format = antichat_config.picture_extension
  create_dir_if_needed(os.path.join(destination, antichat_config.cat_class_name))
  create_dir_if_needed(os.path.join(destination, antichat_config.no_cat_class_name))
  videos = get_all_videos(video_source)
  index = 0
  count = len(videos)
  for video in videos:
    break
    video_name = os.path.basename(video)
    print(str(index) + "/" + str(count) + " " + video_name)
    create_snapshots(video, destination, file_format, scale, True)
    index += 1
  copy_all_class_images(image_source, destination, file_format, scale)
