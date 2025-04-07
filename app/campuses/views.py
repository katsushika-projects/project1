from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Campus, University
from .serializers import CampusSerializer, UniversitySerializer


class UniversityDetailView(generics.RetrieveAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer


class UniversityListView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = University.objects.all()
        name = request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        serializer = UniversitySerializer(queryset, many=True)
        return Response(serializer.data)


class CampusDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Campus.objects.all()
    serializer_class = CampusSerializer


class CampusListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Campus.objects.all()
        university_id = request.query_params.get("university_id", None)
        if university_id:
            queryset = queryset.filter(university=university_id)
        serializer = CampusSerializer(queryset, many=True)
        return Response(serializer.data)
