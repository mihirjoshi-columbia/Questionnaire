import pandas as pd
import json

def convert_csv_to_json():
    print("Reading CSV file...")
    df = pd.read_csv('merged_preferences.csv')
    
    # Initialize dictionary to store the formatted data
    user_responses = {}
    
    print("Converting data format...")
    # Iterate through each row in the dataframe
    for index, row in df.iterrows():
        user_id = row['User_ID']  # Using correct column name
        
        # If this user isn't in our dictionary yet, add them
        if user_id not in user_responses:
            user_responses[user_id] = {}
        
        # Add non-empty responses to the user's data
        for column in df.columns:
            if column != 'User_ID' and pd.notna(row[column]) and row[column] != '':
                user_responses[user_id][column] = str(row[column])
    
    # Write to JSON file
    print("Writing to JSON file...")
    with open('responses.json', 'w') as f:
        json.dump(user_responses, f, indent=4, ensure_ascii=False)
    
    print("Conversion complete! Data saved to responses.json")
    print(f"Total number of users converted: {len(user_responses)}")

if __name__ == "__main__":
    try:
        convert_csv_to_json()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
