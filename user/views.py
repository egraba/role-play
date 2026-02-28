from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


@method_decorator(ratelimit(key="ip", rate="5/m", block=True), name="post")
class RateLimitedLoginView(LoginView):
    pass
