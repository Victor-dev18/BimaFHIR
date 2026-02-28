import os
import json
from dotenv import load_dotenv
from llama_parse import LlamaParse
from groq import AsyncGroq

# Load environment variables FIRST
load_dotenv()

# Initialize the Groq Client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def extract_plan_data(file_path: str) -> dict:
    print(f"Starting extraction for: {file_path}")
    
    print("Parsing PDF with LlamaParse...")
    parser = LlamaParse(
        api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        result_type="markdown",
        verbose=True
    )
    
    documents = await parser.aload_data(file_path)
    markdown_content = "\n".join([doc.text for doc in documents])
    print(f"Successfully parsed {len(documents)} pages into Markdown.")

    print("Sending to Groq (Llama-3.3-70B) for blazing fast extraction...")
    
    system_instruction = """
    You are an expert medical insurance underwriter and FHIR data extraction agent.
    Your job is to read the provided insurance policy document and extract the exact terms, benefits, and exclusions.
    Pay special attention to tabular data for sub-limits (e.g., room rent, maternity) and ICD codes for exclusions.
    
    You MUST return a valid JSON object with this EXACT structure:
    {
      "insurer_name": "Name of the insurance company",
      "plan_name": "Name of the specific policy",
      "plan_type": "e.g., Indemnity, Base, Floater",
      "benefits": [
         {
           "benefit_name": "Name (e.g., Room Rent, Mental Illness)", 
           "limit": "Financial limit if any", 
           "waiting_period": "Waiting period if any"
         }
      ],
      "exclusions": [
         {
           "exclusion_type": "Type of exclusion", 
           "icd_codes": ["Code1", "Code2"]
         }
      ]
    }
    If a limit, waiting period, or ICD code is not mentioned, leave the field as null or an empty list.
    """

    try:
        # Trimmed to 35,000 characters (~8,000 tokens) to stay safely under the 12k TPM limit
        optimized_content = markdown_content[:35000] 

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Policy Document Content:\n{optimized_content}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 
        )
        
        extracted_data = json.loads(response.choices[0].message.content)
        print("Extraction complete! JSON successfully generated.")
        
        return extracted_data
        
    except Exception as e:
        print(f"Error during AI extraction: {str(e)}")
        raise e