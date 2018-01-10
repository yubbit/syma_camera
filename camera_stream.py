from multiprocessing import Process, Event
from multiprocessing.sharedctypes import Array
from datetime import datetime
import requests
import cv2
import numpy as np

def main():
    url = 'http://192.168.1.1/videostream.cgi'
    user = 'admin'
    pwd = ''
    auth = requests.auth.HTTPDigestAuth(user, pwd)
    r = requests.get(url, auth=auth, stream=True, timeout=9)

    h = 480
    w = 640
    ch = 3
    img = Array('B', np.zeros(h * w * ch, dtype=np.uint8))
    arr = np.frombuffer(img.get_obj(), dtype=np.uint8)
    img_lock = Event()

    stream = Process(target=stream_video, args=(r, img, img_lock))
    stream.start()

    fps = 60.0
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter('output.mp4', fourcc, fps, (640, 480))

    prev = datetime.now()
    time_interval = 1.0 / fps

    while True:
        now = td_to_ms(datetime.now() - prev)
        if now >= time_interval:
            if not img_lock.is_set():
                img_lock.set()
                frame = arr.reshape((h, w, ch))
                img_lock.clear()
                cv2.imshow('camera', frame)
                out.write(frame)
                prev = datetime.now()
                time_interval = (2.0 / fps) - now

        if cv2.waitKey(1) == 27:
            break

    stream.terminate()
    out.release()
    cv2.destroyAllWindows()

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

    return


def get_frame_mat(img):
    mat = cv2.imdecode(np.fromstring(img, dtype=np.uint8), cv2.IMREAD_COLOR)

    return mat


def stream_video(r, img, img_lock):
    arr = np.frombuffer(img.get_obj(), dtype=np.uint8)
    for i in get_frame_bytes(r):
        if not img_lock.is_set():
            img_lock.set()
            arr[:] = get_frame_mat(i).flatten()
            img_lock.clear()

    return


def td_to_ms(td):
    return td.seconds + td.microseconds / 1000000


if __name__ == '__main__':
    main()

