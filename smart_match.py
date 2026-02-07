import pandas as pd
import numpy as np
import json
import argparse
from datetime import datetime

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.column_map = {
            "Timestamp": "timestamp",
            "Name (First + Last)": "name",
            "Student Email": "email",
            "Phone Number": "phone",
            "Class Year": "year",
            "School": "school",
            "What is your gender?": "gender",
            "What is your sexual orientation?": "orientation",
            "What are you looking for?": "looking_for",
            "Are you looking for someone who is similar to you or is different?": "similar_preference",
            "What does your ideal weekend look like?": "weekend",
            "What is your BIGGEST red flag in a partner? ": "red_flag",
            "What is your go-to music genre or vibe?": "music",
            "Which of the following BEST describes your Love Language?": "love_language",
            "Which of the following best describes your belief system?": "beliefs",
            "What is one value from your upbringing that you want to pass on to the next generation?": "values",
            "What is your Dream Job/Field?": "job",
            "What are your Political Views?": "politics",
            "Do you have a preference for your partner's political views? ": "politics_preference",
            "What is your sleep schedule?": "sleep",
            "Do you smoke? Do you care if your partner smokes?": "smoking",
            "Trust": "stat_trust",
            "Humor": "stat_humor",
            "Communication": "stat_communication",
            "Kindness": "stat_kindness",
            "Looks (be fr)": "stat_looks",
            "Money (also be fr)": "stat_money",
            "Ambition": "stat_ambition",
            "Pick a vibe: If we're arguing, what are you doing?": "arguing_style",
            "If we are together at a function, would you prefer to:": "function_style",
            "Would you be interested in participating in pop the balloon at this event?": "pop_balloon"
        }

    def load_and_clean(self):
        self.df = pd.read_csv(self.filepath)
        self.df = self.df.rename(columns=self.column_map)
        
        # Clean Year
        self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
        
        # Clean Stats (ensure they are numeric)
        stat_cols = ['stat_trust', 'stat_humor', 'stat_communication', 'stat_kindness', 'stat_looks', 'stat_money', 'stat_ambition']
        for col in stat_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(3) # Default to 3 if missing
            
        print(f"Loaded {len(self.df)} profiles.")
        return self.df

class Matcher:
    def __init__(self, df):
        self.df = df
        self.ids = df.index.tolist()
        
    def get_grade_compatibility(self, year_a, year_b):
        """
        Returns True if years are adjacent or same.
        Freshman (2029) <-> Sophomore (2028) is OK (diff 1).
        Freshman (2029) <-> Junior (2027) is NOT OK (diff 2).
        """
        if pd.isna(year_a) or pd.isna(year_b):
            return True # Permissive if missing
        return abs(year_a - year_b) <= 1

    def get_gender_category(self, user):
        g = str(user['gender']).lower()
        if 'non-binary' in g or 'agender' in g:
            return 'NB'
        if 'female' in g or 'woman' in g:
            return 'Woman'
        if 'male' in g or 'man' in g:
            return 'Man'
        return 'NB' # Fallback

    def get_orientation_category(self, user):
        o = str(user['orientation']).lower()
        if 'heterosexual' in o or 'straight' in o:
            return 'Straight'
        if 'gay' in o or 'lesbian' in o or 'homosexual' in o:
            return 'Gay'
        if 'bisexual' in o or 'pansexual' in o or 'fluid' in o or 'queer' in o:
            return 'Bi'
        return 'Bi' # Fallback/Unsure -> treat as open

    def get_orientation_compatibility(self, user_a, user_b):
        """
        Strict check based on allowed pairings:
        
        Straight Man + Straight Woman
        Bi Man + Straight Woman
        Bi Man + Bi Man
        Bi Man + Bi Woman
        Gay Man + Bi Man
        Gay Man + Gay Man
        Bi Woman + Straight Man
        Bi Woman + Bi Woman
        Gay Woman + Bi Woman
        Gay Woman + Gay Woman
        
        Non-binary Logic (User approved plan for permissiveness):
        NB + NB
        NB + Bi/Pan/Queer (Man/Woman)
        """
        
        g_a = self.get_gender_category(user_a)
        o_a = self.get_orientation_category(user_a)
        g_b = self.get_gender_category(user_b)
        o_b = self.get_orientation_category(user_b)
        
        # Define Tuple: (Gender, Orientation)
        p_a = (g_a, o_a)
        p_b = (g_b, o_b)
        
        # Allowed set (Direction agnostic, we will check both A->B and B->A logic or just set membership of the frozen set of pairs)
        # Actually simplest is to just check if the sorted pair of tuples is in the allowlist.
        
        # Let's normalize the pair key: sorted by some property? 
        # Or just check both permutations against a set of allowed directed pairs (but this is symmetric matching).
        # We'll use a set of frozensets to represent allowed unordered pairs.
        
        allowed_pairs = set()
        
        def add_pair(g1, o1, g2, o2):
            allowed_pairs.add(frozenset({(g1, o1), (g2, o2)}))
            
        # User List
        # 1. straight man + straight women
        add_pair('Man', 'Straight', 'Woman', 'Straight')
        
        # 2. bi men + straight women
        add_pair('Man', 'Bi', 'Woman', 'Straight')
        
        # 3. bi men + bi men
        add_pair('Man', 'Bi', 'Man', 'Bi')
        
        # 4. bi men + bi women
        add_pair('Man', 'Bi', 'Woman', 'Bi')
        
        # 5. gay men + bi men
        add_pair('Man', 'Gay', 'Man', 'Bi')
        
        # 6. gay men + gay men
        add_pair('Man', 'Gay', 'Man', 'Gay')
        
        # 7. bi women + straight men (Covered by #2 reversed, but adding explicitly does no harm to set logic)
        add_pair('Woman', 'Bi', 'Man', 'Straight')
        
        # 8. bi women + bi women
        add_pair('Woman', 'Bi', 'Woman', 'Bi')
        
        # 9. gay women + bi women
        add_pair('Woman', 'Gay', 'Woman', 'Bi')
        
        # 10. gay women + gay women
        add_pair('Woman', 'Gay', 'Woman', 'Gay')
        
        # NB Logic
        # NB + NB
        add_pair('NB', 'Bi', 'NB', 'Bi')      # NB is treated as 'Bi' orientation-wise if unspecified? 
        # Actually my helper returns 'Bi' for fallback. If NB says 'Gay', they get 'Gay'. 
        # But 'Gay' usually implies 'Same Gender'. NB+NB is Same Gender?
        # Let's just Allow Any NB + Any NB?
        # Or specifically NB + NB (regardless of orientation)?
        # For simplicity in this function, let's assume if Gender is NB, we allow match with NB.
        # But we also want NB + Bi (Man/Woman).
        
        pair_to_check = frozenset({p_a, p_b})
        
        if pair_to_check in allowed_pairs:
            return True
            
        # Special NB Handling Checks (since they might strictly fail the set above if we don't enumerate all)
        
        # NB + NB matching
        if g_a == 'NB' and g_b == 'NB':
            return True
            
        # NB + Bi/Pan (Man or Woman)
        # If one is NB, the other MUST be Bi (which includes Pan/Queer/Fluid)
        if (g_a == 'NB' and o_b == 'Bi') or (g_b == 'NB' and o_a == 'Bi'):
            return True
        return False
        
    def calculate_score(self, idx_a, idx_b, mode="romantic"):
        user_a = self.df.loc[idx_a]
        user_b = self.df.loc[idx_b]
        
        score = 0
        max_score = 0
        
        # --- Hard Constraints ---
        
        # 1. Grade Adjacency
        if not self.get_grade_compatibility(user_a['year'], user_b['year']):
            return -1000
            
        # 2. Orientation (Only for Romantic)
        if mode == "romantic":
            if not self.get_orientation_compatibility(user_a, user_b):
                return -1000

        # --- Soft Constraints / Scoring ---
        
        # 1. Look for Similarity vs Difference
        # "Are you looking for someone who is similar to you or is different?"
        # We'll take the asker's preference (user_a)
        seek_sim = "similar" in str(user_a['similar_preference']).lower()
        
        # Helper for scoring
        def compare_categorical(val_a, val_b, weight=1.0):
            return weight if str(val_a).lower() == str(val_b).lower() else 0
            
        def compare_multi_select(val_a, val_b, weight=1.0):
            set_a = set(str(val_a).split(', '))
            set_b = set(str(val_b).split(', '))
            overlap = len(set_a.intersection(set_b))
            union = len(set_a.union(set_b))
            if union == 0: return 0
            return weight * (overlap / union)
            
        def compare_numeric_diff(val_a, val_b, weight=1.0, invert=False):
            # Invert=True means we want DIFFERENCE (for 'opposites attract' logic if needed)
            # Default is we want SIMILARITY (small difference = high score)
            diff = abs(val_a - val_b) # range roughly 0-4 for 1-5 stats
            norm_diff = diff / 4.0 # 0 to 1
            similarity = 1.0 - norm_diff
            
            if invert:
                return weight * norm_diff
            else:
                return weight * similarity

        # --- Features ---
        
        # Politics (High weight)
        # If user has non-negotiables, penalize heavily for difference
        pol_pref_a = str(user_a['politics_preference'])
        pol_match = (str(user_a['politics']) == str(user_b['politics']))
        
        if "non-negotiable" in pol_pref_a and not pol_match:
            score -= 50
        elif pol_match:
            score += 10
        max_score += 10
            
        # Smoking
        # "No I don't smoke, I do care about if my partner smokes."
        smokes_b = "yes" in str(user_b['smoking']).lower().split(',')[0] # simplistic check
        care_a = "i do care" in str(user_a['smoking']).lower()
        
        if care_a and smokes_b:
            score -= 50
        
        # Interests (Music, Weekend)
        score += compare_multi_select(user_a['music'], user_b['music'], weight=15)
        score += compare_multi_select(user_a['weekend'], user_b['weekend'], weight=15)
        max_score += 30
        
        # Vibe / Personality (Stats)
        stat_cols = ['stat_trust', 'stat_humor', 'stat_communication', 'stat_kindness', 'stat_looks', 'stat_money', 'stat_ambition']
        
        for col in stat_cols:
            # If finding similar: high weight on small diff
            # If finding different: slightly lower weight on small diff (or reward diff)
            # Generally, people want similar values on core things like Trust/Kindness even if they want "different" personalities.
            # We'll keep Trust/Comm/Kindness as "Must be high/similar".
            if col in ['stat_trust', 'stat_communication', 'stat_kindness']:
                score += compare_numeric_diff(user_a[col], user_b[col], weight=5)
            else:
                # For looks, ambition, etc, respect the "similar/different" pref slightly
                if seek_sim:
                    score += compare_numeric_diff(user_a[col], user_b[col], weight=3)
                else:
                    # If they want different, maybe we don't penalize difference as much, 
                    # or we actually reward it? Let's just make it neutral weight or lower weight for similarity.
                    score += compare_numeric_diff(user_a[col], user_b[col], weight=1) 
            max_score += 5 # (approx max contribution)

        # Love Language (Good to match)
        score += compare_categorical(user_a['love_language'], user_b['love_language'], weight=10)
        max_score += 10

        # --- Score Normalization ---
        # Target Range: 38.8 to 98.6
        # Expected Raw Range: approx -60 to 90
        if score < -500:
            return score # Hard Incompatible
            
        # Linear Mapping
        # norm = min_target + (score - min_raw) * (range_target / range_raw)
        # min_raw = -60, max_raw = 90 -> range = 150
        # min_target = 38.8, max_target = 98.6 -> range = 59.8
        
        factor = 59.8 / 150.0
        normalized = 38.8 + (score + 60) * factor
        
        # Clamp
        normalized = max(38.8, min(normalized, 98.6))

        return normalized


    def find_all_matches(self):
        """
        Legacy method: Runs both checks.
        """
        matches = self.find_ideal_matches()
        groups = self.find_groups()
        return matches, groups

    def find_ideal_matches(self):
        """
        Generates Ideal Match (Pair) for everyone.
        """
        # --- 1. Ideal Matches ---
        print("\nCalculating Ideal Matches...")
        matches = {}
        for idx in self.ids:
            best_score = -float('inf')
            best_match = None
            
            for other_idx in self.ids:
                if idx == other_idx: continue
                
                s = self.calculate_score(idx, other_idx, mode="romantic")
                if s > best_score and s > -500: # Filter out hard incompatible
                    best_score = s
                    best_match = other_idx
            
            matches[idx] = (best_match, best_score)
        return matches

    def find_groups(self):
        """
        Generates Groups of ~5 (updated code says 10, keeping logic same).
        """
        # --- 2. Groups ---
        print("\nForming Groups of 10...")
        # Greedy approach
        unassigned = set(self.ids)
        groups = []
        target_group_size = 10
        
        while len(unassigned) > 0:
            if len(unassigned) < target_group_size:
                # Add remainder to last group if it exists
                if groups:
                    groups[-1].extend(list(unassigned))
                else:
                    groups.append(list(unassigned)) # Just one small group
                break
                
            # Start new group with random person
            seed = list(unassigned)[0]
            unassigned.remove(seed)
            current_group = [seed]
            
            while len(current_group) < target_group_size and unassigned:
                # Find best fit for the *current group*
                # We can define group fit as average score with all current members
                best_candidate = None
                best_group_score = -float('inf')
                
                for candidate in unassigned:
                    # Group constraint: Grade adjacency with EVERYONE in group? 
                    # Or just generally consistent? 
                    # Let's enforce Strict Adjacency with ALL existing members to prevent a chain like Fr-So-Jr where Fr and Jr shouldn't mix.
                    
                    valid_candidate = True
                    total_score = 0
                    
                    for member in current_group:
                        # Check grade
                        if not self.get_grade_compatibility(self.df.loc[candidate]['year'], self.df.loc[member]['year']):
                            valid_candidate = False
                            break
                        
                        # Score (use 'friend' mode or just skip orientation check)

                        # We reuse calculate_score but maybe we shouldn't punish orientation mismatch for groups
                        # Let's use mode="friend" (logic below)
                        
                        # Calculating score manually for friend context (skipping orientation check inside score function logic if we tweaked it)
                        # Actually calculate_score does -1000 for orientation only if mode="romantic".
                        # So let's call it with mode="friend"
                        
                        s = self.calculate_score(candidate, member, mode="friend")
                        total_score += s
                        
                    if valid_candidate:
                        avg_score = total_score / len(current_group)
                        if avg_score > best_group_score:
                            best_group_score = avg_score
                            best_candidate = candidate
                            
                if best_candidate:
                    current_group.append(best_candidate)
                    unassigned.remove(best_candidate)
                else:
                    # No valid candidates found for this group (maybe isolated by grade)
                    break 
            
            groups.append(current_group)

        return groups

    def generate_report(self, matches, groups):
        print("\n" + "="*40)
        print("          MATCHING REPORT")
        print("="*40)
        
        print("\n--- IDEAL PAIR MATCHES ---")
        for idx, (match_idx, score) in matches.items():
            user = self.df.loc[idx]
            if match_idx is not None:
                match = self.df.loc[match_idx]
                print(f"{user['name']} ({user['year']}) <--> {match['name']} ({match['year']}) [Score: {score:.1f}]")
            else:
                print(f"{user['name']} ({user['year']}) <--> NO COMPATIBLE MATCH FOUND")

        print("\n\n--- GROUPS ---")
        for i, grp in enumerate(groups):
            print(f"\nGroup {i+1}:")
            member_names = [f"{self.df.loc[uid]['name']} ({self.df.loc[uid]['year']})" for uid in grp]
            for name in member_names:
                print(f"  - {name}")

    def generate_ranked_report(self, matches):
        print("\n" + "="*40)
        print("      RANKED PAIR MATCHES REPORT")
        print("="*40)
        
        # Convert matches dict to a list of unique pairs to avoid duplicates A-B and B-A?
        # Actually user might want to see valid matches for *everyone*, even if asymmetric scores (though symmetric here)
        # But usually "match" implies bidirectional. 
        # The current logic: matches[A] = Best for A.
        # It's possible A's best is B, but B's best is C.
        # "Print pair matches" -> Let's list everyone's best match, ranked by the score.
        
        # Structure: list of (user_idx, match_idx, score)
        ranked_list = []
        for idx, (match_idx, score) in matches.items():
            ranked_list.append((idx, match_idx, score))
            
        # Sort by score descending
        ranked_list.sort(key=lambda x: x[2], reverse=True)
        
        for idx, match_idx, score in ranked_list:
            user = self.df.loc[idx]
            user_name = f"{user['name']} ({user['year']})"
            
            if match_idx is not None:
                match = self.df.loc[match_idx]
                match_name = f"{match['name']} ({match['year']})"
                print(f"[{score:.1f}] {user_name} <--> {match_name}")
            else:
                print(f"[{score:.1f}] {user_name} <--> NO MATCH")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matchmaking Algorithm")
    parser.add_argument('--rank-pairs', action='store_true', help="Print only ranked pair matches")
    args = parser.parse_args()

    loader = DataLoader('data.csv')
    df = loader.load_and_clean()
    
    matcher = Matcher(df)
    
    if args.rank_pairs:
        matches = matcher.find_ideal_matches()
        matcher.generate_ranked_report(matches)
    else:
        # Default behavior
        matches = matcher.find_ideal_matches()
        groups = matcher.find_groups()
        matcher.generate_report(matches, groups)
