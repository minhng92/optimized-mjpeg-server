#!/usr/bin/env python3
from importlib import import_module
import sys, os, time, yaml, datetime
from flask import Flask, Response
import _thread

import cv2

# 181113r
app = Flask(__name__)
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_NO_IMAGE_FILE_PATH = os.path.join(CURRENT_FOLDER, 'default.jpg')
IMAGE_FOLDER = os.path.join(CURRENT_FOLDER, 'images')
NUM_MAX_IMAGES_PER_CAM_FOLDER = 150
TIME_SLEEP_PER_SCAN_SECONDS = NUM_MAX_IMAGES_PER_CAM_FOLDER/30 # 5 seconds
LIVE_MJPEG_TEMPLATE = 'assets/live_mjpeg.html'

def get_time():
    return datetime.datetime.today().strftime('%Y%m%d%H%M%S')

# class with static methods
class GVCamManager():
    @staticmethod
    def get_latest_frame(cam_id):
        cam_folder = os.path.join(IMAGE_FOLDER, cam_id)
        if not os.path.isdir(cam_folder): # cam folder is not existed
            return None

        file_names = [f for f in os.listdir(cam_folder) if os.path.isfile(os.path.join(cam_folder, f))]
        file_names = sorted(file_names)

        if len(file_names) == 0:
            return None

        latest_img_path = os.path.join(cam_folder, file_names[-1])

        f = open(latest_img_path, 'rb').read()
        return f

img_manager = GVCamManager
def get_image_loop(cam_id):
    while True:
        time.sleep(0.03) # 30ms --> maximum performance: 30 FPS
        frame = img_manager.get_latest_frame(cam_id)
        frame = open(DEFAULT_NO_IMAGE_FILE_PATH, 'rb').read() if frame is None else frame

        if len(frame) == 0: # invalid image
            time.sleep(0.1)
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
@app.route('/mjpeg/<cam_id>', methods=['GET'])
def mjpeg(cam_id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(get_image_loop(cam_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def manage_image_files(image_dir):
    print('[%s][THREAD] Started thread "manage_image_files()" for auto-cleaning images' % get_time())
    # infinity loop
    while True:
        for root, dirnames, filenames in os.walk(image_dir):
            for d in dirnames:
                folder = os.path.join(root, d)
                file_names = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
                file_names = sorted(file_names)
                if len(file_names) > 2*NUM_MAX_IMAGES_PER_CAM_FOLDER:
                    del_list = file_names[:NUM_MAX_IMAGES_PER_CAM_FOLDER]
                    for img_del_path in del_list:
                        try:
                            os.remove(img_del_path)
                        except:
                            pass
                pass
            pass
        time.sleep(TIME_SLEEP_PER_SCAN_SECONDS)
        pass

def read_camera(camera_folder, camera_url):
    print('[%s][THREAD] Started thread "read_camera()" for reading camera: %s' % (get_time(), camera_url))

    stream = cv2.VideoCapture(camera_url)
    stream.set(cv2.CAP_PROP_BUFFERSIZE, 30)
    while True:
        ret, frame = stream.read()
        if ret:     # successful 
            timestamp = str(time.time())
            img_name = 'img_%s_%s.jpg' % (os.path.basename(camera_folder), timestamp)
            cv2.imwrite(os.path.join(camera_folder, img_name), frame)
        else:
            print('[%s][THREAD] Failed to read stream @ %s. Retry connecting in 10 seconds...' % (get_time(), camera_url))
            stream.release()
            time.sleep(10) # sleep 10 seconds
            stream.open(camera_url)        
        
        time.sleep(0.03) # 30 ms
    pass

if __name__ == '__main__':
    yaml_path = 'config.yaml'
    assert os.path.isfile(yaml_path)

    with open(yaml_path) as f:
        data_dict = yaml.safe_load(f)

    host = data_dict['mjpeg']['host']
    port = data_dict['mjpeg']['port']

    if 'app' in data_dict and 'logfile' in data_dict['app']:
        logfile = data_dict['app']['logfile']
        print('Logfile @', os.path.abspath(logfile))
        sys.stdout = open(logfile, 'a')
    print('[%s] Successfully read yaml config @' % get_time(), os.path.abspath(yaml_path))

    try:
        # docs: https://docs.python.org/3/library/_thread.html
        _thread.start_new_thread(manage_image_files, (IMAGE_FOLDER,))
        pass
    except Exception as e:
        print('[%s]'%get_time(), e)
        raise Exception("[Error] Unable to start thread for managing image files")

    if 'streams' in data_dict and data_dict['streams']['is_use']:
        stream_list = data_dict['streams']['stream_list']
        # parse stream list line-by-line
        # then start opencv to read streams
        stream_lines = stream_list.split()
        stream_lines = [s.strip() for s in stream_lines]
        
        list_camera_name = []
        list_camera_url = []
        for s_line in stream_lines:
            line_split = s_line.split(',')
            line_split = [s.strip() for s in line_split]

            camera_name, camera_url = line_split
            encoded_camera_name = camera_url.replace('/', '_').replace(':', '_').replace('.', '_')

            camera_folder = os.path.join(IMAGE_FOLDER, encoded_camera_name)
            os.makedirs(camera_folder, exist_ok=True)

            try:
                # docs: https://docs.python.org/3/library/_thread.html
                _thread.start_new_thread(read_camera, (camera_folder, camera_url,))
                pass
            except Exception as e:
                print('[%s]'%get_time(), e)
                raise Exception("[Error] Unable to start thread for reading camera @ %s" % camera_url)
        
            list_camera_name.append(camera_name)
            list_camera_url.append(encoded_camera_name)
        
        # load html template
        assert os.path.isfile(LIVE_MJPEG_TEMPLATE)
        assert len(list_camera_name) == len(list_camera_url)
        with open(LIVE_MJPEG_TEMPLATE, 'r') as f:
            html_template = f.read()

        camera_list_str = []
        for camera_name, camera_url in zip(list_camera_name, list_camera_url):
            html_cam_line = """
                <div class="camera_row" title="%(mjpeg_url)s">
                    <i class="fa fa-video-camera camera_color" aria-hidden="true"></i> &nbsp; %(camera_name)s
                </div>
            """ % {
                'mjpeg_url': 'http://%s:%d/mjpeg/%s' % (host, int(port), camera_url),
                'camera_name': camera_name,
            }
            html_cam_line = html_cam_line.strip()
            camera_list_str.append(html_cam_line)
        
        # save generated html
        camera_list_str = ''.join(camera_list_str)
        with open('_' + os.path.basename(LIVE_MJPEG_TEMPLATE), 'w') as f:
            f.write(html_template.replace('CAMERA_LINES_REPLACED_BY_PYTHON_CODE', camera_list_str))
        pass

    app.run(host=host, threaded=True, port=port)

    #while True:
    #    pass
