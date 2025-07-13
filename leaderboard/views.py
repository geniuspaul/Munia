from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TopEarner, TopReferral
from .serializers import TopEarnerSerializer, TopReferralSerializer


class TopEarnerAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        top_10 = TopEarner.objects.all().order_by('rank')[:10]
        top_10_serialized = TopEarnerSerializer(top_10, many=True).data

        user_entry = TopEarner.objects.filter(user=request.user).first()
        authenticated_user = TopEarnerSerializer(user_entry).data if user_entry else None

        return Response({
            "top_10": top_10_serialized,
            "authenticated_user": authenticated_user
        })


class TopReferralAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        top_10 = TopReferral.objects.all().order_by('rank')[:10]
        top_10_serialized = TopReferralSerializer(top_10, many=True).data

        user_entry = TopReferral.objects.filter(user=request.user).first()
        authenticated_user = TopReferralSerializer(user_entry).data if user_entry else None

        return Response({
            "top_10": top_10_serialized,
            "authenticated_user": authenticated_user
        })
