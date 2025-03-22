import fitz  # PyMuPDF for text extraction
import google.generativeai as genai  # Google Gemini AI
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import traceback
import re

# Configure Google Gemini AI
GEMINI_API_KEY = genai.configure(api_key="AIzaSyAR3ZxLtdFLD34o14Zg23KjRTbQwDgzA_I")  # Ensure API key is set in the environment


class UploadAndSummarizePDFView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # No title is needed anymore, just ensure we are handling file data correctly
        pdf_files = request.FILES.getlist("pdf_file")  # Allow multiple PDFs

        if not pdf_files:
            return Response({"error": "No PDF files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        try:
            for pdf_file in pdf_files:
                # Extract text from PDF
                extracted_text = extract_text_from_pdf(pdf_file)

                # Analyze extracted content for financial details and summary
                analysis = analyze_project_funds(extracted_text)

                # Store results with the PDF file's name and the analysis
                results.append({
                    "fileName": pdf_file.name,
                    "analysis": analysis
                })

            # Return analysis results as the response
            return Response({"results": results}, status=status.HTTP_200_OK)

        except Exception as e:
            error_trace = traceback.format_exc()  # Capture full error traceback
            print(f"Error processing request: {error_trace}")  # Log for debugging purposes
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF using PyMuPDF"""
    try:
        pdf_file.seek(0)  # Ensure we're reading from the start of the file
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Open PDF from the file stream
        text = "\n".join([page.get_text("text") for page in doc])

        if not text.strip():  # If no text was extracted
            print("Warning: No text extracted from PDF.")
            return "No extractable text found in the PDF file."

        print(f"Extracted {len(text)} characters from PDF.")  # Debugging line to log extracted text length
        return text
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")  # Log PDF extraction errors
        return "Error extracting text from PDF."


def analyze_project_funds(text):
    """Extract structured financial details using regex and generate a project summary using Gemini AI."""
    if not text.strip():
        return {"error": "No meaningful content extracted from the document."}

    try:
        ### Step 1: Extract financial details using regex ###
        def extract_amount(pattern):
            match = re.search(pattern, text)
            return int(match.group(1).replace(",", "")) if match else 0

        # Extracting financial details using regex
        financial_details = {
            "totalBudget": extract_amount(r"Total Budget:\s*\$(\d{1,3}(?:,\d{3})*)"),
            "fundsSpent": extract_amount(r"Funds Spent:\s*\$(\d{1,3}(?:,\d{3})*)"),
            "remainingFunds": extract_amount(r"Remaining Funds:\s*\$(\d{1,3}(?:,\d{3})*)"),
            "percentageUtilized": round(
                (extract_amount(r"Funds Spent:\s*\$(\d{1,3}(?:,\d{3})*)") /
                 extract_amount(r"Total Budget:\s*\$(\d{1,3}(?:,\d{3})*)")) * 100, 2)
        }

        # Extract expenditure breakdown
        expenditure_breakdown = []
        lines = text.split("\n")
        current_category = None
        total_spent = 0
        subcategories = []

        for line in lines:
            category_match = re.match(r"•\s*(.+?):\s*\$(\d{1,3}(?:,\d{3})*)", line)
            subcategory_match = re.match(r"o\s*(.+?):\s*\$(\d{1,3}(?:,\d{3})*)", line)

            if category_match:
                # Save previous category before switching
                if current_category:
                    expenditure_breakdown.append({
                        "category": current_category,
                        "totalSpent": total_spent,
                        "subCategories": subcategories
                    })

                # Start new category
                current_category = category_match.group(1).strip()
                total_spent = int(category_match.group(2).replace(",", ""))
                subcategories = []  # Reset subcategories list for new category

            elif subcategory_match and current_category:
                # Append subcategories under the current category
                subcategories.append({
                    "name": subcategory_match.group(1).strip(),
                    "amount": int(subcategory_match.group(2).replace(",", ""))
                })

        # Add the last processed category if any
        if current_category:
            expenditure_breakdown.append({
                "category": current_category,
                "totalSpent": total_spent,
                "subCategories": subcategories
            })

        ### Step 2: Generate project summary using Gemini AI ###
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"Summarize the following government project fund assessment. "
            f"Ensure the summary highlights financial trends, budget efficiency, risks, and recommendations:\n\n{text}"
        )

        # Check if response has the 'text' attribute (summary)
        summary = response.text.strip() if hasattr(response, 'text') else "Error: No valid response."

        ### Step 3: Return structured JSON output ###
        return {
            "project": "Extracted Project Name",  # Placeholder for project name
            "financialDetails": financial_details,
            "summary": summary
        }

    except Exception as e:
        print(f"Gemini API error: {str(e)}")  # Log any errors related to the Gemini API
        return {"error": "Error generating analysis."}
