from textblob import TextBlob
import json
from time import sleep

class Matcher:
    def __init__(self, user_data):
        self.user_data = user_data
        # Define weights for different questions (can be adjusted)
        self.question_weights = {
            "What is your favorite book genre?": 1.0,
            "What is your favorite color?": 0.5,
            "What is your favorite food cuisine?": 0.8,
            "What is your favorite movie genre?": 1.0,
            "What is your favorite season?": 0.6,
            "What is your ideal vacation destination?": 0.9,
            "What is your preferred hobby?": 0.9,
            "Who is your favorite music artist?": 0.7
        }

    def calculate_response_similarity(self, response1, response2):
        """Calculate similarity between two responses"""
        # Exact match
        if response1.lower() == response2.lower():
            return 1.0
        
        # Calculate sentiment similarity as a backup
        try:
            sent1 = TextBlob(str(response1)).sentiment.polarity
            sent2 = TextBlob(str(response2)).sentiment.polarity
            return 1 - abs(sent1 - sent2)
        except:
            return 0.0

    def get_compatibility_score(self, user1_data, user2_data):
        """Calculate overall compatibility between two users"""
        total_score = 0
        total_weight = 0

        for question, weight in self.question_weights.items():
            if question in user1_data and question in user2_data:
                response1 = user1_data[question]
                response2 = user2_data[question]
                
                similarity = self.calculate_response_similarity(response1, response2)
                total_score += similarity * weight
                total_weight += weight

        if total_weight == 0:
            return 0
        
        return total_score / total_weight

    def get_top_matches(self, user_id, top_n=3):
        """Find top matches for a given user"""
        print(f"\nFinding matches for {user_id}...")
        user_data = self.user_data[user_id]
        compatibility_scores = []

        for other_id, other_data in self.user_data.items():
            if other_id != user_id:
                compatibility = self.get_compatibility_score(user_data, other_data)
                compatibility_scores.append((other_id, compatibility))
                print(f"Compatibility with {other_id}: {compatibility:.2f}")

        # Sort by compatibility score in descending order
        compatibility_scores.sort(key=lambda x: x[1], reverse=True)
        return compatibility_scores[:top_n]

def load_user_data(filename):
    """Load user response data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def create_groups(matcher, user_data, group_size=8):
    """Create groups of users based on compatibility scores"""
    
    # Create a copy of users that we can modify
    available_users = list(user_data.keys())
    groups = []
    
    while len(available_users) >= group_size:
        print(f"\nForming group {len(groups) + 1}...")
        current_group = []
        
        # Start with first available user
        first_user = available_users[0]
        current_group.append(first_user)
        available_users.remove(first_user)
        
        # Find most compatible users for the group
        while len(current_group) < group_size and available_users:
            best_avg_score = -1
            best_user = None
            
            # For each remaining user, calculate average compatibility with current group
            for candidate in available_users:
                total_score = 0
                for group_member in current_group:
                    score = matcher.get_compatibility_score(
                        user_data[candidate], 
                        user_data[group_member]
                    )
                    total_score += score
                avg_score = total_score / len(current_group)
                
                if avg_score > best_avg_score:
                    best_avg_score = avg_score
                    best_user = candidate
            
            if best_user:
                current_group.append(best_user)
                available_users.remove(best_user)
        
        groups.append(current_group)
    
    # Handle remaining users
    if available_users:
        if len(groups) > 0:
            # Distribute remaining users to existing groups
            for user in available_users:
                # Find group with best average compatibility
                best_group_score = -1
                best_group_idx = 0
                
                for i, group in enumerate(groups):
                    total_score = 0
                    for group_member in group:
                        score = matcher.get_compatibility_score(
                            user_data[user], 
                            user_data[group_member]
                        )
                        total_score += score
                    avg_score = total_score / len(group)
                    
                    if avg_score > best_group_score:
                        best_group_score = best_group_score
                        best_group_idx = i
                
                groups[best_group_idx].append(user)
        else:
            # If no groups were formed, create a final group with remaining users
            groups.append(available_users)
    
    return groups

def print_groups(groups, matcher, user_data):
    """Print groups and their internal compatibility scores"""
    print("\n=== Group Assignments ===")
    
    for i, group in enumerate(groups, 1):
        print(f"\nGroup {i} (Size: {len(group)}):")
        print("Members:", ", ".join(group))
        
        # Calculate and print average group compatibility
        total_score = 0
        num_pairs = 0
        for j, user1 in enumerate(group):
            for user2 in group[j+1:]:
                score = matcher.get_compatibility_score(
                    user_data[user1],
                    user_data[user2]
                )
                total_score += score
                num_pairs += 1
        
        avg_compatibility = total_score / num_pairs if num_pairs > 0 else 0
        print(f"Average Group Compatibility: {avg_compatibility:.2f}")
        print("-" * 40)

# Modify the main function to include group creation
def main():
    # Load user data
    user_data = load_user_data('responses.json')
    
    # Create matcher instance
    matcher = Matcher(user_data)
    
    # Print individual matches
    print("=== Individual User Matches ===")
    for user_id in user_data:
        print(f"\nTop matches for {user_id}:")
        matches = matcher.get_top_matches(user_id, top_n=3)
        for match_id, score in matches:
            print(f"{match_id}: {score:.2f} compatibility score")
        print("-" * 40)
    
    # Create and print groups
    groups = create_groups(matcher, user_data, group_size=8)
    print_groups(groups, matcher, user_data)

if __name__ == "__main__":
    main()