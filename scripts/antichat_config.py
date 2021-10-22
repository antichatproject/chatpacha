#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pprint

config_file_path = os.path.abspath(__file__)
config_dir_path = os.path.dirname(config_file_path)
antichat_dir_path = os.path.dirname(config_dir_path)

img_width = 180
img_height = 180
cat_class_name = "chat"
no_cat_class_name = "pas_chat"
class_names = [ cat_class_name, no_cat_class_name ]
validation_split = .01
model_path = os.path.join(antichat_dir_path, "antichat_model")
data_path = os.path.join(antichat_dir_path, "data")
generated_images_path = os.path.join(data_path, "generated")
classified_images_path = os.path.join(data_path, "classified")
picture_extension = "jpg"

# Notification
cat_detection_threshold = .80
cat_notification_delay = 60 * 2
cat_notification_limit_count = 6
cat_notification_limit_decount_period = 60 * 5

log_path = "/var/log/antichat"

ftp_snap_path = os.path.normpath(os.path.join(antichat_dir_path, "..", "cam", "FI9900P_00626E6778C6", "snap"))

website_path = os.path.join(antichat_dir_path, "website")
website_images_path = os.path.join(website_path, "images")
website_stop_file_path = os.path.join(website_images_path, "stop")
website_incoming_path = os.path.join(website_images_path, "incoming")
website_test_path = os.path.join(website_images_path, "tests")
website_training_path = os.path.join(website_path, "training")

if __name__ == "__main__":
  path_to_test = {
    "model_path": model_path,
    "generated_images_path": generated_images_path,
    "classified_images_path": classified_images_path,
    "data_path": data_path,
    "ftp_snap_path": ftp_snap_path,
    "keep_video_path": keep_video_path,
    "website_path": website_path,
    "website_images_path": website_images_path,
    "website_test_path": website_test_path,
  }
  for path_name, path in path_to_test.items():
    if os.path.exists(path):
      print("{}: OK".format(path_name))
    else:
      print("{}: NOT OK, {}".format(path_name, path))
