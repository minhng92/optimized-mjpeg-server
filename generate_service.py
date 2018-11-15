import os
import getpass

SERVICE_CONTENT_TEMPLATE = """
[Unit]
Description=MJPEG Server
[Service]
User=%(user)s
# The configuration file application.properties should be here:
#change this to your workspace
WorkingDirectory=%(src_dir)s
Environment=PATH=%(env)s
#path to executable. 
#executable is a bash script which calls jar file
ExecStart=%(src_dir)s/main.py
SuccessExitStatus=0
TimeoutStopSec=10
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
"""

SOURCE_ABS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src')
assert os.path.isdir(SOURCE_ABS_DIR)

USER = getpass.getuser()

with open('mjpeg_optimized.service', 'w') as f:
    f.write(SERVICE_CONTENT_TEMPLATE % {
        'user': USER,
        'src_dir': SOURCE_ABS_DIR,
        'env': os.environ['PATH']
    })

print('Done generating "mjpeg_optimized.service"! To install mjpeg service, run $ sh install.sh')
