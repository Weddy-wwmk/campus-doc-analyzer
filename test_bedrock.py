import json
from typing_extensions import runtime
import boto3
from botocore.exceptions import ClientError

def analyze_coursework_sample():
    # 1. Initialize the Bedrock Runtime client
    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1" 
    )

    # 2. Set the Anthropic Claude 4.5 Haiku Model 
    model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    # 3. Define a question/prompt
    sample_prompt = (
        "I am preparing for my technical coursework exams."
        "Briefly explain the primary difference between Relational (SQL) and NoSQL databases" 
        "in 3 bullet points with a student-friendly focus."
    )

    # 4. Construct the Anthropic Messages API payload
    # Packaging the prompt into a JSON message box (payload)
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": sample_prompt
            }
        ]
    }

    try: 
        print("Sending request to Anthropic Claude 4.5 Haiku via Bedrock...\n"
            )

        # 5. Invoke the model by sending the JSON box across the internt to AWS Bedrock
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        # 6. Parse (unpack) AWS response and display the Claude's output
        response_body = json.loads(response.get("body").read())
        output_text = response_body["content"][0]["text"]

        print("--- Claude 4.5 Haiku Output ---")
        print(output_text.strip())

    except ClientError as e:
        # Handle any AWS account or network errors.
            print(f"AWS Error: {e}") 

        # Execute the function when the file runs.
if __name__ == "__main__":
    analyze_coursework_sample()


      

    