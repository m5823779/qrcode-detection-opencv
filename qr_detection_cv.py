import cv2
import time
import numpy as np
import webbrowser
from mss.windows import MSS as mss
from screeninfo import get_monitors


class mouse_event():
    def __init__(self):
        self.pos = None
        self.click = False

    def getCoord(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.click = True
        else:
            self.click = False
        self.pos = (x, y)

    def pass_mouse_event(self):
        return self.click, self.pos


main_screen = get_monitors()[0]
screen = get_monitors()[1]

sct = mss()
mouse_rec = mouse_event()

cv2.namedWindow('Window', cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow('Window', 0, 0)
cv2.setWindowProperty('Window', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback('Window', mouse_rec.getCoord)

qrcode_detector = cv2.QRCodeDetector()
scaling_size = 2

while True:
    time_start = time.time()

    user_click, mouse_cord = mouse_rec.pass_mouse_event()
    sct_img = sct.grab(sct.monitors[2])
    image = np.array(sct_img)
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    input = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    input = cv2.resize(input, (int(image.shape[1] // scaling_size), int(image.shape[0] // scaling_size)))
    ret, *results = qrcode_detector.detectMulti(input)

    transformation_matrix = np.array([[scaling_size, 0], [0, scaling_size]])

    if results[0] is not None:
        for points in results[0]:

            points = points.dot(transformation_matrix)

            points = points.astype("int")
            if mouse_cord is not None and user_click and \
                    points[0, 0] <= mouse_cord[0] <= points[2, 0] and points[0, 1] <= mouse_cord[1] <= points[2, 1]:
                crop_qr = image[points[0, 1]:points[2, 1], points[0, 0]:points[2, 0]]

                # qr code decode
                h, w, _ = crop_qr.shape
                pose = np.array([[[0, 0], [w, 0], [w, h], [0, h]]])
                url = str(qrcode_detector.decode(crop_qr, pose)[0])

                if 'http' not in str(url):
                    url = "Not URL link"
                    cv2.putText(image, url, (points[0, 0], points[0, 1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                else:
                    webbrowser.open_new_tab(url)

            elif mouse_cord is not None and not user_click and \
                    points[0, 0] <= mouse_cord[0] <= points[2, 0] and points[0, 1] <= mouse_cord[1] <= points[2, 1]:
                draw_box_leftyop = (max(points[0, 0] - 10, 0), max(points[0, 1] - 10, 0))
                draw_box_rightbottom = (min(points[2, 0] + 10, main_screen.width), min(points[2, 1] + 10, main_screen.height))
                cv2.rectangle(image, draw_box_leftyop, draw_box_rightbottom, (0, 255, 0), 3)
                cv2.putText(image, "click to search", (points[0, 0], points[0, 1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


            else:
                draw_box_leftyop = (max(points[0, 0] - 10, 0), max(points[0, 1] - 10, 0))
                draw_box_rightbottom = (min(points[2, 0] + 10, main_screen.width), min(points[2, 1] + 10, main_screen.height))
                cv2.rectangle(image, draw_box_leftyop, draw_box_rightbottom, (0, 0, 255), 2)

    print('framerate: {:.3f} fps'.format( 1 / (time.time() - time_start) ), end='\r')
    time_start = time.time()
    cv2.imshow("Window", image)
    cv2.waitKey(1)