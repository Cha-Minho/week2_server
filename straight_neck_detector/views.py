from django.views.decorators.csrf import csrf_exempt
from .forms import ImageUploadForm
from django.http import HttpResponse, HttpResponseBadRequest
from PIL import Image
from io import BytesIO
import time
import math as m
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from django.conf import settings
# from multiprocessing import Process

# p1 = Process()
# Initialize
good_frames = 0
bad_frames = 0

blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Calculate distance
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


# Calculate angle.
def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree

# Function to send alert
def sendWarning(x):
    pass




def image_processing(image_object):
    copy_object = image_object
    global good_frames
    global bad_frames
    try:
        image = np.array(image_object)
        # Process the image
        keypoints = pose.process(image)

        # Use lm and lmPose as representative of the following methods.
        lm = keypoints.pose_landmarks
        lmPose = mp_pose.PoseLandmark

        # Get the size of the image
        h, w = image.shape[:2]

        # Landmark coordinates
        l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
        l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
        r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
        r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
        l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
        l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
        l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
        l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

        # Calculate distances and angles
        offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)
        neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
        torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

        # Draw the landmarks on the image
        draw = ImageDraw.Draw(image_object)
        for id, landmark in enumerate(lm.landmark):
            x, y = int(landmark.x * w), int(landmark.y * h)
            draw.ellipse([x-5, y-5, x+5, y+5], fill=yellow)
        
        # Connect landmarks with lines
        connections = mp_pose.POSE_CONNECTIONS
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
        
            start_landmark = lm.landmark[start_idx]
            end_landmark = lm.landmark[end_idx]
        
            start_x, start_y = int(start_landmark.x * w), int(start_landmark.y * h)
            end_x, end_y = int(end_landmark.x * w), int(end_landmark.y * h)
        
            draw.line([(start_x, start_y), (end_x, end_y)], fill=pink, width=2)

        # Determine whether good posture or bad posture
        bad_posture = False
        if neck_inclination < 40 and torso_inclination < 10:
            good_frames += 1
            bad_frames = 0
        else:
            good_frames = 0
            bad_frames += 1
            bad_posture = True

        # If bad posture for more than 3 minutes (180s) send an alert
        bad_time =  (1 / 30) * bad_frames  # Assuming a frame rate of 30 FPS
        if bad_time > 180:
            sendWarning()

        return image_object, bad_posture
    except:
        return copy_object, True


@csrf_exempt
def image_api(request):
    start_time = time.time()
    if request.method == 'POST':
        file = request.FILES['image']
        image = Image.open(file).convert("RGB")

        # Save the incoming image for debugging
        image_path = os.path.join("week2/media", 'incoming_image.png')
        image.save(image_path)

        processed_image, _ = image_processing(image)

        # Rotate the image 90 degrees clockwise
        processed_image = processed_image.rotate(-90)

        # Save the processed image
        processed_image_path = os.path.join("week2/media", 'processed_image.png')
        processed_image.save(processed_image_path)

        output = BytesIO()
        processed_image.save(output, format='PNG')
        response = HttpResponse(content_type='image/png')
        response.write(output.getvalue())
        end_time = time.time()
        print(end_time - start_time)
        return response
        
    else:
        return HttpResponseBadRequest('Only POST request are allowed')



@csrf_exempt
def for_test(request):
    if request.method == 'GET':
        return HttpResponse("Simple response")
    else:
        return HttpResponse("Unsupported method")