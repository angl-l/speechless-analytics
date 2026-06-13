"""Stage 2: AI Correction using Gemini API.

Reads transcript.csv, sends each raw_script value to Gemini for correction
(spelling, punctuation, capitalisation — meaning preserved), and writes
the result back as a new column 'text'.

Set GEMINI_API_KEY before running:
    export GEMINI_API_KEY="your_key_here"

Output: transcript_corrected.csv
"""

import os
import time
import pandas as pd
from google import genai

MODEL_NAME = "gemini-2.5-flash"
INPUT_CSV = "transcript.csv"
OUTPUT_CSV = "transcript_corrected.csv"

SYSTEM_PROMPT = (
    "You are a transcript editor. "
    "Always correct the spelling, punctuation, and capitalisation of the sentence below, "
    "even if it looks mostly correct. "
    "Always capitalise the first word. Always end with a punctuation mark (. or ?). "
    "Do not change the meaning. "
    "Return only the corrected sentence with no extra explanation."
)


def apply_basic_corrections(text: str) -> str:
    """Capitalise first letter and ensure sentence ends with punctuation."""
    text = text.strip()
    if not text:
        return text
    text = text[0].upper() + text[1:]
    if text[-1] not in ".?!":
        text += "."
    return text


def correct_transcript(client: genai.Client, raw_text: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\n{raw_text.strip()}"
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    result = response.text.strip()
    return apply_basic_corrections(result)


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)

    df = pd.read_csv(INPUT_CSV)

    if "raw_script" not in df.columns:
        raise ValueError(f"Expected column 'raw_script' not found in {INPUT_CSV}.")

    corrected = []
    for i, row in df.iterrows():
        raw = str(row["raw_script"])
        print(f"Correcting row {i + 1}/{len(df)}: {raw!r}")
        try:
            fixed = correct_transcript(client, raw)
        except Exception as e:
            print(f"  Warning: Gemini error on row {i + 1}: {e}. Applying basic corrections.")
            fixed = apply_basic_corrections(raw)
        corrected.append(fixed)
        # small delay to stay within free-tier rate limits
        time.sleep(0.5)

    # Insert 'text' column right after 'raw_script'
    insert_pos = df.columns.get_loc("raw_script") + 1
    df.insert(insert_pos, "text", corrected)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone. Corrected CSV saved to: {OUTPUT_CSV}")
    print(df[["name", "raw_script", "text"]].to_string(index=False))


if __name__ == "__main__":
    main()
