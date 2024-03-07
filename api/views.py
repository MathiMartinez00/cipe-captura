from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app.models import Scientist
import json


@method_decorator(csrf_exempt, name='dispatch')
class ScientistController(View):

    def get(self, request, *args, **kwargs):
        scientists = [s.serialize() for s in Scientist.objects.all()]
        return JsonResponse(scientists, safe=False)

    def post(self, request, *args, **kwargs):
        scientist_data = json.loads(request.body)
        Scientist.objects.create(**scientist_data)
        return JsonResponse({'message': 'Scientist created successfully!'})
