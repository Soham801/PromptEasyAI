import os

import pytest
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


@pytest.mark.skipif(
    os.getenv("PROMPTEASY_RUN_LIVE_GROQ") != "1",
    reason="Live Groq probes require PROMPTEASY_RUN_LIVE_GROQ=1.",
)
def test_live_groq_connection():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.fail("GROQ_API_KEY is required for the live Groq probe.")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("PROMPTEASY_MODEL", "openai/gpt-oss-20b"),
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
    )

    assert response.choices[0].message.content