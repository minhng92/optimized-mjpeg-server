#!/usr/bin/env python
from importlib import import_module
import os, time
from flask import Flask, Response
import _thread

# 181113r
app = Flask(__name__)
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_NO_IMAGE_FILE_PATH = os.path.join(CURRENT_FOLDER, 'default.jpg')
IMAGE_FOLDER = os.path.join(CURRENT_FOLDER, 'images')
NUM_MAX_IMAGES_PER_CAM_FOLDER = 150
TIME_SLEEP_PER_SCAN_SECONDS = NUM_MAX_IMAGES_PER_CAM_FOLDER/30 # 5 seconds

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
    print('Thread is running... manage_image_files()')
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

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5050

    try:
        # docs: https://docs.python.org/3/library/_thread.html
        _thread.start_new_thread(manage_image_files, (IMAGE_FOLDER,)) # empty tuple (second param) means no passing parameter
        pass
    except Exception as e:
        print(e)
        raise Exception("[Error] Unable to start thread for managing image files")

    app.run(host=host, threaded=True, port=port)

    #while True:
    #    pass
