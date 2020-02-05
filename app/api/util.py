from django.http import JsonResponse

def unauthorized(body):
    return JsonResponse(body, status=403, safe=False)

def success(body):
    return JsonResponse(body, status=200, safe=False)

def notFound(body):
    return JsonResponse(body, status=404, safe=False)