# TODO

* Update test script
* Write usage in README.MD

# INSTALLATION

```
$ pip3 install -r requirements.txt
```

# INSTALL MJPEG SERVER AS A SERVICE

```
$ sudo sh install.sh

Check failed service message:
$ journalctl -u mjpeg_optimized.service -e

Check mjpeg service status:
$ sudo service mjpeg_optimized status

Restart mjpeg service:
$ sudo service mjpeg_optimized restart

Stop mjpeg service:
$ sudo service mjpeg_optimized stop
```

# USAGE

Configure `src/config.yaml` before starting mjpeg server.

```
$ cd src
$ python3 main.py
```
