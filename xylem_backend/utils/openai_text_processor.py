from openai import OpenAI
from difflib import SequenceMatcher
from django.conf import settings
import json


def process_text_with_openai(text):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
    You are an expert information extractor. Given a natural, unstructured text describing a missing person report, extract the information and format it into this JSON structure:

{{
    "name": "",
    "age":  <integer>,
    "gender": "",
    "clothing_description": "",
    "last_seen_location": "",
    "last_seen_datetime": "",    
    "note": <any additional notes>
}}

- Always output valid JSON.
- Use ISO 8601 format for datetime (e.g., "2025-06-01T15:30:00Z").
- Leave fields empty (`""` or `null`) if information is missing.
- Only extract from the text provided.
- Ignore irrelevant info.

Now, here is the text:


{text}

if the text does not contain any information about a missing person, return an empty JSON object: {{}}
    """

    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that writes missing person notices.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return json.loads(response.choices[0].message.content.strip())


def summarize_text(text):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
    You are a summarization expert. Given a JSON data containing information about a missing person, summarize the key details in a table format.
    Here is the JSON data:
    {text}
    Please provide a concise summary in a table format.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes missing person reports.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()




def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def matching_score(str1, str2):
    parts1 = [p.strip() for p in str1.split(',')]
    parts2 = [p.strip() for p in str2.split(',')]
    
    total_score = 0
    matches = 0

    for part1 in parts1:
        for part2 in parts2:
            score = similarity(part1, part2)
            if score > 80:  # Consider it a match if similarity is over 80%
                total_score += score
                matches += 1
                break  # Avoid counting the same part twice

    if matches == 0:
        return 0
    return total_score / matches  # Average of matched scores
   
