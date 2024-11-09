import pandas as pd
import glob
import os

def merge_preference_files():
    # Get all CSV files that start with 'preferences_'
    csv_files = glob.glob('preferences_*.csv')
    
    if not csv_files:
        print("No preference CSV files found!")
        return
    
    # Initialize list to store all dataframes
    all_users = []
    
    # Process each CSV file
    for i, file in enumerate(csv_files, 1):
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Pivot the dataframe to convert questions to columns
        user_df = df.pivot(columns='Question', values='Answer')
        
        # Add user ID
        user_df['User_ID'] = f'User_{i}'
        
        # Reorder columns to put User_ID first
        cols = ['User_ID'] + [col for col in user_df.columns if col != 'User_ID']
        user_df = user_df[cols]
        
        all_users.append(user_df)
    
    # Combine all user dataframes
    merged_df = pd.concat(all_users, ignore_index=True)
    
    # Save to new CSV file
    output_file = 'merged_preferences.csv'
    merged_df.to_csv(output_file, index=False)
    
    print(f"Successfully merged {len(csv_files)} files into {output_file}")
    print(f"Total users processed: {len(merged_df)}")
    
    # Optionally, clean up individual files
    cleanup = input("Do you want to delete individual preference files? (y/n): ").lower()
    if cleanup == 'y':
        for file in csv_files:
            os.remove(file)
        print("Individual preference files deleted.")

if __name__ == "__main__":
    merge_preference_files()
