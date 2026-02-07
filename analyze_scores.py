from smart_match import DataLoader, Matcher
import pandas as pd
import numpy as np

loader = DataLoader('data.csv')
df = loader.load_and_clean()
matcher = Matcher(df)

all_scores = []
matches = matcher.find_ideal_matches()

for user_id, (match_id, score) in matches.items():
    if score > -500: # Valid matches
        all_scores.append(score)

print(f"Total Matches: {len(all_scores)}")
print(f"Min Score: {min(all_scores) if all_scores else 'N/A'}")
print(f"Max Score: {max(all_scores) if all_scores else 'N/A'}")
print(f"Mean Score: {np.mean(all_scores) if all_scores else 'N/A'}")
print(f"Median Score: {np.median(all_scores) if all_scores else 'N/A'}")

# Check coverage
unmatched = [uid for uid in matcher.ids if matches[uid][1] <= -500]
print(f"Unmatched Users: {len(unmatched)}")
if unmatched:
    print(f"Unmatched IDs: {unmatched}")
