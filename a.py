from openai import OpenAI

API_KEY = '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'# Replace with your actual API key
client = OpenAI(api_key=API_KEY)

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
