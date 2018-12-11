from PIL import Image
import numpy as np
import time
import sys, os
RANDOM_IMAGE_SIZE = 480

if __name__ == "__main__":
    assert len(sys.argv) > 1, 'Destination folder not found!\nTry again with the following command:\n$ python test_mjpeg.py "images" # or "src/images"'

    out_folder = sys.argv[1]
    while True:
        img_name = 'img_%s.jpg' %  str(time.time())
        imarray = np.random.rand(RANDOM_IMAGE_SIZE, RANDOM_IMAGE_SIZE, 3) * 255
        im = Image.fromarray(imarray.astype('uint8')).convert('RGB')
        im.save(os.path.join(out_folder, img_name))
        print('Generated image @', img_name)
        time.sleep(0.04)
