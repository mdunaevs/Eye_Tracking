'''

This program detects an eye's pupil position. This information will then be translated into
information that replicates the eye movements of our Mona Lisa device. Using opencv, I detect 
the locations of the eyes for the largest face. Once the eyes have been isolated, I apply blob
filtering on them to extract the pupil. A blob is just a group of connected pixels in a binary 
image. To extract the pupil, I find the second largest blob which represents the pupil. Using the
information of the position of this blob and a relative position to the center of the eyes, I can
calculate a distance between these positions.

To run the program, download the code and xml classifiers and on terminal run 
    $ python3 eye-tracker.py


To exit from the program press the 'q' key.

One thing to note is try to keep the lighting constistent, because sometimes when you have weird lighting
the program has troubles trying to find the eye. 

'''

import cv2
import numpy
import paho.mqtt.client as mqtt

# Classifiers used for detecting face and eyes 
faceMask = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyeMask = cv2.CascadeClassifier('haarcascade_eye.xml')

# Detects and returns an image of the largest face on the screen.
def detect_largest_face(img):
    gray_frame = cv2.cvtColor(img, cv2.IMREAD_GRAYSCALE)
    # Use the face mask cascade classifier
    coords = faceMask.detectMultiScale(gray_frame, 1.3, 5)
    if len(coords) > 1:
        biggest = (0, 0, 0, 0)
        for i in coords:
            if i[3] > biggest[3]:
                biggest = i
        biggest = numpy.array([i], numpy.int32)
    elif len(coords) == 1:
        biggest = coords
    else:
        return None
    for (x, y, w, h) in biggest:
        frame = img[y:y + h, x:x + w]
    return frame

# Detects the eyes of the largest face on the screen
def detect_eyes(img):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eyes = eyeMask.detectMultiScale(gray_frame, 1.3, 5) # detect eyes
    width = numpy.size(img, 1) # get face frame width
    height = numpy.size(img, 0) # get face frame height
    left_eye = None
    right_eye = None
    for (x, y, w, h) in eyes:
        if y > height / 2:
            pass
        eyecenter = x + w / 2  # get the eye center
        # check if we are working with the left or right eye
        if eyecenter < width * 0.5:
            left_eye = img[y:y + h, x:x + w]
        else:
            right_eye = img[y:y + h, x:x + w]
    return left_eye, right_eye

# Cuts portion of the image frame to remove the eyebrows 
def cut_eyebrows(img):
    height, width = img.shape[:2]
    eyebrow_h = int(height / 4)
    img = img[eyebrow_h:height-eyebrow_h, 0:width]  # cut eyebrows out (15 px)
    return img

# Isolates the pupil from the eye
def extractPupilBlob(pupilFrame, eyeh, eyew):
    windowClose = numpy.ones((5,5),numpy.uint8)
    windowOpen = numpy.ones((2,2),numpy.uint8)
    windowErode = numpy.ones((2,2),numpy.uint8)
    pupilInit = pupilFrame
    _, pupilFrame = cv2.threshold(pupilFrame,55,255,cv2.THRESH_BINARY)
    pupilFrame = cv2.morphologyEx(pupilFrame, cv2.MORPH_CLOSE, windowClose)
    pupilFrame = cv2.morphologyEx(pupilFrame, cv2.MORPH_ERODE, windowErode)
    pupilFrame = cv2.morphologyEx(pupilFrame, cv2.MORPH_OPEN, windowOpen)
    
    threshold = cv2.inRange(pupilFrame,250,255)		#get the blobs
    _, contours, _ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    
    # if there are 3 or more blobs, delete the biggest and delete the left most for the right eye
    # #if there are 2 blob, take the second largest
    # #if there are 1 or less blobs, do nothing
    
    if len(contours) >= 2:
        #find biggest blob
        maxArea = 0
        MAindex = 0 # index of largest blob 
        distanceX = []
        currentIndex = 0 
        for cnt in contours:
            area = cv2.contourArea(cnt)
            center = cv2.moments(cnt)
            # get center coordinates for circle being drawn
            if center['m00'] != 0:
                cx = int(center["m10"] / center["m00"])
                cy = int(center["m01"] / center["m00"])
            else:
                cx,cy = 0, 0
            distanceX.append(cx)	
            if area > maxArea:
                maxArea = area
                MAindex = currentIndex
            currentIndex = currentIndex + 1
        # remove largest blob
        del contours[MAindex]
        del distanceX[MAindex]
    eye = 'right'
    if len(contours) >= 2:
        if eye == 'right':
            edgeOfEye = distanceX.index(min(distanceX))
        else:
            edgeOfEye = distanceX.index(max(distanceX))	
        del contours[edgeOfEye]
        del distanceX[edgeOfEye]
    
    largeBlob = []
    if len(contours) >= 1:		#get largest blob
        maxArea = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > maxArea:
                maxArea = area
                largeBlob = cnt
            
    if len(largeBlob) > 0:
        center = cv2.moments(largeBlob)
        # get center coordinates for circle being drawn
        if center['m00'] != 0:
            cx = int(center["m10"] / center["m00"])
            cy = int(center["m01"] / center["m00"])
        else:
            cx,cy = 0, 0
        cv2.circle(pupilInit,(cx,cy),5,255,-1)
    return (pupilInit, cx, cy)


def nothing(x):
    pass

def getDistance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1/2)

# Executes pupil tracking code
def main():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('image')
    while True:
        _, frame = cap.read()
        face = detect_largest_face(frame) # gets face
        if face is not None:
            faceh, facew = face.shape[:2]
            cv2.rectangle(face,(0, 0),(facew, faceh),(255,255,0),2)
            eyes = detect_eyes(face) # gets eyes
            for eye in eyes:
                if eye is not None:
                    eye = cut_eyebrows(eye) # removes eyebrows from eye
                    eyeh, eyew = eye.shape[:2]
                    # draw crosshair
                    cv2.rectangle(eye,(0, 0),(eyew, eyeh),(255,0,255),2)
                    cv2.line(eye, (eyew // 2, 0), ((eyew // 2,eyeh)), (0,0,255),1)
                    cv2.line(eye, (0, eyeh // 2), ((eyew, eyeh // 2)), (0,0,255),1)

                    # Converts eye image into grayscale so that we can apply binary 
                    # classification / operations on it
                    pupilFrame = cv2.cvtColor(eye,cv2.COLOR_RGB2GRAY)
                    pupilFrame = cv2.equalizeHist(pupilFrame)

                    # get the pupil blob image 
                    eye, pupilx, pupily = extractPupilBlob(pupilFrame, eyew, eyeh)
                    eyex, eyey = eyew // 2, eyeh // 2

                    distance = round(getDistance(eyex, eyey, pupilx, pupily), 2)
                    print(distance)

                    cv2.imshow('eye', eye)
        cv2.imshow('image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()