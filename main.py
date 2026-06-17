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


FILE_RAW = Path("transcript.csv")
FILE_CORRECTED = Path("transcript_corrected.csv")
FILE_ENRICHED = Path("transcript_corrected_enriched.csv")
FILE_SPEAKER_STATS = Path("analysis_speaker_stats.csv")
FILE_METRICS = Path("analysis_metrics_summary.csv")
OUTPUT_JSON = Path("pipeline_results.json")


def show_stage1():
    print("\n" + "="*50)
    print(" STAGE 1: Speech Transcription (Vosk)")
    print("="*50)

    if not FILE_RAW.exists():
        print("❌ transcript.csv not found")
        return None

    df = pd.read_csv(FILE_RAW)
    print(f"✅ transcript.csv found — {len(df)} rows")
    print("\nSample:")
    for _, row in df.head(3).iterrows():
        print(f"  {row['name']:<10} →  {row['raw_script'].strip()}")
    return df


def show_stage2():
    print("\n" + "="*50)
    print(" STAGE 2: AI Correction (Gemini)")
    print("="*50)

    if not FILE_CORRECTED.exists():
        print("❌ transcript_corrected.csv not found")
        return None

    df = pd.read_csv(FILE_CORRECTED)
    print(f"✅ transcript_corrected.csv found — {len(df)} rows")
    print("\nSample:")
    for _, row in df.head(3).iterrows():
        print(f"  {row['name']:<10} →  {row['text'].strip()}")
    return df


def show_stage3():
    print("\n" + "="*50)
    print(" STAGE 3: Enrichment")
    print("="*50)

    if not FILE_ENRICHED.exists():
        print("❌ transcript_corrected_enriched.csv not found")
        return None

    df = pd.read_csv(FILE_ENRICHED)
    print(f"✅ transcript_corrected_enriched.csv found — {len(df)} rows")
    print("\nSample:")
    for _, row in df.head(3).iterrows():
        print(f"  {row['name']:<10} | words: {row['num_words']:>2} | chars: {row['text_size_chars']:>3} | rate: {row['speech_rate_wps']} wps | question: {str(row['question_flag']):<5} | turn: {row['speaker_turn_id']}")
    return df


def show_stage4(df_enriched):
    print("\n" + "="*50)
    print(" STAGE 4: Validation & Analysis")
    print("="*50)

    if not FILE_SPEAKER_STATS.exists() or not FILE_METRICS.exists():
        print("❌ Analysis files not found — run validation.py first")
        return

    print("✅ All validation checks passed")

    # Speaker stats
    speaker_stats = pd.read_csv(FILE_SPEAKER_STATS)
    print("\n📌 SPEAKER STATISTICS")
    for _, row in speaker_stats.iterrows():
        print(f"  {row['name']:<10} — {row['total_turns']} turns | {row['total_raw_chars']} raw chars | {row['total_corr_chars']} corrected chars")

    # Metrics summary
    metrics = pd.read_csv(FILE_METRICS)
    print("\n📌 OVERALL METRICS")
    print(f"  Avg raw chars:        {metrics['avg_raw_chars'][0]}")
    print(f"  Avg corrected chars:  {metrics['avg_corr_chars'][0]}")
    print(f"  Avg length change:    {metrics['avg_length_change'][0]}")

    # Enriched extras
    if df_enriched is not None:
        print("\n📌 ENRICHED METRICS")
        print(f"  Questions detected:   {df_enriched['question_flag'].sum()}")
        print(f"  Max speaker turns:    {df_enriched['speaker_turn_id'].max()}")
        print(f"  Total speaking time:  {df_enriched['time_taken_sec'].sum():.1f} seconds")
        print(f"  Avg speaking time:    {df_enriched['time_taken_sec'].mean():.1f} seconds")

    return speaker_stats, metrics


def save_json(df_raw, df_corrected, df_enriched):
    """Save all results to JSON for the UI."""

    speaker_stats = pd.read_csv(FILE_SPEAKER_STATS) if FILE_SPEAKER_STATS.exists() else None
    metrics = pd.read_csv(FILE_METRICS) if FILE_METRICS.exists() else None

    results = {
        "stage1": {
            "rows": len(df_raw),
            "sample": [
                {"name": row["name"], "text": row["raw_script"].strip()}
                for _, row in df_raw.head(3).iterrows()
            ]
        },
        "stage2": {
            "rows": len(df_corrected),
            "sample": [
                {"name": row["name"], "text": row["text"].strip()}
                for _, row in df_corrected.head(3).iterrows()
            ]
        },
        "stage3": {
            "rows": len(df_enriched),
            "sample": [
                {
                    "name": row["name"],
                    "num_words": int(row["num_words"]),
                    "text_size_chars": int(row["text_size_chars"]),
                    "speech_rate_wps": float(row["speech_rate_wps"]),
                    "question_flag": bool(row["question_flag"]),
                    "speaker_turn_id": int(row["speaker_turn_id"])
                }
                for _, row in df_enriched.head(3).iterrows()
            ]
        },
        "stage4": {
            "speaker_stats": speaker_stats.to_dict(orient="records") if speaker_stats is not None else [],
            "metrics": metrics.to_dict(orient="records")[0] if metrics is not None else {},
            "questions_detected": int(df_enriched["question_flag"].sum()),
            "total_speaking_time": round(float(df_enriched["time_taken_sec"].sum()), 1),
            "avg_speaking_time": round(float(df_enriched["time_taken_sec"].mean()), 1)
        }
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to {OUTPUT_JSON} for the UI")


if __name__ == "__main__":
    print("\n" + "="*50)
    print(" MEETING SPEECH ANALYTICS PIPELINE")
    print("="*50)

    df_raw = show_stage1()
    df_corrected = show_stage2()
    df_enriched = show_stage3()
    show_stage4(df_enriched)

    if df_raw is not None and df_corrected is not None and df_enriched is not None:
        save_json(df_raw, df_corrected, df_enriched)

    print("\n" + "="*50)
    print(" PIPELINE COMPLETE")
    print("="*50)
