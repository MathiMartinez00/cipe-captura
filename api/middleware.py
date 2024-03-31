from django.utils.deprecation import MiddlewareMixin
from api.models import UserToken
from django.http import HttpResponse


class BasicAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.headers.get('Authorization', None):
            values = request.headers['Authorization'].split(" ")

            auth_type = values[0]
            if auth_type != 'Bearer' or len(values) > 2:
                return HttpResponse('Invalid format.', status=401)

            token_value = values[1]
            try:
                token = UserToken.objects.filter(bearer_token=token_value).get()
                request.user = token.user
            except UserToken.DoesNotExist:
                return HttpResponse('Invalid token.', status=401)

        return None

    def process_response(self, request, response):
        return response
