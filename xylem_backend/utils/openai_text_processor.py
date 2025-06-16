from django.conf import settings
import openai


def process_text_with_openai(text):
    openai.api_key = settings.OPENAI_API_KEY

    prompt = f"""
    You are an expert information extractor. Given a natural, unstructured text describing a missing person report, extract the information and format it into this JSON structure:

{{
    "name": "",
    "age":  <integer>,
    "gender": "",
    "clothing_description": "",
    "last_seen_location": "",
    "last_seen_datetime": "",    
    "note": <any additional notes>,
}}

- Always output valid JSON.
- Use ISO 8601 format for datetime (e.g., "2025-06-01T15:30:00Z").
- Leave fields empty (`""` or `null`) if information is missing.
- Only extract from the text provided.
- Ignore irrelevant info.

Now, here is the text:


{text}
    """

    response = openai.ChatCompletion.create(
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

    print(response.choices[0].message["content"])
