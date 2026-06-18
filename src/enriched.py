import pandas as pd

def enrich_data(enriched):

    test_enriched = enriched.copy()                       # a copy to try enrichment without changing the original dataframe.

    test_enriched["question_flag"] = test_enriched["text"].str.endswith('?')              # create col 1. question_flag
    test_enriched["num_words"] = test_enriched["text"].apply(lambda x: len(x.split()))    # create col 2. num_words
    test_enriched["text_size_chars"] = test_enriched["text"].str.len()                    # create col 3. text_size_chars
    test_enriched["speech_rate_wps"]= (test_enriched["num_words"] / test_enriched["time_taken_sec"]).round(1) # create col 4. speech_rate_wps
    test_enriched["speaker_turn_id"] = test_enriched.groupby(['name']).cumcount()+1       # create col 5. speaker_turn_id
    # print(test_enriched1) # [25 rows x 10 columns]
  
    test_enriched.to_csv("transcript_corrected_enriched.csv", index=False)                 # save under transcript_corrected_enriched name
   
    return(test_enriched) 
    

if __name__ == "__main__":
    enriched = pd.read_csv('transcript_corrected.csv') # load CSV file into a DataFrame.
    enrichedTranscript = enrich_data(enriched) 
    print(enrichedTranscript)                                                              # for checking

