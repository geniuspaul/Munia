from .models import MiningSession

def m_session(request):
    return MiningSession.objects.filter(user=request.user).latest('start_time')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')