#1. Importing dependencies

#Importing OpenCV for computer VIsion Stuff
#import numpy.core.multiarray
import numpy
import cv2
from matplotlib import pyplot as plt 

#Function to get photo
def take_photo():
    cap = cv2.VideoCapture(0)
    ret,frame = cap.read()
    cv2.imwrite("webcamphoto.jpg",frame)
    cap.release()
    
#2. Connecting to Your Webcam

##Conect to capture device
#cap = cv2.VideoCapture(0)
##Get a frame from the device
#ret, frame = cap.read()

##Using matplotlib to visualize the frame 
#plt.imshow(frame)
#plt.show()

##Releases capture
#cap.release()

#take_photo()

#3. Rendering in real time

#Conect to webcam
cap = cv2.VideoCapture(0)
#Loop throught everyu frame until we close our webcam
while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow('Webcam',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()