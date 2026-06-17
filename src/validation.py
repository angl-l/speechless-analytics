import pandas as pd
import numpy as np
from pathlib import Path

# ----------------------
# File paths
# ----------------------
FILE_RAW = Path("transcript.csv")
FILE_CORRECTED = Path("transcript_corrected.csv")
FILE_ENRICHED = Path("transcript_corrected_enriched.csv")


# ----------------------
# Validation Functions
# ----------------------
def validate_raw_transcript():
    """Validate raw transcript file"""
    print("="*50)
    print("VALIDATING RAW TRANSCRIPT")
    print("="*50)

    if not FILE_RAW.exists():
        print("❌ File not found:", FILE_RAW)
        return None

    df = pd.read_csv(FILE_RAW)
    errors = []

    # 1. Check required columns
    required_cols = ["timestamp", "name", "raw_script", "time_taken_sec"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    else:
        print("✅ All required columns present")

    # 2. Check for missing values
    nulls = df[required_cols].isnull().sum()
    if nulls.any():
        errors.append(f"Missing values:\n{nulls[nulls>0]}")
    else:
        print("✅ No missing values")

    # 3. Check time values are positive
    invalid_time = df[df["time_taken_sec"] <= 0]
    if not invalid_time.empty:
        errors.append(f"{len(invalid_time)} rows have invalid time (≤0)")
    else:
        print("✅ All time values valid")

    # 4. Check text not empty
    empty_text = df[df["raw_script"].str.strip() == ""].shape[0]
    if empty_text > 0:
        errors.append(f"{empty_text} rows have empty raw text")
    else:
        print("✅ All raw text filled")

    # 5. Timestamp format check
    try:
        pd.to_datetime(df["timestamp"])
        print("✅ Timestamp format valid")
    except Exception as e:
        errors.append(f"Invalid timestamp format: {e}")

    # Report errors
    if errors:
        print("\n⚠️ Validation issues:")
        for err in errors:
            print("   -", err)
    else:
        print("\n✅ Raw transcript passed all validation checks")

    return df


def validate_corrected_transcript():
    """Validate corrected transcript rules"""
    print("\n" + "="*50)
    print("VALIDATING CORRECTED TRANSCRIPT")
    print("="*50)

    if not FILE_CORRECTED.exists():
        print("❌ File not found:", FILE_CORRECTED)
        return None

    df = pd.read_csv(FILE_CORRECTED)
    errors = []

    # 1. Required columns
    required = ["timestamp", "name", "raw_script", "text", "time_taken_sec"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    else:
        print("✅ All required columns present")

    # 2. Corrected text rules
    def check_rules(text):
        if not isinstance(text, str) or text.strip() == "":
            return False, "Empty"
        starts_upper = text[0].isupper()
        ends_punct = text[-1] in (".", "?", "!")
        return starts_upper and ends_punct, f"StartUpper:{starts_upper}, EndPunct:{ends_punct}"

    rule_check = df["text"].apply(check_rules)
    invalid = [i for i, (ok, _) in enumerate(rule_check) if not ok]

    if invalid:
        errors.append(f"{len(invalid)} rows break correction rules")
        for idx in invalid[:3]:
            errors.append(f"   Row {idx+1}: {df.loc[idx, 'text']!r} | {rule_check[idx][1]}")
    else:
        print("✅ All text follows rules: capital start + end punctuation")

    # 3. Meaning preserved check (basic: same words count approx)
    df["raw_words"] = df["raw_script"].str.split().str.len()
    df["corr_words"] = df["text"].str.split().str.len()
    big_diff = df[abs(df["raw_words"] - df["corr_words"]) > 3]
    if not big_diff.empty:
        errors.append(f"{len(big_diff)} rows have large word count difference — possible meaning change")
    else:
        print("✅ Word count consistent — meaning likely preserved")

    # Report
    if errors:
        print("\n⚠️ Validation issues:")
        for err in errors:
            print("   -", err)
    else:
        print("\n✅ Corrected transcript passed all validation checks")

    return df


def validate_enriched_transcript():
    """Validate enriched file metrics and structure — skip if missing"""
    print("\n" + "="*50)
    print("VALIDATING ENRICHED TRANSCRIPT")
    print("="*50)

    if not FILE_ENRICHED.exists():
        print("ℹ️ Enriched file not found — skipping this step")
        return None

    df = pd.read_csv(FILE_ENRICHED)
    errors = []

    # 1. Required columns
    required = [
        "timestamp", "name", "raw_script", "text", "time_taken_sec",
        "question_flag", "num_words", "text_size_chars", "speech_rate_wps", "speaker_turn_id"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    else:
        print("✅ All enriched columns present")

    # 2. Numeric ranges
    if not df["num_words"].between(1, 1000).all():
        errors.append("num_words out of reasonable range")
    else:
        print("✅ num_words valid")

    if not df["speech_rate_wps"].between(0.1, 5.0).all():
        errors.append("speech_rate_wps out of expected range (0.1–5.0)")
    else:
        print("✅ speech_rate_wps valid")

    if not df["text_size_chars"].between(1, 5000).all():
        errors.append("text_size_chars out of range")
    else:
        print("✅ text_size_chars valid")

    # 3. Boolean flag
    if not df["question_flag"].isin([True, False]).all():
        errors.append("question_flag has non-boolean values")
    else:
        print("✅ question_flag values correct")

    if errors:
        print("\n⚠️ Validation issues:")
        for err in errors:
            print("   -", err)
    else:
        print("\n✅ Enriched transcript passed all validation checks")

    return df


# ----------------------
# Analysis Functions
# ----------------------
def run_analysis(df_raw, df_corr, df_enriched):
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)

    # --- 1. Basic Overview ---
    print("\n📌 OVERVIEW")
    print(f"Total entries: {len(df_raw)}")
    print(f"Unique speakers: {df_raw['name'].nunique()} — {sorted(df_raw['name'].unique())}")
    print(f"Total recording time: {df_raw['time_taken_sec'].sum():.1f} seconds")

    # --- 2. Correction Impact ---
    print("\n📌 CORRECTION IMPACT")
    df_corr["changed"] = df_corr["raw_script"].str.strip() != df_corr["text"].str.strip()
    changed_pct = df_corr["changed"].mean() * 100
    print(f"Entries modified: {df_corr['changed'].sum()} ({changed_pct:.1f}%)")
    print(f"Entries unchanged: {len(df_corr) - df_corr['changed'].sum()}")

    # Length change
    df_corr["len_diff"] = df_corr["text"].str.len() - df_corr["raw_script"].str.len()
    print(f"Average length change: {df_corr['len_diff'].mean():.1f} characters")

    # --- 3. Speaker Analysis ---
    print("\n📌 SPEAKER STATISTICS")
    speaker_stats = df_corr.groupby("name").agg(
        total_turns=("name", "count"),
        total_raw_chars=("raw_script", lambda x: x.str.len().sum()),
        total_corr_chars=("text", lambda x: x.str.len().sum()),
        avg_raw_length=("raw_script", lambda x: x.str.len().mean()),
        avg_corr_length=("text", lambda x: x.str.len().mean())
    ).round(2)
    print(speaker_stats.to_string())

    # --- 4. Metrics Summary ---
    print("\n📌 OVERALL METRICS SUMMARY")
    metrics = pd.DataFrame({
        "avg_raw_chars": [df_corr["raw_script"].str.len().mean()],
        "avg_corr_chars": [df_corr["text"].str.len().mean()],
        "avg_length_change": [df_corr["len_diff"].mean()]
    }).round(2)
    print(metrics.to_string(index=False))

    # --- Use enriched data only if available ---
    if df_enriched is not None:
        print("\n📌 ADDITIONAL ENRICHED METRICS")
        print(f"Questions detected: {df_enriched['question_flag'].sum()}")
        print(f"Conversation turns: {df_enriched['speaker_turn_id'].max()}")

    # --- Save analysis outputs ---
    speaker_stats.to_csv("analysis_speaker_stats.csv")
    metrics.to_csv("analysis_metrics_summary.csv", index=False)
    df_corr.to_csv("analysis_correction_comparison.csv", index=False)
    print("\n✅ Analysis files saved:")
    print("   - analysis_speaker_stats.csv")
    print("   - analysis_metrics_summary.csv")
    print("   - analysis_correction_comparison.csv")


# ----------------------
# Run everything
# ----------------------
if __name__ == "__main__":
    df_raw = validate_raw_transcript()
    df_corr = validate_corrected_transcript()
    df_enriched = validate_enriched_transcript()

    if df_raw is not None and df_corr is not None:
        run_analysis(df_raw, df_corr, df_enriched)
    else:
        print("\n❌ Missing required files — cannot run analysis")