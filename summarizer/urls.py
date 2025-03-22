from django.urls import path
from .views import UploadAndSummarizePDFView

urlpatterns = [
    path("upload-summarize-pdf/", UploadAndSummarizePDFView.as_view(), name="upload_summarize_pdf"),

]
