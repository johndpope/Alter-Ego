#This executes the camera on the Input-PI
from picamera import PiCamera
import os
import time
from fractions import Fraction
from files import *

def set_camera_settings(camera, settings):
    camera.exposure_mode = settings["exp-mode"]
    camera.framerate = Fraction(settings["framerate"], int(settings["interval"]))
    camera.sharpness = 80
    camera.exposure_compensation = settings["exp"]
    camera.zoom = setZoom(settings)

def monitorCamSettings(camera):
    print("iso: ", camera.iso)
    print("exposure speed: ", camera.exposure_speed)
    print("frame rate: ", camera.framerate)
    print(camera.exposure_mode)
    print(camera.digital_gain)
    print(camera.analog_gain)
    print(camera.brightness) 

def setZoom(settings):
    x = y = settings["zoom"] / 2
    width = height = 1.0 - x * 2
    return (x, y, width, height)

def take_picture(camera):
    path = get_new_file_name("MyPics/")
    camera.capture(path, quality=100)

def clearFolder():
    pics = os.listdir("MyPics")
    if len(pics) > 100:
        sorted_pics = sorted(pics, key=lambda x: os.path.getmtime(x))
        old_pics = pics[0:50]
        for pic in old_pics:
            print(os.path.join("MyPics", pic))
            #os.remove(os.path.join("MyPics", pic))

#FIXME: check Shutterspeed and White Balance

def main():
    ID = get_pi_id()
    cameraSettings = get_json_settings('MyScripts/project-settings.json')[ID]['camera']
    camera = PiCamera(resolution=(cameraSettings['res']['x'],cameraSettings['res']['y']))
    set_camera_settings(camera, cameraSettings)
    interval = cameraSettings["interval"]
    #monitorCamSettings(camera)
    for i in range(3):
        time.sleep(interval)
        print(ID + " taking a picture: " + str(i + 1) + "...")
        clearFolder()
        take_picture(camera)
    camera.close()

if __name__ == "__main__":
    main()
    



