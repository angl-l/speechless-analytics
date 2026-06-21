"""Main pipeline summary.

Displays the results of all pipeline stages without re-running them.
Reads the existing CSV files and prints a summary of each stage.
Also saves results to pipeline_results.json for the UI.

Run:
    python main.py
"""

import json
from pathlib import Path
import pandas as pd

# File paths for each stage output
FILE_RAW = Path("transcript.csv")
FILE_CORRECTED = Path("transcript_corrected.csv")
FILE_ENRICHED = Path("transcript_corrected_enriched.csv")
FILE_SPEAKER_STATS = Path("analysis_speaker_stats.csv")
FILE_METRICS = Path("analysis_metrics_summary.csv")
FILE_SPEAKER_DETAILS = Path("analysis_speaker_details.csv")
OUTPUT_JSON = Path("pipeline_results.json")


def show_stage1(df):
    print("\n" + "="*50)
    print(" STAGE 1: Speech Transcription (Vosk)")
    print("="*50)
    print("transcript.csv found -", len(df), "rows")

    # Print first 3 rows as a sample
    print("\nSample:")
    for i, row in df.head(3).iterrows():
        print(" ", row["timestamp"], "|", row["name"], "->", row["raw_script"].strip(), "|", row["time_taken_sec"])



def show_stage2(df):
    print("\n" + "="*50)
    print(" STAGE 2: AI Correction (Gemini)")
    print("="*50)
    print("transcript_corrected.csv found -", len(df), "rows")

    # Print first 3 rows as a sample
    print("\nSample:")
    for i, row in df.head(3).iterrows():
        print(" ", row["timestamp"], "|", row["name"], "->", row["raw_script"].strip(), "->", row["text"].strip(), ",", round(float(row["time_taken_sec"]),2))



def show_stage3(df):
    print("\n" + "="*50)
    print(" STAGE 3: Enrichment")
    print("="*50)
    print("transcript_corrected_enriched.csv found -", len(df), "rows")
    
    # Print first 5 rows as a sample
    print("\nSample:")
    for i, row in df.head(5).iterrows():
        print(" ", row["timestamp"], "|", row["name"],
              "| Raw Script:", row["raw_script"].strip(),
              "| Text:", row["text"].strip(),
              "| Time(Sec):", round(float(row["time_taken_sec"]),2),
              "| question:", row["question_flag"],
              "| words:", row["num_words"],
              "| chars:", row["text_size_chars"],
              "| rate:", row["speech_rate_wps"], "wps",
              "| turn:", row["speaker_turn_id"])


def show_stage4(speaker_stats, metrics, speaker_details):
    print("\n" + "="*50)
    print(" STAGE 4: Validation & Analysis")
    print("="*50)

    # Read validation results and show summary
    validation_results = pd.read_csv("validation_results.csv")
    total_rows = len(validation_results)
    passed = len(validation_results[validation_results["status"] == "PASS"])
    failed = total_rows - passed

    print("Validation results: ", passed, "passed,", failed, "failed out of", total_rows, "rows")

   # Print speaker statistics
    print("\nSPEAKER STATISTICS")
    for i, row in speaker_stats.iterrows():
        print(" ", row["name"], "-",
              row["total_turns"], "turns |",
              row["total_words"], "words |",
              row["total_raw_chars"], "Characters |",
              row["total_corr_chars"], "Corrected Characters |",
              row["total_time"], "seconds |",
              row["total_questions"], "questions |",
              row["avg_speech_rate"], "wps")
        
    # Print overall metrics
    print("\nMETRICS SUMMARY")
    print("  Total raws:        ", metrics["total_rows"][0])
    print("  Total speaking time:  ", metrics["total_speaking_time_sec"][0], "seconds")
    print("  Avg speaking time:    ", metrics["avg_speaking_time_per_speaker_sec"][0], "seconds")
    print("  Avg raw chars:        ", metrics["avg_raw_chars"][0])
    print("  Avg corrected chars:  ", metrics["avg_corrected_chars"][0])
    print("  Avg length change:    ", metrics["avg_length_change"][0])
    print("  Total questions:      ", metrics["total_questions"][0])

    # Load and print speaker details analysis
    print("\nANALYSIS")
    for i, row in speaker_details.iterrows():
        print(" ", row["metric"], "-", row["name"], "-", row["value"])


def save_json(df_raw, df_corrected, df_enriched, speaker_stats, metrics, speaker_details):
    
    # Build stage 1 sample list — include timestamp, name, raw transcript and time
    stage1_sample = []
    for i, row in df_raw.head(3).iterrows():
        stage1_sample.append({
            "timestamp": row["timestamp"],
            "name": row["name"],
            "text": row["raw_script"].strip(),
            "time_taken_sec": round(float(row["time_taken_sec"]), 2)
        })

    # Build stage 2 sample list — include timestamp, name, raw, corrected and time
    stage2_sample = []
    for i, row in df_corrected.head(3).iterrows():
        stage2_sample.append({
            "timestamp": row["timestamp"],
            "name": row["name"],
            "raw_script": row["raw_script"].strip(),
            "text": row["text"].strip(),
            "time_taken_sec": round(float(row["time_taken_sec"]), 2)
        })

    # Build stage 3 sample list — include timestamp, name, text, time, question, words, chars, rate
    stage3_sample = []
    for i, row in df_enriched.head(5).iterrows():
        stage3_sample.append({
            "timestamp": row["timestamp"],
            "name": row["name"],
            "text": row["text"].strip(),
            "time_taken_sec": round(float(row["time_taken_sec"]), 2),
            "question_flag": bool(row["question_flag"]),
            "num_words": int(row["num_words"]),
            "text_size_chars": int(row["text_size_chars"]),
            "speech_rate_wps": float(row["speech_rate_wps"])
        })
                
    # Put everything together in one dictionary
    results = {
        "stage1": {"rows": len(df_raw), "sample": stage1_sample},
        "stage2": {"rows": len(df_corrected), "sample": stage2_sample},
        "stage3": {"rows": len(df_enriched), "sample": stage3_sample},
        "stage4": {
            "speaker_stats": speaker_stats.to_dict(orient="records"),
            "speaker_details": speaker_details.to_dict(orient="records"),
            "metrics": metrics.to_dict(orient="records")[0],
        }
    }

    # Save to JSON file for the UI
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to", OUTPUT_JSON, "for the UI")

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" MEETING SPEECH ANALYTICS PIPELINE")
    print("="*50)

    # Load all CSV files once
    df_raw = pd.read_csv(FILE_RAW)
    df_corrected = pd.read_csv(FILE_CORRECTED)
    df_enriched = pd.read_csv(FILE_ENRICHED)
    speaker_stats = pd.read_csv(FILE_SPEAKER_STATS)
    metrics = pd.read_csv(FILE_METRICS)
    speaker_details = pd.read_csv(FILE_SPEAKER_DETAILS)

    # Run each stage
    show_stage1(df_raw)
    show_stage2(df_corrected)
    show_stage3(df_enriched)
    show_stage4(speaker_stats, metrics, speaker_details)

    # Save results to JSON for the UI
    save_json(df_raw, df_corrected, df_enriched, speaker_stats, metrics, speaker_details)

    print("\n" + "="*50)
    print(" PIPELINE COMPLETE")
    print("="*50)
