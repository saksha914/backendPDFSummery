from django.db import models
from django.core.validators import FileExtensionValidator
from datetime import datetime

class ProjectPDF(models.Model):
    pdf_file = models.FileField(
        upload_to="pdfs/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    title = models.CharField(max_length=255, default="Untitled PDF")
    extracted_text = models.JSONField(default=dict, blank=True)  # Ensure default is an empty dictionary
    summary = models.JSONField(default=dict, blank=True)  # Ensure default is an empty dictionary
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "summarizer_projectpdf"

class Document(models.Model):
    title = models.CharField(max_length=255)
    firebase_url = models.URLField(max_length=500)  # Store Firebase Storage URL
    description = models.TextField(blank=True)
    keywords = models.TextField(help_text="Comma-separated keywords for search")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_analyzed = models.DateTimeField(null=True, blank=True)
    analysis_result = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['keywords']),
        ]
