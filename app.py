import json
import os
import tempfile
import boto3
import docx
import streamlit as st
from pypdf import PdfReader 
from botocore.exceptions import ClientError

# Set browser tab title and page layout
st.set_page_config(page_title="Campus Study Assistant", page_icon="📚", layout="centered")

def extract_text_from_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()  # Get file extension

    # Write the uploaded byte stream to a temporary local file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext)as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name 

    extracted_text = ""

    # read the temporary file based on its extension and extract text accordingly
    try:
        if ext == ".pdf":
            reader = PdfReader(temp_file_path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text:
                    extracted_text += f"\n--- Page {page_num} ---\n{text}"

        elif ext == ".docx":
            doc = docx.Document(temp_file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            extracted_text = "\n".join(paragraphs)

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)  # Clean up the temporary file
    return extracted_text

# connects to Bedrock and specifies Cluade Haiku as our model.
def analyze_with_bedrock(combined_document_text):
    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name= "us-east-1"
    )

    model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Construct the prompt for Bedrock with the extracted document content
    prompt = f"""
You are an expert academic tutor. Analyze the following combined coursework document and provide a single unified study guide:
1. Executive Summary (Comprehensive overview of all provided materials in 3-5 sentences).
2. Key Concepts & Definations (Synthesized bullet points across all documents).
3. Potential Exam Questions (5 high-yield exam questions covering all topics presented).

Combined Document Content:
{combined_document_text}
""" 
    # Construct the payload for the Bedrock API call
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}]
    }
    # convert the payload to JSON and invoke the model to get the response
    response = bedrock.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )
    response_body = json.loads(response.get("body").read())
    return response_body["content"][0]["text"]

# ----STREAMLIT UI LAYOUT----
st.title("📚 Campus Study Assistant :")
st.caption("Powered by Anthropic Claude Haiku via Amazon Bedrock")

st.markdown("""
Upload your lecture notes, slide decks, or syllabus ('.pdf' or 'docx') to receive a concise summary, key concepts, and potential exam questions.
""")

# Create a drag-an-drop file upload box
uploaded_files = st.file_uploader(
    "Upload your coursework document", type=["pdf", "docx"], accept_multiple_files = True
        )

if uploaded_files:
    st.info(f"📄 Loaded **{len(uploaded_files)}** file(s) for this unit")

    if st.button("Generate Master Study Guide", type="primary"):
        with st.spinner("Combining document contents and generating master study guide..."):
            try:
                combined_text_list = []

                # 1. Gather text from all uploaded files
                for file in uploaded_files:
                    text = extract_text_from_file(file)
                    if text.strip():
                        combined_text_list.append(f"=== DOCUMENT: {file.name} ===\n{text}")

                full_unit_text = "\n\n".join(combined_text_list)

                # 2. Check if text exists
                if not full_unit_text.strip():
                    st.error("Could not extract readable text from the uploaded files.")
                else:
                    # 3. Call Bedrock ONCE with the combined text
                    master_summary = analyze_with_bedrock(full_unit_text)

                    # 4. Display the single combined output
                    st.success("Master study guide generated successfully!")
                    st.subheader("📖 Master Unit Study Guide")
                    st.markdown(master_summary)

            except ClientError as e:
                st.error(f"AWS Error: {e}")
            except Exception as e:
                st.error(f"Error processing documents: {e}")



