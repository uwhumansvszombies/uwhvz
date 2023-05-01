from django.http import JsonResponse

def success(body = ""):
    return JsonResponse(body, status=200, safe=False)

def badRequest(body = ""):
    return JsonResponse(body, status=400, safe=False)

def unauthorized(body = ""):
    return JsonResponse(body, status=401, safe=False)

def forbidden(body = ""):
    return JsonResponse(body, status=403, safe=False)

def notFound(body = ""):
    return JsonResponse(body, status=404, safe=False)

def conflictOrDuplicate(body = ""):
    return JsonResponse(body, status=409, safe=False)
