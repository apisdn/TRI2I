#!/usr/bin/env python3
# Copyright 2021 Seek Thermal Inc.
#
# Original author: Michael S. Mead <mmead@thermal.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import sleep

import numpy as np

from seekcamera import (
    SeekCameraIOType,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
)

from datetime import datetime
import cv2
import os


def on_frame(camera, camera_frame, stuff):
    """Async callback fired whenever a new frame is available.

    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera for which the new frame is available.
    camera_frame: SeekCameraFrame
        Reference to the class encapsulating the new frame (potentially
        in multiple formats).
    stuff: Tuple
        [TextIOWrapper, camera object, image number]
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the open CSV file to which
        to log data.
    """
    frame = camera_frame.thermography_float

    # Append the frame to the CSV file.
    np.savetxt(stuff[0], frame.data, fmt="%.1f")

    # Save the RGB image
    ret,ogrgb = stuff[1].read()
    rgbimg = ogrgb#cv2.flip(ogrgb, 1)#flip horizontally
    rgbimg = cv2.rotate(rgbimg, cv2.ROTATE_90_CLOCKWISE)
    rgbimg = rgbimg[64:576, 0:512]
    rgbimg = cv2.resize(rgbimg, (240,240), interpolation = cv2.INTER_AREA)

    max_number = 0
    
    # List all files in the directory
    for filename in os.listdir():
        if filename.endswith(".png"):
            try:
                # Extract the number part from the filename
                number = int(filename.split('.')[0])
                if number > max_number:
                    max_number = number
            except ValueError:
                pass  # Ignore files that don't match the expected pattern
    
    filename = str(max_number + 1) + ".png"
    cv2.imwrite(filename, rgbimg)
    print(str(max_number+1))


def on_event(camera, event_type, event_status, rgbcam):
    """Async callback fired whenever a camera event occurs.

    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera on which an event occurred.
    event_type: SeekCameraManagerEvent
        Enumerated type indicating the type of event that occurred.
    event_status: Optional[SeekCameraError]
        Optional exception type. It will be a non-None derived instance of
        SeekCameraError if the event_type is SeekCameraManagerEvent.ERROR.
    rgbcam: cv2 camera object
        User defined data passed to the callback. This can be anything
        but in this case it is a camera.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        # Open a new CSV file with the unique camera chip ID embedded.
        try:
            now = datetime.now()
            date_time = now.strftime("%Y%m%d%H%M")
            file = open("thermography-" + date_time + ".csv", "w")
        except OSError as e:
            print("Failed to open file: %s" % str(e))
            return

        # Start streaming data and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame, [file, rgbcam])
        camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        camera.capture_session_stop()

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return


def main():
    cwd = os.getcwd()
    os.environ["SEEKTHERMAL_LIB_DIR"] = cwd

    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M")
    dir1 = os.path.join(os.getcwd(),"therm" + date_time)
    os.mkdir(dir1)
    os.chdir(dir1)

    rgb = cv2.VideoCapture(0)
    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.

        manager.register_event_callback(on_event, rgb)

        while True:
            sleep(1.0)


if __name__ == "__main__":
    main()