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

def create_snapshots(video_path, destination, scale = None, file_format = "jpg", sort_with_category = False):
  zero_padding = 6
  video_name = os.path.splitext(os.path.basename(video_path))[0]
  cat_video = video_name.startswith("chat_")
  if sort_with_category:
    if cat_video:
      snapshot_path = os.path.join(destination, "chat")
    else:
      snapshot_path = os.path.join(destination, "pas_chat")
  else:
    snapshot_path = os.path.join(destination, video_name)
  if not os.path.exists(snapshot_path):
    os.makedirs(snapshot_path)
  if os.path.exists(os.path.join(snapshot_path, video_name + "-" + ("0" * (zero_padding - 1)) + "1." + file_format)):
    print("  Already done")
    return
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

def copy_images(origin, destination, scale = None, file_format = "jpg"):
  for filename in os.listdir(origin):
    image_name = os.path.splitext(filename)[0]
    input_filename = os.path.join(origin, filename)
    command = [ "ffmpeg", "-hide_banner", "-i", input_filename ]
    vf_args = []
    if scale is not None:
      vf_args = vf_args + [ scale ]
    if len(vf_args) > 0:
      command = command + [ "-vf", ",".join(vf_args) ]
    output_filename = os.path.join(destination, image_name + "." + file_format)
    if os.path.exists(output_filename):
      print("Already done " + output_filename)
      continue
    command.append(output_filename)
    print("Copy " + input_filename + " " + output_filename)
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def copy_all_class_images(origin, destination, scale = None, file_format = "jpg"):
  for filename in os.listdir(origin):
    copy_images(os.path.join(origin, filename), os.path.join(destination, filename), scale, file_format)

if __name__ == "__main__":
  video_source = antichat_config.keep_video_path
  image_source = antichat_config.extra_images_path
  destination = antichat_config.generated_images_path
  if False:
    scale = "scale=320:-1"
    file_format = "png"
  else:
    scale = None
    file_format = "jpg"
  videos = get_all_videos(video_source)
  index = 0
  count = len(videos)
  for video in videos:
    video_name = os.path.basename(video)
    print(str(index) + "/" + str(count) + " " + video_name)
    create_snapshots(video, destination, scale, file_format, True)
    index += 1
  copy_all_class_images(image_source, destination, scale, file_format)

