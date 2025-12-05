from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Note
from .serializers import NoteSerializer

@api_view(['GET'])
def health(request):
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
class NoteListCreateAPIView(ListCreateAPIView):
    """API view to list all notes or create a new note."""
    queryset = Note.objects.all().order_by("-created_at")
    serializer_class = NoteSerializer

# PUBLIC_INTERFACE
class NoteRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, or delete a specific note."""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
