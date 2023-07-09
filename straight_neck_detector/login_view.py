from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from straight_neck_detector.models import User
import json

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email) # Fetch user from DB

            if user.password == password:
                return HttpResponse("User logged in.")
            else:
                return HttpResponse("Invalid username or password.")
        except User.DoesNotExist:
            return HttpResponse("User does not exist.")
    else:
        return HttpResponse("Only POST requests allowed.")


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        is_employed = data.get('is_employed')

        if not User.objects.filter(email=email).exists():  # Check if user with the same email exists
            user = User(email=email, name=name, password=password, is_employed=is_employed)
            user.save() # Save the new user to DB
            return HttpResponse("User registered.")
        else:
            return HttpResponse("User with this email already exists.")
    else:
        return HttpResponse("Only POST requests allowed.")
