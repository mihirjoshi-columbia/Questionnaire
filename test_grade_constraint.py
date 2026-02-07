import pandas as pd
from smart_match import Matcher

# Mock Data
data = {
    'name': ['Fr', 'So', 'Jr', 'Sr'],
    'year': [2029, 2028, 2027, 2026],
    # Fill required cols with dummy data to avoid errors in calculate_score
    'gender': ['Male']*4, 'orientation': ['Straight']*4, 'similar_preference': ['Similar']*4,
    'music': ['Pop']*4, 'weekend': ['Chill']*4, 
    'love_language': ['Touch']*4, 'politics': ['Moderate']*4, 'politics_preference': ['No preference']*4,
    'smoking': ['No']*4,
    'stat_trust': [5]*4, 'stat_humor': [5]*4, 'stat_communication': [5]*4, 
    'stat_kindness': [5]*4, 'stat_looks': [5]*4, 'stat_money': [5]*4, 'stat_ambition': [5]*4
}
df = pd.DataFrame(data)

matcher = Matcher(df)

print("--- Testing Grade Adjacency ---")

pairs = [
    (0, 1, "Fr+So (2029+2028)", True),
    (0, 2, "Fr+Jr (2029+2027)", False),
    (0, 3, "Fr+Sr (2029+2026)", False),
    (1, 2, "So+Jr (2028+2027)", True),
    (1, 3, "So+Sr (2028+2026)", False),
    (2, 3, "Jr+Sr (2027+2026)", True),
]

passed = True
for idx_a, idx_b, desc, expected in pairs:
    # Use mode="friend" to skip orientation check and isolate Grade Adjacency check
    score = matcher.calculate_score(idx_a, idx_b, mode="friend")
    # If compatible, score should be > -500 (calculated normally)
    # If incompatible, score should be -1000
    is_compatible = (score > -500)
    
    status = "PASS" if is_compatible == expected else "FAIL"
    if status == "FAIL": passed = False
    
    print(f"{desc}: Score={score}, Allowed={is_compatible}, Expected={expected} -> {status}")

if passed:
    print("\nALL TESTS PASSED")
else:
    print("\nSOME TESTS FAILED")
