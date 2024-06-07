from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from api.models import Complaint
from api.serializers import ComplaintSerializer
from app.models import Scientist

import json


@method_decorator(csrf_exempt, name='dispatch')
class ScientistListView(View):

    def get(self, request, *args, **kwargs):
        scientists = [s.serialize() for s in Scientist.objects.all()]
        return JsonResponse(scientists, safe=False)

    def post(self, request, *args, **kwargs):
        try:
            scientist_data = json.loads(request.body)
            scientist = Scientist.objects.create(**scientist_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'Scientist already registered.'}, status=400)
        return JsonResponse(scientist.serialize(), safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ScientistDetailView(View):

    def get(self, request, scientist_id, *args, **kwargs):
        try:
            scientist = Scientist.objects.get(id=scientist_id)
        except Scientist.DoesNotExist:
            return JsonResponse({'error': 'Scientist not found.'}, status=404)
        return JsonResponse(scientist.serialize(), safe=False)

    def put(self, request, scientist_id, *args, **kwargs):
        try:
            scientist_data = json.loads(request.body)
            scientist = Scientist.objects.get(id=scientist_id)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Scientist.DoesNotExist:
            return JsonResponse({'error': 'Scientist not found.'}, status=404)

        Scientist.objects.filter(id=scientist.id).update(**scientist_data)
        return JsonResponse({'message': 'Scientist updated successfully!'})

    def delete(self, request, scientist_id, *args, **kwargs):
        try:
            scientist = Scientist.objects.get(id=scientist_id)
        except Scientist.DoesNotExist:
            return JsonResponse({'error': 'Scientist not found.'}, status=404)
        scientist.delete()
        return JsonResponse({'message': 'Scientist deleted successfully!'})


@method_decorator(csrf_exempt, name='dispatch')
class GetUserToken(View):
    requires_auth = False

    def post(self, request, *args, **kwargs):
        try:
            credentials = json.loads(request.body)
            user = User.objects.get(username=credentials['username'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        if check_password(credentials['password'], user.password):
            return JsonResponse({'token': user.usertoken.bearer_token})

        return JsonResponse({'message': 'Invalid credentials.'}, status=400)


class ComplaintListView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

