from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TopEarner, TopReferral
from .serializers import TopEarnerSerializer, TopReferralSerializer

class TopEarnerAPIView(APIView):
    def get(self, request):
        queryset = TopEarner.objects.all().order_by('rank')
        serializer = TopEarnerSerializer(queryset, many=True)
        return Response(serializer.data)

class TopReferralAPIView(APIView):
    def get(self, request):
        queryset = TopReferral.objects.all().order_by('rank')
        serializer = TopReferralSerializer(queryset, many=True)
        return Response(serializer.data)
