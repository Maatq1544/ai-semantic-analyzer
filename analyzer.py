import pandas as pd
import os
import json
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import sys

# Load credentials from environment or direct (Tommy style: safety first)
DEEPSEEK_API_KEY = "sk-d8f8b50e8c644385b40767ff88b2892d"
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

def analyze_row(row_data, task_description, columns):
    """Analyze a single row based on a dynamic task with precise JSON enforcement."""
    row_context = "\n".join([f"{col}: {row_data.get(col, '')}" for col in columns])
    
    prompt = f"""
    You are a professional Data Analyst.
    
    TASK:
    {task_description}
    
    DATA TO ANALYZE:
    {row_context}
    
    REQUIREMENTS:
    1. Return ONLY a flat JSON object.
    2. The keys must correspond exactly to the data points requested in the task.
    3. Do not include any explanations, markdown, or nested objects.
    4. If data is missing for a specific point, use "N/A".
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Return only flat JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            timeout=20
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"analysis_error": str(e)}

def process_data(input_path, task_description):
    # Support CSV or Excel
    try:
        if input_path.endswith('.csv'):
            df = pd.read_csv(input_path)
        else:
            df = pd.read_excel(input_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print(f"Loaded {len(df)} rows. Starting analysis...")
    
    columns = df.columns.tolist()
    
    # Process rows in parallel (Tommy's multi-threading)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(analyze_row, row.to_dict(), task_description, columns) for _, row in df.iterrows()]
        results = [f.result() for f in futures]
    
    # Merge results with original data
    res_df = pd.DataFrame(results)
    final_df = pd.concat([df.reset_index(drop=True), res_df.reset_index(drop=True)], axis=1)
    
    output_path = f"analyzed_{os.path.basename(input_path)}"
    if input_path.endswith('.csv'):
        final_df.to_csv(output_path, index=False)
    else:
        final_df.to_excel(output_path, index=False)
        
    print(f"Done. File saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyzer.py <file_path> '<task_description>'")
    else:
        process_data(sys.argv[1], sys.argv[2])
