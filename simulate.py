import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

class UserSimulator:
    def __init__(self):
        # Define all possible responses for each question
        self.responses = {
            "What is your favorite book genre?": [
                "Romance", "Mystery", "Fantasy", "Sci-Fi", "Horror", "Non-Fiction",
                "Historical Fiction", "Biography", "Adventure", "Thriller"
            ],
            "What is your favorite color?": [
                "Red", "Blue", "Green", "Purple", "Yellow", "Orange", "Pink",
                "Black", "White", "Grey"
            ],
            "What is your favorite food cuisine?": [
                "Italian", "Chinese", "Mexican", "Indian", "Japanese", "Thai",
                "French", "Greek", "American", "Korean"
            ],
            "What is your favorite movie genre?": [
                "Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance",
                "Documentary", "Thriller", "Animation", "Adventure"
            ],
            "What is your favorite season?": [
                "Spring", "Summer", "Fall", "Winter"
            ],
            "What is your ideal vacation destination?": [
                "Beach", "Mountains", "City", "Countryside", "Islands", "Desert",
                "Forest", "Lake", "Historical Sites", "Theme Parks"
            ],
            "What is your preferred hobby?": [
                "Reading", "Gaming", "Cooking", "Sports", "Music", "Art",
                "Photography", "Writing", "Gardening", "Travel"
            ],
            "Who is your favorite music artist?": [
                "Taylor Swift", "Drake", "BTS", "The Beatles", "Ed Sheeran",
                "Beyoncé", "Lady Gaga", "Eminem", "Coldplay", "The Weeknd"
            ]
        }

    def generate_user_preferences(self, user_id):
        """Generate preferences for a single user"""
        preferences = []
        
        # Generate one response for each question
        for question, options in self.responses.items():
            preferences.append({
                'User_ID': f'User_{user_id}',
                question: random.choice(options)
            })
        
        return preferences

def simulate_users(num_users=40):
    print(f"Starting simulation of {num_users} users...")
    simulator = UserSimulator()
    all_preferences = []
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=min(num_users, 10)) as executor:
        # Submit all tasks
        future_to_user = {
            executor.submit(simulator.generate_user_preferences, i+1): i+1 
            for i in range(num_users)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_user):
            user_id = future_to_user[future]
            try:
                preferences = future.result()
                all_preferences.extend(preferences)
                print(f"Simulated user {user_id}/{num_users}")
            except Exception as e:
                print(f"Error simulating user {user_id}: {str(e)}")
    
    # Convert to DataFrame and save to CSV
    import pandas as pd
    df = pd.DataFrame(all_preferences)
    df.to_csv('merged_preferences.csv', index=False)
    print("Simulation complete! Data saved to merged_preferences.csv")

if __name__ == "__main__":
    simulate_users(40)
