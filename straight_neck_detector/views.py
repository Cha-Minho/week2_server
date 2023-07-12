from django.views.decorators.csrf import csrf_exempt
from .forms import ImageUploadForm
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from PIL import Image
from io import BytesIO
import time
import math as m
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from django.conf import settings
import base64
# from multiprocessing import Process

# p1 = Process()

# Initialize
good_frames = 0
bad_frames = 0

yellow = (0, 255, 255)
pink = (255, 0, 255)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,  # 정적 이미지 모드로 설정하여 추론 속도 향상
    model_complexity=1,      # 모델 복잡성을 낮춰 속도 향상
    min_detection_confidence=0.5,  # 최소 탐지 신뢰도 설정
    min_tracking_confidence=0.5    # 최소 추적 신뢰도 설정
)

# Calculate distance
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


# Calculate angle.
def findAngle(x1, y1, x2, y2):
    print(x1, y1, x2, y2)
    theta = m.atan2(y2 - y1, x2 - x1)
    degree = m.degrees(theta)
    return degree

def image_processing(image_object):
    global good_frames
    global bad_frames
    bad_posture = False
    
    try:
        image = np.array(image_object)
        # Process the image
        h, w = image.shape[:2]
        bad_color = (255, 0, 0)  # Set the bad color to red
        new_image = Image.new('RGBA', (w, h), (0,0,0,0))
        draw = ImageDraw.Draw(new_image)
        keypoints = pose.process(image)

        # Use lm and lmPose as representative of the following methods.
        lm = keypoints.pose_landmarks

        # Landmark coordinates
        l_shldr_x = int(lm.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w)
        l_shldr_y = int(lm.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)
        r_shldr_x = int(lm.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w)
        r_shldr_y = int(lm.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)
        l_ear_x = int(lm.landmark[mp_pose.PoseLandmark.LEFT_EAR].x * w)
        l_ear_y = int(lm.landmark[mp_pose.PoseLandmark.LEFT_EAR].y * h)
        l_hip_x = int(lm.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * w)
        l_hip_y = int(lm.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * h)

        # Calculate distances and angles
        neck_inclination = -(-findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y) - 90) -3
        torso_inclination = -findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y) - 90
        print(f"neck_inclination {neck_inclination} torso_inclination {torso_inclination}")
        if neck_inclination >= 10:
            color = bad_color
            bad_posture = True
        else:
            color = yellow
            bad_posture = False
        # Draw the landmarks on the image
        for id, landmark in enumerate(lm.landmark):
            x, y = int(landmark.x * w), int(landmark.y * h) - 20
            draw.ellipse([x-5, y-5, x+5, y+5], fill=color)

        # Determine whether good posture or bad posture
    

        # If bad posture for more than 3 minutes (180s) send an alert
        bad_time =  (1 / 30) * bad_frames  # Assuming a frame rate of 30 FPS

        return new_image, bad_posture
    except:
        return Image.new('RGBA', (w, h), (0,0,0,0)), False





@csrf_exempt
def image_api(request):
    start_time = time.time()
    if request.method == 'POST':
        file = request.FILES['image']
        image = Image.open(file).convert("RGB")

        # Save the incoming image for debugging
        image_path = os.path.join("week2/media", 'incoming_image.png')
        image.save(image_path)

        processed_image, bad_posture = image_processing(image)

        # Save the processed image
        processed_image_path = os.path.join("week2/media", 'processed_image.png')
        processed_image.save(processed_image_path)

        # Convert the processed image to base64
        output = BytesIO()
        processed_image.save(output, format='PNG')
        base64_image = base64.b64encode(output.getvalue()).decode()

        # Create a response JSON object
        response_data = {
            'image': base64_image,
            'bad_posture': bad_posture
        }

        print("--- %s seconds ---" % (time.time() - start_time))
        return JsonResponse(response_data)
    else:
        return HttpResponseBadRequest("Only POST method allowed")



@csrf_exempt
def for_test(request):
    if request.method == 'GET':
        return HttpResponse("Simple response")
    else:
        return HttpResponseBadRequest("Unsupported method")