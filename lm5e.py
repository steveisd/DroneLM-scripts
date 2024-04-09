#Apologies for spaghetti code
import cv2
import numpy as np
import os
import pygame
import socket
import tellopy
import threading
import time
import subprocess

prepend = "/".join(os.path.abspath(__file__).split("\\")[:-1])

try: os.remove(prepend + "/exit.txt")
except: pass

subprocess.Popen(["start", "cmd", "/c", "python " + prepend + "/chattere.py"], shell=True)

def cam():
    try:
        global vidOut
        global stop_cam
        global cam_error
        cap = cv2.VideoCapture("udp://@127.0.0.1:5000") # Random address

        if not cap.isOpened:
            cap.open()

        while not stop_cam:
            res, vidOut = cap.read()

    except Exception as e:
        cam_error = e

    finally:
        cap.release()
        print("Video Stream stopped.")

def videoFrameHandler(event, sender, data): # Video Frame loopback
    loopback.sendto(data,('127.0.0.1',5000)) # Random address

def flightDataHandler(event, sender, data):
    #print(data)
    pass

def handleFileReceived(event, sender, data):
    """Create a file in the same folder as program (hopefully)"""
    global date_fmt
    path = 'tello' + str(int(time.time())) + '.jpeg'
    with open(path, 'wb') as fd:
        fd.write(data)

#loop
vidOut = None # Frame that can be used externally
stop_cam = False # Stop flag
cam_error = None # Error message can view or raise()
loopback = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
camt = threading.Thread(None, cam) # Start thread
camt.start()

drone = tellopy.Tello()
drone.connect()
drone.start_video()
drone.subscribe(drone.EVENT_VIDEO_FRAME, videoFrameHandler)
drone.subscribe(drone.EVENT_FILE_RECEIVED, handleFileReceived)
drone.subscribe(drone.EVENT_FLIGHT_DATA, flightDataHandler)

pygame.init()
pygameWindow = pygame.display.set_mode((720,360)) # Can scale to 1280, 720 or others
pygame.display.set_caption("LOL")
clock = pygame.time.Clock()
#drone.set_video_encoder_rate(5)

x = 0
y = 0
z = 0

warn = ""
prompt = ""
#feel free to edit this
loggerr = "### Instruction: You are in control of a drone. Given your current position of (" + str(x) + ", " + str(y) + ", " + str(z) + ") where your limits are between (-15, 0, -15) and (15, 15, 15) and current state: ONGROUND you can take the following actions: FORWARD(), BACKWARD(), LEFT(), RIGHT(), UP(), DOWN(), FLY(), TALK(message) where “message” can be anything to say, or LAND(). To use an action, output them as is or else nothing will happen you big dummy.\nAction log:\nDrone: FLY()\nDrone: LAND()\nDrone:"

with open(prepend + "/output.txt", "w", encoding="utf-8") as f:
    f.write(loggerr)

#main
try:
    done = False
    while not done:
        loggerr = "### Instruction: You are in control of a drone. Given your current position of (" + str(x) + ", " + str(y) + ", " + str(z) + ") where your limits are between (-15, 0, -15) and (15, 15, 15) and current state: ONGROUND you can take the following actions: FORWARD(), BACKWARD(), LEFT(), RIGHT(), UP(), DOWN(), FLY(), TALK(message) where “message” can be anything to say, or LAND(). To use an action, output them as is or else nothing will happen you fucking idiot.\nAction log:\nDrone: FLY()\nDrone: LAND()\nDrone:"

        if os.path.isfile(prepend + "/input.txt"):
            with open(prepend + "/input.txt", "r", encoding="utf-8") as f:
                action = f.read()
            os.remove(prepend + "/input.txt")

            # if "FLY()" in action: #uncomment this to make your LM be able to takeoff
            #     drone.takeoff()
            #     y += 5
            #     prompt += " FLY()\nDrone:"

            if "LAND()" in action:
                drone.land()
                y = 0
                prompt += " LAND()\nDrone:"
            if "UP()" in action:
                if y > 15:
                    prompt += " REACHED LIMIT!\nDrone:"
                else:
                    if y == 0:
                        drone.takeoff()
                    else:
                        drone.up(50)
                    y += 5
                    prompt += " UP()\nDrone:"
            if "DOWN()" in action:
                y -= 5
                if y == 0:
                    drone.land()
                    prompt += " LAND()\nDrone:"
                else:
                    drone.down(50)
                    prompt += " DOWN()\nDrone:"
            if "FORWARD()" in action:
                if x > 15:
                    prompt += " REACHED LIMIT!\nDrone:"
                else:
                    prompt += " FORWARD()\nDrone:"
                    x += 5
                    drone.forward(50)
            if "BACKWARD()" in action:
                if x < -15:
                    prompt += " REACHED LIMIT!\nDrone:"
                else:
                    prompt += " FORWARD()\nDrone:"
                    x -= 5
                    drone.backward(50)
            if "LEFT()" in action:
                if z < -15:
                    prompt += " REACHED LIMIT!\nDrone:"
                else:
                    prompt += " LEFT()\nDrone:"
                    z -= 5
                    drone.left(50)
            if "RIGHT()" in action:
                if z > 15:
                    prompt += " REACHED LIMIT!\nDrone:"
                else:
                    prompt += " RIGHT()\nDrone:"
                    z += 5
                    drone.right(50)

            if "TALK(" in action:
                prompt += " " + action + "\nDrone:"

            with open(prepend + "/output.txt", "w", encoding="utf-8") as f:
                f.write(loggerr + prompt)

            print("!")

        else:
            action = ""
        print("Action", action)

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    done = True
                if e.key == pygame.K_RETURN:
                    drone.take_picture()
                if e.key == pygame.K_z:
                    drone.set_video_mode(not drone.zoom)
                if e.key == pygame.K_1:
                    drone.takeoff()
                if e.key == pygame.K_2:
                    drone.land()
                if e.key == pygame.K_w:
                    drone.up(50)
                if e.key == pygame.K_s:
                    drone.down(50)
                if e.key == pygame.K_a:
                    drone.set_yaw(-1.0)
                if e.key == pygame.K_d:
                    drone.set_yaw(1.0)
                if e.key == pygame.K_UP:
                    drone.forward(50)
                if e.key == pygame.K_DOWN:
                    drone.backward(50)
                if e.key == pygame.K_LEFT:
                    drone.left(50)
                if e.key == pygame.K_RIGHT:
                    drone.right(50)

            if e.type == pygame.KEYUP:
                if e.key == pygame.K_w:
                    drone.up(0)
                if e.key == pygame.K_s:
                    drone.down(0)
                if e.key == pygame.K_a:
                    drone.set_yaw(0)
                if e.key == pygame.K_d:
                    drone.set_yaw(0)
                if e.key == pygame.K_UP:
                    drone.forward(0)
                if e.key == pygame.K_DOWN:
                    drone.backward(0)
                if e.key == pygame.K_LEFT:
                    drone.left(0)
                if e.key == pygame.K_RIGHT:
                    drone.right(0)

        try:
            frame = cv2.cvtColor(vidOut, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            pygameWindow.fill((0,0,0))
            pygameWindow.blit(frame,(0,0))

        except Exception as e:
            print(e)
            pygameWindow.fill((0,0,255))

        pygame.display.update()
        clock.tick(15)

finally:
    stop_cam = True
    camt.join()
    drone.quit()
    pygame.quit()
    cv2.destroyAllWindows()
    time.sleep(3)
    print("END")


with open(prepend + "/exit.txt", "w", encoding="utf-8") as f:
    pass

exit()
