# Speechless Analytics Application

## Purpose

This application is intended to be used to transcribe meeting notes. 
The application will save the notes as a .csv file which will then be analysed to produce an output report which will include a short summary of the meeting as well as numerical analysis of the meeting. 

## Installation

To download the application, please use one of the options below depending on your operating system. Additionally, you will need your GEMINI API key and Internet connection.
-	Mac: 
o	Download the repo 
o	Create and activate a virtual environment:
	```python3 -m venv .venv```
	```source .venv/bin/activate```
o	Install dependencies:
	```Pip install -r requirements.txt```
-	Windows:
o	Download the repo
o	Create and activate a virtual environment:
	```python -m venv .venv```
	```.venv\bin\Activate.ps1```
	Optional: temporary PowerShell bypass (current session only): Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass Then run: .venv\Scripts\Activate.ps1
If activation is blocked, run scripts directly with: .venv\Scripts\python.exe your_script.py

o	Install dependencies:
	```pip install -r requirements.txt```


## Output Expectations
When the application runs, it produces the following in order:
1.	Record and transcribe: each speaker's turn is recorded and transcribed by Vosk into a transcript CSV.
2.	AI correction: each raw transcript is sent to Gemini, which fixes spelling, punctuation, and capitalisation without changing the meaning, adding a corrected text column.
3.	Enrichment: Python adds 5 calculated columns: question_flag, num_words, text_size_chars, speech_rate_wps, and speaker_turn_id.
4.	Validation: the dataset is checked before analysis (at least 25 rows, no missing required values, and correct data types). Clear messages are printed if any check fails.
5.	Analysis report: a short summary of the meeting covering total speaking time, who spoke and how often, who asked the most questions, and each speaker's average speech rate.
The final cleaned and enriched dataset is saved in the resources folder as transcript_corrected_enriched.csv.
## Time and Space Complexity
The time and space complexity of the first stage of the application which listens and transcribes line by line is O(n) for both space and time. This is because it must process each line once and write it into the csv file every time.
The time and space complexity of the second stage of the application, which sends each raw transcript to the Gemini model for AI correction, is O(n) for both time and space. This is because it makes a single pass over the n rows of the dataset, sending each transcript to Gemini exactly once, applying basic corrections to the result, and storing each corrected sentence in a list before writing them all into a new CSV file. The space is also O(n) because the whole dataset is loaded into a pandas DataFrame and an equally sized list of corrected sentences is held in memory at the same time.
Time complexity for stage three, where the transcribed dataset is enriched with 5 calculated columns is O(n * m) in the worst case, where n is 25 (rows) and m is length of a single line. Length of a single line (m) is considered in time complexity because it is used for calculated column ext_size_chars. Space complexity is O(n * m) because we store another copy of the file during creation of calculated columns. Addition of extra columns requires both - extra time and space. The time complexity for the last stage is O(n) because the operation runs in linear time. The space complexity is O(n x m) because the full dataset must be loaed into memory as well as the extra columns to allow for analysis.

