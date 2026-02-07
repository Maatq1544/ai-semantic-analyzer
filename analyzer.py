import pandas as pd
import os
import json
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import sys

# Load credentials
DEEPSEEK_API_KEY = "sk-d8f8b50e8c644385b40767ff88b2892d"
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

def analyze_row(row_data, task_description, columns):
    """Analyze a single row based on a dynamic task."""
    row_context = ", ".join([f"{col}: {row_data.get(col, '')}" for col in columns])
    
    prompt = f"""
    Task: {task_description}
    
    Data to analyze:
    {row_context}
    
    Return the result ONLY as a flat JSON object where keys are the new data points requested in the task. 
    Do not include nested objects.
    Example: {{"gender": "male", "sentiment": "positive"}}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional data analyst. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            timeout=15
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def process_data(input_path, task_description):
    # Support CSV or Excel
    if input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    else:
        df = pd.read_excel(input_path)
        
    print(f"Loaded {len(df)} rows. Analyzing based on task: {task_description}")
    
    columns = df.columns.tolist()
    
    # Process rows in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(analyze_row, row.to_dict(), task_description, columns) for _, row in df.iterrows()]
        results = [f.result() for f in futures]
    
    # Flatten results into a DataFrame and join with original
    res_df = pd.DataFrame(results)
    final_df = pd.concat([df.reset_index(drop=True), res_df.reset_index(drop=True)], axis=1)
    
    output_path = f"analyzed_{os.path.basename(input_path)}"
    if input_path.endswith('.csv'):
        final_df.to_csv(output_path, index=False)
    else:
        final_df.to_excel(output_path, index=False)
        
    print(f"Analysis complete. Results saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyzer.py <file_path> '<task_description>'")
    else:
        process_data(sys.argv[1], sys.argv[2])
