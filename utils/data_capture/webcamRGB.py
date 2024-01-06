import os

import cv2

from datetime import datetime

print(cv2.getBuildInformation())

# Set up folder to save new capture data in
now = datetime.now()
date_time = now.strftime("%Y%m%d%H%M")
dirname = "webcamRGB" + date_time
filepath = os.path.join(os.getcwd(),dirname)
os.mkdir(filepath)
print("saving images to: " + filepath)
os.chdir(filepath)

cam_port = 0
camera = cv2.VideoCapture(cam_port)

count = 1
first = True

# Set up display
window_name = "Webcam Capture"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while True:
    result, img = camera.read()
    img = img[0:480, 0:480]

    if result:
        #resize window to image
        if first:
            (height, width, _) = img.shape
            cv2.resizeWindow(window_name, width * 2, height * 2)
            first == False
        
        #show image in window
        cv2.imshow(window_name, img)

        name = str(count) + ".png"#note--change filetype to option
        cv2.imwrite(name, img)
        count+=1

        # Process key events.
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

        # Check if the window has been closed manually.
        if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
            break

cv2.destroyWindow(window_name)