# Speechless Analytics

> We listen. AI corrects. Data speaks.

## Purpose

This application is intended to be used to transcribe meeting notes. The application will save the notes as a .csv file, correct it with basic punctuation, add  5 calculated columns, and produce analysis in the form of report, which will include a short summary of the meeting as well as numerical analysis of the meeting.

---

## Installation

To download the application, please use one of the options below depending on your operating system. Additionally, you will need your GEMINI API key and Internet connection.

**Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Optional: if activation is blocked, run a temporary PowerShell bypass (current session only):
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
> Then run: `.venv\Scripts\Activate.ps1`
> If activation is still blocked, run scripts directly with: `.venv\Scripts\python.exe your_script.py`

---

## How to Run

Set your Gemini API key:

```bash
export GEMINI_API_KEY="your_key_here"
```

Run each stage in order:

```bash
python src/vosk_microphone_black_box.py   # Stage 1: Record and transcribe
python src/ai_correction.py               # Stage 2: AI correction
python src/enriched.py                    # Stage 3: Enrichment
python src/validation.py                  # Stage 4: Validation and analysis
```

View the summary and launch the UI:

```bash
python main.py
python3 -m http.server 8000
```

Then open: http://localhost:8000/ui.html

---

## Output Expectations

When the application runs, it produces the following in order:

1. **Record and transcribe:** Each speaker's turn is recorded and transcribed by Vosk into a `transcript.csv`.By [Angela](https://github.com/angl-l) 
2. **AI correction:** Each raw transcript is sent to Gemini (UsingGemini API key) with the prompt , which fixes spelling, punctuation, and capitalisation without changing the meaning, adding a `corrected text` column and saved in `transcript_corrected.csv`.By [Rihanna](https://github.com/RihannaP) 
3. **Enrichment:** Enrichment: The following 5 calculated columns are added to the corrected csv dataset from Stage 2, using Python and pandas dataframe: `question_flag`, `num_words`, `text_size_chars`, `speech_rate_wps`, and `speaker_turn_id` and saved in `transcript_corrected_enriched.csv`.By [Elena](https://github.com/elenagbnv)
4. **Validation & Analysis:** The dataset is checked before analysis (at least 25 rows, no missing required values, and correct data types). Clear messages are printed if any check fails and saved in `validation_result.csv`. A short summary of the meeting is then produced covering total speaking time, who spoke and how often, who asked the most questions, and each speaker's average speech rate and saved in `analysis_correction_comparison.csv` ,`analysis_metrics_summary.csv`, `analysis_speaker_stats.csv` and `analysis_speaker_details.csv`. By [Solomon](https://github.com/Solomon-get)
5. **Report:** Running `main.py` prints a full console report of all stages including sample data, speaker statistics, and analytics. It also saves `pipeline_results.json` which is used by the UI. Opening `ui.html` in a browser displays all pipeline stages in a visual format with tables and metric cards. By [Rihanna](https://github.com/RihannaP) 

The final cleaned and enriched dataset is saved as `transcript_corrected_enriched.csv`.

---

## Time and Space Complexity

The time and space complexity of the first stage of the application which listens and transcribes line by line is O(n) for both space and time. This is because it must process each line once and write it into the csv file every time.

The time and space complexity of the second stage of the application, which sends each raw transcript to the Gemini model for AI correction, is O(n) for both time and space. This is because it makes a single pass over the n rows of the dataset, sending each transcript to Gemini exactly once, applying basic corrections to the result, and storing each corrected sentence in a list before writing them all into a new CSV file. The space is also O(n) because the whole dataset is loaded into a pandas DataFrame and an equally sized list of corrected sentences is held in memory at the same time.

Time complexity for stage three, where the transcribed dataset is enriched with 5 calculated columns is O(n × m) in the worst case, where n is 25 (rows) and m is the length of a single line. Length of a single line (m) is considered in time complexity because it is used for the calculated column `text_size_chars`. Space complexity is O(n × m) because we store another copy of the file during creation of calculated columns.

The time complexity for the last stage is O(n) because the operation runs in linear time. The space complexity is O(n × m) because the full dataset must be loaded into memory as well as the extra columns to allow for analysis.

---

## Use of AI

- **AI assistant** was used to help debug code and structure UI (Icon and Emoji for the report).
- **The Copilot** icon tag under Contributors of our repo is due to a code push by one of our team members who has Copilot functionality enabled in both the environments (VS and Git). Copilot was not used to produce any part of the code for this project.

All code was reviewed, tested, and adapted by the team. Every team member understands the code they submitted and can explain it.

---

## Team


[Angela](https://github.com/angl-l)  |
[Elena](https://github.com/elenagbnv) |
[Rihanna](https://github.com/RihannaP) |
[Solomon](https://github.com/Solomon-get)

## Video
[Video](https://birkbeckuol-my.sharepoint.com/:v:/r/personal/lgiral01_student_bbk_ac_uk/Documents/Big%20Data%20Analytics/Speechless%20Analytics.mp4?csf=1&web=1&e=xyciP9&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)

Birkbeck University · 2026
