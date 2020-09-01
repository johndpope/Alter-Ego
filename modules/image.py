# This is the main module for image and video manipulations
from PIL import Image
import cv2
from modules.util.files import *

settings = get_json_settings('project-settings.json')['image']
RESIZE_FORMAT = (settings["resize"]["width"], settings["resize"]["height"])

def evaluate_face_ratio(image, bounding_box):
    faceArea = get_bounding_box_area(bounding_box)
    imageArea = get_image_area(loadImage(image))
    ratio = faceArea/imageArea
    print (ratio)
    return ratio > settings["face-ratio"]["min"] and ratio < settings["face-ratio"]["max"]

def loadImage(path):
    return Image.open(path)

def openImage(image):
    image.show()

def resizeImage(sourceImage):
    destinationImage = sourceImage.resize(RESIZE_FORMAT)
    return destinationImage

def saveImage(image, path):
    path = get_new_file_name(path)
    image.save(path)
    return path

def prepare_deepfake_preview(sourcePath):
    targetFrames = {tf for tf in settings["preview"]["frames"]}
    cam = cv2.VideoCapture(sourcePath) 
    frameCount = 0
    paths = [] 
    while True:
        material, frame = cam.read()
        if not material:
            break 
        if frameCount in targetFrames:
            name = get_new_file_name('test/output/stills/', get_file_name(sourcePath + "_"))
            print ('Creating' + name + " from f. " + str(frameCount) + "...") 
            cv2.imwrite(name, frame) 
            paths.append(name)
        frameCount += 1
    cam.release() 
    cv2.destroyAllWindows()
    return paths

def get_bounding_box_area(bounding_box):
    left, top, right, bottom = bounding_box
    area = right * bottom
    return area

def get_image_area(image):
    width, height = image.size
    area = width * height
    return area