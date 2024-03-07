from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model


# TODO: Figure this out. Add a way to generate tokens.
class BasicAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        User = get_user_model()
        if request.headers.get('Authorization', None):
            values = request.headers['Authorization'].split(" ")
            auth_type = values[0]
            token_value = values[1]
            user = User.objects.filter(username=token_value)
            if user:
                request.user = user[0]
        return None

    def process_response(self, request, response):
        return response
