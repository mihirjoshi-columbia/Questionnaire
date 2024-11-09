import pandas as pd
import numpy as np
from openai import OpenAI
import os
from time import sleep
from dotenv import load_dotenv

# Load environment variables at the start of your script
load_dotenv()

class PreferencesMatcher:
    def __init__(self, csv_file='merged_preferences.csv'):
        self.df = pd.read_csv(csv_file)
        self.user_ids = self.df['User_ID'].tolist()
        
        # Get API key from environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
    def get_llm_compatibility_score(self, user1_data, user2_data):
        """Use GPT to analyze compatibility between two users"""
        # Create a detailed prompt about both users
        prompt = f"""
        Analyze the compatibility between two users based on their preferences:

        User 1 Preferences:
        {self._format_preferences(user1_data)}

        User 2 Preferences:
        {self._format_preferences(user2_data)}

        Please provide:
        1. A compatibility score between 0-100
        2. A brief explanation of why they would or wouldn't be compatible
        3. List their key common interests

        Format your response exactly like this example:
        SCORE: 85
        EXPLANATION: These users would be highly compatible due to their shared interests in...
        COMMON_INTERESTS: music (Taylor Swift), movies (Action), etc.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing compatibility between people based on their interests and preferences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return self._parse_llm_response(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            return {
                'score': 50,
                'explanation': "Error in LLM analysis",
                'common_interests': []
            }
    
    def _format_preferences(self, user_data):
        """Format user preferences for the prompt"""
        return "\n".join([f"{col}: {user_data[col]}" for col in user_data.index if col != 'User_ID'])
    
    def _parse_llm_response(self, response):
        """Parse the LLM response into structured data"""
        lines = response.split('\n')
        result = {
            'score': 50,
            'explanation': "",
            'common_interests': []
        }
        
        for line in lines:
            if line.startswith('SCORE:'):
                result['score'] = int(line.replace('SCORE:', '').strip())
            elif line.startswith('EXPLANATION:'):
                result['explanation'] = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('COMMON_INTERESTS:'):
                interests = line.replace('COMMON_INTERESTS:', '').strip()
                result['common_interests'] = [i.strip() for i in interests.split(',')]
                
        return result
    
    def get_top_matches(self, user_id, top_n=5):
        """Get top N matches for a specific user using LLM analysis"""
        user_data = self.df[self.df['User_ID'] == user_id].iloc[0]
        matches = []
        
        # Get compatibility scores for all other users
        for other_id in self.user_ids:
            if other_id != user_id:
                other_data = self.df[self.df['User_ID'] == other_id].iloc[0]
                
                # Get LLM analysis
                compatibility = self.get_llm_compatibility_score(user_data, other_data)
                
                matches.append({
                    'match_id': other_id,
                    'compatibility': compatibility
                })
                
                # Add a small delay to avoid rate limiting
                sleep(0.5)
        
        # Sort by compatibility score and get top N
        matches.sort(key=lambda x: x['compatibility']['score'], reverse=True)
        return matches[:top_n]
    
    def generate_all_matches(self, min_group_size=8, max_group_size=10):
        """Generate optimal groupings using LLM compatibility scores"""
        available_users = set(self.user_ids)
        groups = []
        
        while len(available_users) >= min_group_size:
            current_group = []
            
            # Start with a random user
            first_user = available_users.pop()
            current_group.append(first_user)
            
            while len(current_group) < max_group_size and available_users:
                best_match = None
                best_score = -1
                
                # Get group compatibility scores
                for user in available_users:
                    avg_score = 0
                    for member in current_group:
                        user_data = self.df[self.df['User_ID'] == user].iloc[0]
                        member_data = self.df[self.df['User_ID'] == member].iloc[0]
                        compatibility = self.get_llm_compatibility_score(user_data, member_data)
                        avg_score += compatibility['score']
                    
                    avg_score /= len(current_group)
                    
                    if avg_score > best_score:
                        best_score = avg_score
                        best_match = user
                
                if best_match:
                    current_group.append(best_match)
                    available_users.remove(best_match)
                    
                    if len(available_users) < (min_group_size - len(current_group)):
                        current_group.extend(list(available_users))
                        available_users.clear()
                        break
            
            groups.append(current_group)
        
        return groups

def main():
    # Make sure OPENAI_API_KEY is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize matcher
    matcher = PreferencesMatcher()
    
    # Generate and display individual matches
    print("\n=== Individual User Matches ===")
    for user_id in matcher.user_ids[:2]:  # Show first 2 users as example
        print(f"\nTop matches for {user_id}:")
        matches = matcher.get_top_matches(user_id, top_n=3)
        for match in matches:
            print(f"\nMatch: {match['match_id']}")
            print(f"Compatibility Score: {match['compatibility']['score']}%")
            print(f"Explanation: {match['compatibility']['explanation']}")
            print("Common Interests:")
            for interest in match['compatibility']['common_interests']:
                print(f"  - {interest}")
    
    # Generate and display optimal groups
    print("\n=== Optimal Groups ===")
    groups = matcher.generate_all_matches()
    for i, group in enumerate(groups, 1):
        print(f"\nGroup {i} ({len(group)} members):")
        print(", ".join(group))

if __name__ == "__main__":
    main()