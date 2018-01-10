import requests
import cv2
import numpy as np

def main():
    url = 'http://192.168.1.1/videostream.cgi'
    user = 'admin'
    pwd = ''
    auth = requests.auth.HTTPDigestAuth(user, pwd)
    r = requests.get(url, auth=auth, stream=True, timeout=9)

    for img in get_frame_bytes(r):
        mat = get_frame_mat2(img)
        cv2.imshow('img', mat)
        if cv2.waitKey(1) == 27:
            break

    return

def get_frame_bytes(r):
    buf = b''
    for chunk in r.iter_content(chunk_size=1024):
        buf += chunk
        beg = buf.find(b'\xff\xd8')
        end = buf.find(b'\xff\xd9')
        if beg != -1 and end != -1 and beg < end:
            img = buf[beg:end+2]
            buf = buf[end+2:]

            yield img

def get_frame_mat(img):
    mat = cv2.imdecode(np.fromstring(img, dtype=np.uint8), cv2.IMREAD_COLOR)

    return mat

import io
from PIL import Image
def get_frame_mat2(img):
    mat = np.asarray(Image.open(io.BytesIO(img)))

    return mat

main()
