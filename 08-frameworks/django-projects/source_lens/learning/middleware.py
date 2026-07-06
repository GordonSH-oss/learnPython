class SourceLensHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.source_lens_middleware_seen = True
        response = self.get_response(request)
        response["X-Source-Lens"] = "middleware-ran"
        return response
