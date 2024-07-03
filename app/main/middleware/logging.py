import logging

logger = logging.getLogger('waitress')

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Route: {request.path}, Method: {request.method}")
        response = self.get_response(request)
        return response