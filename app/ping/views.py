from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from .models import PingLog

class PingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ping, _ = PingLog.objects.get_or_create(pk="00000000-0000-0000-0000-000000000000")
        ping.last_pinged_at = now()
        ping.save()
        return Response({"status": "pong", "timestamp": now()})
