
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


def custom_response(success, data=None, message=None):
    response_data = {
        "success": success,
        "data": data if data is not None else {},
        "message": message if message else "Operation successful",
    }
    return JsonResponse(response_data)




