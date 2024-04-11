from django.utils.deprecation import MiddlewareMixin
from api.models import UserToken
from django.http import HttpResponse
from django.urls import resolve


class BasicAuthMiddleware(MiddlewareMixin):
    """
    This middleware checks for an Authorization header with a value for Bearer <token>.
    If a token is supplied, it will be checked against the UserToken model.
    If a user is found with that token, it will fetch it and associate request.user to it.
    """
    def process_request(self, request):
        # Check for requires_auth parameter in class based view.
        func, args, kwargs = resolve(request.path_info)
        view_class = getattr(func, 'view_class', None)
        if view_class is not None:
            requires_auth = getattr(view_class, 'requires_auth', True)
            if requires_auth:
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
