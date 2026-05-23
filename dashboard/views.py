from django.contrib.auth import get_user_model
from packing.models import PackingTemplate, Trip

def dashboard_callback(request, context):
    User = get_user_model()
    context.update({
        "total_users": User.objects.count(),
        "total_camps": PackingTemplate.objects.count(),
        "total_campers": Trip.objects.count(),
    })
    return context
