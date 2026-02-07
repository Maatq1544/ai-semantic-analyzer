import pandas as pd
import os
import json
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

# Config
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

def analyze_review(row):
    """Analyze a single review row using AI."""
    nickname = row.get('nickname', 'Unknown')
    review_text = row.get('review', '')
    
    prompt = f"""
    Analyze the following customer review:
    User Nickname: {nickname}
    Review: {review_text}
    
    Tasks:
    1. Estimate gender based on nickname (Male/Female/Unknown).
    2. Estimate age range based on slang/style (e.g., 18-25, 26-40, 40+).
    3. Determine sentiment (Positive, Negative, Neutral, Sarcastic).
    
    Return ONLY a JSON object:
    {{"gender": "...", "age_range": "...", "sentiment": "..."}}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=10
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def process_csv(input_path, output_path):
    df = pd.read_csv(input_path)
    results = []
    
    # Using ThreadPool for speed (DeepSeek is fast)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(analyze_review, [row for _, row in df.iterrows()]))
    
    res_df = pd.DataFrame(results)
    final_df = pd.concat([df, res_df], axis=1)
    final_df.to_csv(output_path, index=False)
    print(f"Finished. Saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    # process_csv('reviews.csv', 'analyzed_reviews.csv')
    pass
