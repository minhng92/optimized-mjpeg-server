#!/bin/bash

# Note: run with root permission
# Created symlink from /etc/systemd/system/multi-user.target.wants/ivas.service to /etc/systemd/system/ivas.service.
sudo chmod +x src/main.py
sudo chmod 777 src/default.jpg
sudo chmod 777 src/config.yaml
sudo chmod -R 777 src/images

python generate_service.py
sudo cp mjpeg_optimized.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable mjpeg_optimized.service
sudo systemctl start mjpeg_optimized
sudo systemctl status mjpeg_optimized
