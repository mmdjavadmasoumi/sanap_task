from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Task
from .serializers import TaskSerializer
from users.permissions import IsInstructor
from rest_framework_simplejwt.authentication import JWTAuthentication


class TaskListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY, description="Filter by task title", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Filter by task status (e.g., 'pending', 'in_progress', 'completed')",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'created_at', openapi.IN_QUERY, description="Filter by task creation date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request):
        if request.user.user_type == 'client':
            queryset = Task.objects.filter(user=request.user)
        else:
            queryset = Task.objects.all()

        title = request.query_params.get('title')
        status = request.query_params.get('status')
        created_at = request.query_params.get('created_at')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if status:
            queryset = queryset.filter(status=status)
        if created_at:
            queryset = queryset.filter(created_at__date=created_at)

        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={201: TaskSerializer()}
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    @swagger_auto_schema(responses={200: TaskSerializer()})
    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if request.user.user_type == 'client' and task.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TaskSerializer)
    def put(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if request.user.user_type == 'client' and task.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
