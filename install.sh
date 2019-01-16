#!/bin/bash

# Note: run with root permission
# Created symlink from /etc/systemd/system/multi-user.target.wants/ivas.service to /etc/systemd/system/ivas.service.
chmod +x src/main.py
chmod 777 src/default.jpg
chmod 777 src/config.yaml
chmod -R 777 src/images

python generate_service.py
cp mjpeg_optimized.service /etc/systemd/system
systemctl daemon-reload
systemctl enable mjpeg_optimized.service
systemctl start mjpeg_optimized
systemctl status mjpeg_optimized
