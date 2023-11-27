
from django.conf import settings
from geopy.distance import geodesic
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import phonenumbers


def normalize_phone_number(phone_number):
    if phone_number.startswith("0"):
        return "+91" + phone_number[1:]  # Replace leading 0 with +91
    elif phone_number.startswith("+91"):
        return phone_number  # Already in the correct format
    else:
        return None



#for distance
def calculate_distance(request):
    if request.method == 'POST':
        latitude1 = float(request.POST.get('latitude1', 0))
        longitude1 = float(request.POST.get('longitude1', 0))
        latitude2 = float(request.POST.get('latitude2', 0))
        longitude2 = float(request.POST.get('longitude2', 0))

        user1_location = (latitude1, longitude1)
        user2_location = (latitude2, longitude2)

        distance_km = geodesic(user1_location, user2_location).kilometers

        return JsonResponse({"distance_km": distance_km})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

