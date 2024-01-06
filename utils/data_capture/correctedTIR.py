#!/usr/bin/env python3
# Copyright 2021 Seek Thermal Inc.
#
# This is a basic file that will capture thermal data from the SeekThermal camera 
# and save it to a specified file in a specified format
#
# This version saves as csv, with little processing. ('corrected' data)
# only processing is flat field subtraction, gain and offset correction, bad pixel replacement
#
# Original author: Michael S. Mead <mmead@thermal.com>
# Modified for use in continuous capture applications by Emma Wadsworth <u1081622@utah.edu>
#
# The license for the original code is here: https://www.apache.org/licenses/LICENSE-2.0
#

from time import sleep

import numpy as np

import os

from datetime import datetime

import matplotlib.pyplot as plot

from seekcamera import (
    SeekCameraIOType,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
)

filenum = 0
def on_frame(camera, camera_frame, nothing):
    """Async callback fired whenever a new frame is available.

    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera for which the new frame is available.
    camera_frame: SeekCameraFrame
        Reference to the class encapsulating the new frame (potentially
        in multiple formats).
    file: TextIOWrapper
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the open CSV file to which
        to log data.
    """

    frame = camera_frame.corrected

    print(
        "frame available: {cid} (size: {w}x{h})".format(
            cid=camera.chipid, w=frame.width, h=frame.height
        )
    )

    global filenum
    try:
        filenum += 1
        file = open(str(filenum) + ".csv","w")
        square = frame.data[0:240, 0:240]
        np.savetxt(file, square, delimiter=',')
        file.close()

        #plot.figure(frameon=False)
        #plot.imshow(frame.data, cmap="inferno");
        #plot.savefig(str(filenum) + '.png');
    except OSError as e:
        print("failed to open file")

    return



def on_event(camera, event_type, event_status, _user_data):
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
    _user_data: None
        User defined data passed to the callback. This can be anything
        but in this case it is None.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        # Start streaming data and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame)
        camera.capture_session_start(SeekCameraFrameFormat.CORRECTED)

        # Set up folder to save new capture data in
        now = datetime.now()
        date_time = now.strftime("%Y%m%d%H%M")
        dirname = "correctedTIR" + date_time
        filepath = os.path.join(os.getcwd(),dirname)
        os.mkdir(filepath)
        print("saving images to: " + filepath)
        os.chdir(filepath)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        camera.capture_session_stop()

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return


def main():
    # Make sure that seekcamera.dll is in the current working directory of this project. 
    # Also make sure you have installed the Seek Camera SDK
    cwd = os.getcwd()
    os.environ["SEEKTHERMAL_LIB_DIR"] = cwd
    print("dll should be in: " + os.environ["SEEKTHERMAL_LIB_DIR"])

    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        manager.register_event_callback(on_event)

        while True:
            sleep(1.0)


if __name__ == "__main__":
    main()