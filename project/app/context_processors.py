from django.conf import settings


def inject_data(request):
    return {
        "USERNAME_MINLENGTH": settings.USERNAME_MINLENGTH,
        "USERNAME_MAXLENGTH": settings.USERNAME_MAXLENGTH,
        "PAGE_SIZE": settings.PAGE_SIZE,
    }