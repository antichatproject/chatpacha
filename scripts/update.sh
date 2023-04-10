#!/usr/bin/env bash

LOCAL_DIR=`dirname "$0"`
"${LOCAL_DIR}/generate_images.py"
"${LOCAL_DIR}/train_model.py"
systemctl restart jet-antichat.service
