"""Stage 2: AI Correction using Gemini API.

Reads transcript.csv, sends each raw_script value to Gemini for correction
(spelling, punctuation, capitalisation, meaning preserved), and writes
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

PROMPT = (
    "You are a transcript editor. "
    "Always correct the spelling, punctuation, and capitalisation of the sentence below, "
    "even if it looks mostly correct. "
    "Always capitalise the first word. Always end with a punctuation mark (. or ?). "
    "Do not change the meaning. "
    "Return only the corrected sentence with no extra explanation."
)


def basic_corrections(text):
    text = text.strip()        # removes trailing spaces
    if text == "":
           return text          # nothing to correct
    text = text[0].upper() + text[1:]  # capitalises first letter
    if text[-1] not in ".?!":
        text += "."            # adds full stop if missing
    return text

# Build the prompt using the system prompt and the raw transcript
def AI_correct_transcript(prompt):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    result = response.text.strip()
    return basic_corrections(result)
    


def main():
    
    df = pd.read_csv(INPUT_CSV)
    if "raw_script" not in df.columns:
        raise ValueError(f"Expected column 'raw_script' not found in {INPUT_CSV}.")

    corrected = []
    for i, row in df.iterrows():
        raw = str(row["raw_script"])
        print(f"Correcting row {i + 1}/{len(df)}: {raw!r}")
        try:
            # Send raw transcript to Gemini for correction
            fixed = AI_correct_transcript(f"{PROMPT}\n\n{raw.strip()}")

        except Exception as e:
            print(f"  Warning: {e}. Applying basic corrections.")
            # Apply basic corrections as a safety net
            fixed = basic_corrections(raw)
            
        corrected.append(fixed)
        # small delay to stay within free-tier rate limits
        time.sleep(4)

    # Find the position after 'raw_script' column to insert 'text' next to it
    insert_pos = df.columns.get_loc("raw_script") + 1 
    # Insert 'text' column right after 'raw_script'
    df.insert(insert_pos, "text", corrected)

    # Save the updated dataframe to a new CSV file
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone. Corrected CSV saved to: {OUTPUT_CSV}")
    print(df[["name", "raw_script", "text"]].to_string(index=False))


if __name__ == "__main__":
    main()
