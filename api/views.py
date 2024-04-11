from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from app.models import Scientist
import json


@method_decorator(csrf_exempt, name='dispatch')
class ScientistListView(View):

    def get(self, request, *args, **kwargs):
        scientists = [s.serialize() for s in Scientist.objects.all()]
        return JsonResponse(scientists, safe=False)

    def post(self, request, *args, **kwargs):
        scientist_data = json.loads(request.body)
        scientist = Scientist.objects.create(**scientist_data)
        return JsonResponse(scientist.serialize(), safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ScientistDetailView(View):

    def get(self, request, scientist_id, *args, **kwargs):
        scientist = [s.serialize() for s in Scientist.objects.filter(id=scientist_id)]
        return JsonResponse(scientist, safe=False)

    def put(self, request, scientist_id):
        scientist_data = json.loads(request.body)
        Scientist.objects.filter(id=scientist_id).update(**scientist_data)
        return JsonResponse({'message': 'Scientist updated successfully!'})

    def delete(self, request, scientist_id, *args, **kwargs):
        Scientist.objects.filter(id=scientist_id).delete()
        return JsonResponse({'message': 'Scientist deleted successfully!'})


@method_decorator(csrf_exempt, name='dispatch')
class GetUserToken(View):
    requires_auth = False

    def post(self, request, *args, **kwargs):
        credentials = json.loads(request.body)
        user = User.objects.get(username=credentials['username'])
        print(user.password, credentials['password'])
        if check_password(credentials['password'], user.password):
            return JsonResponse({'token': user.usertoken.bearer_token})

        return JsonResponse({'message': 'Invalid credentials.'}, status=400)
