#!/bin/bash

# Note: run with root permission
# Created symlink from /etc/systemd/system/multi-user.target.wants/ivas.service to /etc/systemd/system/ivas.service.
chmod +x src/main.py
cp mjpeg_optimized.service /etc/systemd/system
systemctl daemon-reload
systemctl enable mjpeg_optimized.service
systemctl start mjpeg_optimized
systemctl status mjpeg_optimized
