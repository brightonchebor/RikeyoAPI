from django.utils.deprecation import MiddlewareMixin
import re

class CsrfExemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if re.match(r'^/api/', request.path):
            setattr(request, '_dont_enforce_csrf_checks', True)