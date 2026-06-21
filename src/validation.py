"""Main pipeline summary.

This is stage 4 and 5 Displays the results of all pipeline stages without re-running them.
Reads the existing CSV files and prints a summary of each stage.
Also saves results to CSV files and pipeline_results.json for the UI.

Run:
    python validation.py
"""

import json
from pathlib import Path
import pandas as pd


# ----------------------
# FILE PATHS
# ----------------------
FILE_RAW = Path("transcript.csv")
FILE_CORRECTED = Path("transcript_corrected.csv")
FILE_ENRICHED = Path("transcript_corrected_enriched.csv")

# OUTPUT CSV FILES (Validation & Analysis results)
FILE_VALIDATION_RESULTS = Path("validation_results.csv")       # ✅ Validation pass/fail per row
FILE_SPEAKER_STATS = Path("analysis_speaker_stats.csv")        # ✅ Speaker stats
FILE_METRICS = Path("analysis_metrics_summary.csv")            # ✅ Overall metrics
FILE_SPEAKER_DETAILS = Path("analysis_speaker_details.csv")    # ✅ Most/least words, questions, time
FILE_CORRECTION_COMPARISON = Path("analysis_correction_comparison.csv")  # ✅ Raw vs corrected

OUTPUT_JSON = Path("pipeline_results.json")

REQUIRED_COLUMNS = [
    "timestamp", "name", "raw_script", "text", "time_taken_sec",
    "question_flag", "num_words", "text_size_chars", "speech_rate_wps", "speaker_turn_id"
]


# ----------------------
# STAGE 4: VALIDATION FUNCTION
# ----------------------
def validate_csv(df):
    """
    Stage 4 Validation Rules:
    - At least 25 rows
    - No missing values
    - Valid datetime
    - Numeric > 0 for time_taken_sec, num_words, speech_rate_wps, speaker_turn_id
    - Boolean for question_flag
    Saves results to validation_results.csv AND prints full CSV
    """
    errors = []
    validation_status = []

    # 1. Row count
    if len(df) < 25:
        errors.append(f"CSV has only {len(df)} rows — minimum required is 25")

    # 2. Check each row and collect status
    for idx, row in df.iterrows():
        row_errors = []

        # Missing columns/values
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                row_errors.append(f"Missing column: {col}")
            elif pd.isnull(row[col]):
                row_errors.append(f"{col} is missing")

        # Timestamp valid
        if "timestamp" in df.columns and not pd.isnull(row["timestamp"]):
            try:
                pd.to_datetime(row["timestamp"])
            except Exception:
                row_errors.append(f"timestamp '{row['timestamp']}' invalid")

        # Numeric > 0 checks
        numeric_cols = ["time_taken_sec", "num_words", "speech_rate_wps", "speaker_turn_id"]
        for col in numeric_cols:
            if col in df.columns and not pd.isnull(row[col]):
                if not pd.api.types.is_numeric_dtype(type(row[col])):
                    row_errors.append(f"{col} not numeric")
                elif row[col] <= 0:
                    row_errors.append(f"{col} = {row[col]} ≤ 0")

        # Boolean check
        if "question_flag" in df.columns and not pd.isnull(row["question_flag"]):
            if not isinstance(row["question_flag"], bool) and row["question_flag"] not in (True, False, 1, 0, "True", "False"):
                row_errors.append(f"question_flag invalid type")

        # Record status
        status = "PASS" if len(row_errors) == 0 else "FAIL"
        validation_status.append({
            "row_number": idx + 1,
            "name": row.get("name", ""),
            "status": status,
            "errors": "; ".join(row_errors) if row_errors else ""
        })
        if row_errors:
            errors.append(f"Row {idx+1}: {'; '.join(row_errors)}")

    # Save validation results to CSV
    df_validation = pd.DataFrame(validation_status)
    df_validation.to_csv(FILE_VALIDATION_RESULTS, index=False)
    print(f"✅ Validation details saved → {FILE_VALIDATION_RESULTS}")
    
    # 📌 PRINT FULL validation_results.csv
    print("\n" + "="*70)
    print("📄 FILE: validation_results.csv")
    print("="*70)
    print(df_validation.to_string(index=False))
    print("="*70)

    # Final result
    if errors:
        print("❌ Validation failed:")
        for err in errors:
            print(f"   - {err}")
        return False
    else:
        print("✅ Validation passed — all checks OK")
        return True


# ----------------------
# ANALYSIS FUNCTION — SAVES EVERYTHING TO CSV + PRINTS ALL
# ----------------------
def analyse_data(df_raw, df_corrected, df_enriched):
    """
    Stage 5 Analysis:
    - Speaker statistics
    - Overall metrics
    - Speaker details (most/least words, questions, time)
    - Raw vs corrected comparison
    All results saved to separate CSV files AND printed fully
    """
    print("\n📊 Running analysis and saving outputs...")

    # --- 1. Speaker Statistics CSV ---
    speaker_stats = df_enriched.groupby("name").agg(
        total_turns=("name", "count"),
        total_words=("num_words", "sum"),
        total_raw_chars=("raw_script", lambda x: x.str.len().sum()),
        total_corr_chars=("text", lambda x: x.str.len().sum()),
        total_time=("time_taken_sec", "sum"),
        total_questions=("question_flag", "sum"),
        avg_speech_rate=("speech_rate_wps", "mean")
    ).round(3).reset_index()
    speaker_stats.to_csv(FILE_SPEAKER_STATS, index=False)
    print(f"✅ Speaker stats saved → {FILE_SPEAKER_STATS}")
    
    # 📌 PRINT FULL analysis_speaker_stats.csv
    print("\n" + "="*70)
    print("📄 FILE: analysis_speaker_stats.csv")
    print("="*70)
    print(speaker_stats.to_string(index=False))
    print("="*70)

    # --- 2. Overall Metrics CSV ---
    metrics = pd.DataFrame({
        "total_rows": [len(df_enriched)],
        "total_speaking_time_sec": [df_enriched["time_taken_sec"].sum().round(2)],
        "avg_speaking_time_per_speaker_sec": [df_enriched.groupby("name")["time_taken_sec"].sum().mean().round(2)],
        "avg_raw_chars": [df_enriched["raw_script"].str.len().mean().round(2)],
        "avg_corrected_chars": [df_enriched["text"].str.len().mean().round(2)],
        "avg_length_change": [(df_enriched["text"].str.len() - df_enriched["raw_script"].str.len()).mean().round(2)],
        "total_questions": [df_enriched["question_flag"].sum()]
    })
    metrics.to_csv(FILE_METRICS, index=False)
    print(f"✅ Overall metrics saved → {FILE_METRICS}")
    
    # 📌 PRINT FULL analysis_metrics_summary.csv
    print("\n" + "="*70)
    print("📄 FILE: analysis_metrics_summary.csv")
    print("="*70)
    print(metrics.to_string(index=False))
    print("="*70)

    # --- 3. Speaker Details CSV ---
    most_words = speaker_stats.loc[speaker_stats["total_words"].idxmax()]
    least_words = speaker_stats.loc[speaker_stats["total_words"].idxmin()]
    most_questions = speaker_stats.loc[speaker_stats["total_questions"].idxmax()]
    top5_time = speaker_stats.sort_values("total_time", ascending=False).head(5)

    speaker_details = pd.DataFrame([
        {"metric": "Most words", "name": most_words["name"], "value": most_words["total_words"]},
        {"metric": "Least words", "name": least_words["name"], "value": least_words["total_words"]},
        {"metric": "Most questions", "name": most_questions["name"], "value": most_questions["total_questions"]},
        {"metric": "Total meeting time", "name": "ALL", "value": df_enriched["time_taken_sec"].sum().round(2)},
        {"metric": "Average time per speaker", "name": "ALL", "value": df_enriched.groupby("name")["time_taken_sec"].sum().mean().round(2)}
    ])
    # Add top 5 by time
    for i, (_, row) in enumerate(top5_time.iterrows(), 1):
        speaker_details = pd.concat([speaker_details, pd.DataFrame([
            {"metric": f"{i}th speaker by time", "name": row["name"], "value": row["total_time"]}
        ])], ignore_index=True)
    # Add average speech rates
    for _, row in speaker_stats.iterrows():
        speaker_details = pd.concat([speaker_details, pd.DataFrame([
            {"metric": "Average speech rate", "name": row["name"], "value": row["avg_speech_rate"]}
        ])], ignore_index=True)

    speaker_details.to_csv(FILE_SPEAKER_DETAILS, index=False)
    print(f"✅ Speaker details saved → {FILE_SPEAKER_DETAILS}")
    
    # 📌 PRINT FULL analysis_speaker_details.csv
    print("\n" + "="*70)
    print("📄 FILE: analysis_speaker_details.csv")
    print("="*70)
    print(speaker_details.to_string(index=False))
    print("="*70)

    # --- 4. Correction Comparison CSV ---
    comparison = df_corrected[["timestamp", "name", "raw_script", "text", "time_taken_sec"]].copy()
    comparison["changed"] = comparison["raw_script"].str.strip() != comparison["text"].str.strip()
    comparison["length_change"] = comparison["text"].str.len() - comparison["raw_script"].str.len()
    comparison.to_csv(FILE_CORRECTION_COMPARISON, index=False)
    print(f"✅ Correction comparison saved → {FILE_CORRECTION_COMPARISON}")
    
    # 📌 PRINT FULL analysis_correction_comparison.csv
    print("\n" + "="*70)
    print("📄 FILE: analysis_correction_comparison.csv")
    print("="*70)
    print(comparison.to_string(index=False))
    print("="*70)

    return speaker_stats, metrics, speaker_details


# ----------------------
# ORIGINAL STAGE FUNCTIONS
# ----------------------
def show_stage1():
    print("\n" + "="*50)
    print(" STAGE 1: Speech Transcription (Vosk)")
    print("="*50)

    if not FILE_RAW.exists():
        print("X transcript.csv not found")
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
        print("X transcript_corrected.csv not found")
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
        print("X transcript_corrected_enriched.csv not found")
        return None

    df = pd.read_csv(FILE_ENRICHED)
    print(f"✅ transcript_corrected_enriched.csv found — {len(df)} rows")
    print("\nSample:")
    for _, row in df.head(3).iterrows():
        print(f"  {row['name']:<10} | words: {row['num_words']:>2} | chars: {row['text_size_chars']:>3} | rate: {row['speech_rate_wps']} wps | question: {str(row['question_flag']):<5} | turn: {row['speaker_turn_id']}")
    return df


def show_stage4(df_raw, df_corrected, df_enriched):
    print("\n" + "="*50)
    print(" STAGE 4: Validation & Analysis")
    print("="*50)

    if df_enriched is None:
        print("X No enriched data available — cannot validate or analyse")
        return None, None

    # Run validation (saves + prints CSV)
    validation_ok = validate_csv(df_enriched)
    if not validation_ok:
        return None, None

    # Run analysis (saves + prints ALL CSVs)
    speaker_stats, metrics, speaker_details = analyse_data(df_raw, df_corrected, df_enriched)

    # Print summary to console
    print("\n=> SPEAKER STATISTICS SUMMARY")
    for _, row in speaker_stats.iterrows():
        print(f"  {row['name']:<10} — {row['total_turns']} turns | {row['total_words']} words | {row['total_time']}s")

    print("\n=> KEY RESULTS")
    print(f"  Total meeting time:  {metrics['total_speaking_time_sec'][0]} seconds")
    print(f"  Total questions:     {metrics['total_questions'][0]}")

    return speaker_stats, metrics


def save_json(df_raw, df_corrected, df_enriched, speaker_stats, metrics):
    """Save all results to JSON for the UI — FIXED unpack error"""
    
    # --- Safe iteration without unpack error ---
    stage1_sample = []
    if df_raw is not None:
        for _, row in df_raw.head(3).iterrows():
            stage1_sample.append({"name": row["name"], "text": row["raw_script"].strip()})

    stage2_sample = []
    if df_corrected is not None:
        for _, row in df_corrected.head(3).iterrows():
            stage2_sample.append({"name": row["name"], "text": row["text"].strip()})

    stage3_sample = []
    if df_enriched is not None:
        for _, row in df_enriched.head(3).iterrows():
            stage3_sample.append({
                "name": row["name"],
                "num_words": int(row["num_words"]),
                "text_size_chars": int(row["text_size_chars"]),
                "speech_rate_wps": float(row["speech_rate_wps"]),
                "question_flag": bool(row["question_flag"]),
                "speaker_turn_id": int(row["speaker_turn_id"])
            })

    # --- Build JSON data ---
    stage1_data = {
        "rows": len(df_raw) if df_raw is not None else 0,
        "sample": stage1_sample
    }

    stage2_data = {
        "rows": len(df_corrected) if df_corrected is not None else 0,
        "sample": stage2_sample
    }

    stage3_data = {
        "rows": len(df_enriched) if df_enriched is not None else 0,
        "sample": stage3_sample
    }

    stage4_data = {
        "speaker_stats": speaker_stats.to_dict(orient="records") if speaker_stats is not None else [],
        "metrics": metrics.to_dict(orient="records")[0] if (metrics is not None and len(metrics) > 0) else {}
    }

    results = {
        "stage1": stage1_data,
        "stage2": stage2_data,
        "stage3": stage3_data,
        "stage4": stage4_data
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
    speaker_stats, metrics = show_stage4(df_raw, df_corrected, df_enriched)

    if df_raw is not None and df_corrected is not None and df_enriched is not None and speaker_stats is not None:
        save_json(df_raw, df_corrected, df_enriched, speaker_stats, metrics)

    print("\n" + "="*50)
    print(" PIPELINE COMPLETE")
    print("="*50)