# This is the main entry-point for Alter Ego

import socket
import paramiko
import json
import time
import threading

from modules.image import *
from modules.ai_operations import *
from modules.util.files import *

# setup

settings = get_json_settings('project-settings.json')

inPi = settings["input-pi"]
outPi = settings["output-pi"]
commands =  settings["commands"]
timing = settings["timing"]

# concurrency helpers

def parallel(func):
    def parallel_func(*args, **kw):
        t = threading.Thread(None, target=func, args=args, kwargs=kw)
        t.setName(func.__name__ + " as Parallel")
        t.start()
    return parallel_func
    
def parallel_daemon(func):
    def parallel_func(*args, **kw):
        t = threading.Thread(None, target=func, args=args, kwargs=kw, daemon=True)
        t.setName(func.__name__ + " as Parallel Daemon")
        t.start()
    return parallel_func

def monitor_threads():
    print ("Number of Threads: ", threading.active_count())
    for thread in threading.enumerate():
        print(thread)
# run "camera" on IN and OUT Pis with ssh
def run_camera_in():
    print("STARTED: Run Camera Input")
    execOnPi(inPi, commands['camera'])

def run_camera_out():
    # async camera task for output PI
    pass

# Run FTP Folder listener on IN and OUT Pis
def run_ftp_listener_in():
    print("STARTED: FTP Listener Input Pics")
    ftp = connectToFtp(inPi)
    watch_directory_for_change("/home/pi/MyPics", on_new_file_in, remote=ftp)

def run_ftp_listener_out():
    # listen for pictures from Input-PI and if new picture comes in run event
    pass

# Run Deepfake generator
def run_deepfake():
    print("STARTED: Listen for Deepfake Input")
    watch_directory_for_change("test/output/resized", prepare_deepfake)

@parallel_daemon
def watch_directory_for_change(directory, on_new_file, interval=timing["interval"], remote=None):
    path_to_watch = directory
    target = get_os()
    if remote:
        target = remote
    print("starting to watch ", path_to_watch, "...")
    before = dict([(f, None) for f in target.listdir(path_to_watch)])
    while True:
        printpath = path_to_watch
        if remote: 
            printpath = printpath + " : " + str(remote.get_channel().get_id())
        #print("listening on: ", printpath, "...")
        after = dict([(f, None) for f in target.listdir(path_to_watch)])
        added = [f for f in after if not f in before]
        if len(added) > 0:
            time.sleep(interval)
            path = path_to_watch + "/" + added[0]
            print(path)
            if remote: 
                newFile = remote.open(path) 
            else:
                newFile = open(path, "rb")
            on_new_file(newFile)
        before = after
        time.sleep(interval/2)

def on_new_file_in(newFile):
    print("new file detected: ", newFile)
    valid = validate_face(newFile)
    print(valid)
    if valid:
        print("is a face")
        image = loadImage(newFile)
        resizedImage = resizeImage(image)
        newPath = saveImage(resizedImage, "test/output/resized/")
    else: print("is not a face")

@parallel
def prepare_deepfake(image):
    print("Uploading Image to Deepfake API...")
    url = generate_deepfake(image)
    start = time.time()
    time.sleep(timing["process"])
    while True: 
        response = download_deepfake(url)
        if response.ok:
            path = save_video(response.content)
            print("Downloaded Deepfake at: " + path + "in: " + str(time.time() - start))
            process_deepfake(path)
            break
        time.sleep(1)

def process_deepfake(path):
    pass

# Remote Communication tasks

def openSSH(pi):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect(pi["ip"], username=pi["user"], password=pi["password"])
    return client

@parallel_daemon
def execOnPi(pi, command):
    client = openSSH(pi)
    print('started exec of ' + command + '...')
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    # TODO: Implement KeyBoardInterrupt for Child process
    for line in iter(stdout.readline, ""):
        print(line, end="")
    print('finished.')
    client.close()

def connectToFtp(pi):
    client = openSSH(pi)
    ftp = client.open_sftp()
    return ftp

# listen for api response and save output video to media-server

    # download Video and take sample still-frames

    # run samples through face recognition and pair face with video

    # upload face with video pair

# listen for pictures from OUT and find matching face when a new picture is detected

    # send media-server URL to PI and command "display"

def main():
    run_camera_in()
    run_ftp_listener_in()
    run_deepfake()
    while True:
        time.sleep(5)
        monitor_threads()
# Operations before loop
# CORE Async Loop
if __name__ == '__main__':
    main()

# Operations after loop
