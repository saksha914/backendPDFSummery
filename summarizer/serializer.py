from rest_framework import serializers
from .models import ProjectPDF, Document

class ProjectPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPDF
        fields = ["id", "pdf_file", "title", "uploaded_at"]

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "firebase_url", "description", "keywords", "uploaded_at", "last_analyzed", "analysis_result"]
        read_only_fields = ["last_analyzed", "analysis_result"]
