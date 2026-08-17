import json
import os
import boto3
import docx
from pypdf import PdfReader
from botocore.exceptions import ClientError


def extract_text(file_path):
    if not os.path.exists(file_path):  # checks if file exists in computer
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[
        1
    ].lower()  # split filename into 2, and converts .PDF to .pdf

    # Extract from pdf
    if ext == ".pdf":
        reader = PdfReader(file_path)
        extracted_text = ""
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                extracted_text += f"\n--- Page {page_num} ---\n{text}"
        return extracted_text  

    # Extract from docx
    elif ext == ".docx":
        doc = docx.Document(file_path)
        extracted_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                extracted_text.append(paragraph.text)
        return "\n".join(extracted_text)  # OUTSIDE the for loop

    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. Please provide a .pdf or .docx file."
        )


def summarize_coursework(file_path):
    try:
        # 1. Extract text dynamically based on file format
        print(f"Reading document: {file_path}...")
        document_text = extract_text(file_path)

        if not document_text.strip():
            print("Error: Could not extract any readable text from the file.")
            return  

        # 2. Initialize the Bedrock Runtime client
        bedrock = boto3.client(
            service_name="bedrock-runtime", region_name="us-east-1"
        )

        # 3. Active Claude Haiku Inference Profile ID
        model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

        # 4. Construct prompt with embedded document content
        prompt = f"""
You are an expert academic tutor. Analyze the following coursework document and provide:
1. An Executive Summary (3-4 sentences).
2. Key Concepts & Definitions (Bullet points).
3. Potential Exam Questions (3 questions based on the text).

Document Content:
{document_text}
"""
        # 5. Build Bedrock Payload
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,  # output length
            "temperature": 0.2,  # creativity
            "messages": [{"role": "user", "content": prompt}],
        }

        print("Sending document content to Amazon Bedrock for analysis...\n")
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )

        # 6. Parse and display output
        response_body = json.loads(response.get("body").read())
        summary_output = response_body["content"][0]["text"]

        print("=============== STUDY GUIDE SUMMARY ===============")
        print(summary_output.strip())
        print("===================================================")

    # error handling
    except ClientError as e:
        print(f"AWS Error: {e}")
    except Exception as e:
        print(f"Error processing document: {e}")


if __name__ == "__main__":
    # Pass either a .pdf or a .docx file here!
    summarize_coursework("sample_notes.pdf")