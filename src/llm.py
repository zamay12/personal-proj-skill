import os


def call_llm(prompt: str) -> str:
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    model_name = os.getenv("MODEL_NAME", "gpt-5.5")
    client = OpenAI()
    response = client.responses.create(model=model_name, input=prompt)
    return response.output_text
