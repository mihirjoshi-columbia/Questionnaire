import random
import tkinter as tk
from time import sleep

def simulate_user():
    # Create root window
    root = tk.Tk()
    app = PreferenceQuestionnaire(root)
    
    try:
        # Simulate answering each question
        while app.current_question < len(app.questions):
            # Random delay to simulate reading (1-3 seconds)
            sleep(random.uniform(1, 3))
            
            # Get current question widget and entry
            entry = app.answer_entry
            
            # Generate random answers based on the question
            current_question = app.questions[app.current_question]
            answer = generate_random_answer(current_question)
            
            # Input the answer
            entry.insert(0, answer)
            
            # Click next/submit button
            app.next_button.invoke()
            
            # Update the GUI
            try:
                root.update()
            except tk.TclError:
                break
                
    except Exception as e:
        print(f"Error during simulation: {e}")
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass

def generate_random_answer(question):
    """Generate contextual random answers based on the question."""
    if "color" in question.lower():
        return random.choice(["Blue", "Red", "Green", "Yellow", "Purple", "Orange"])
    elif "music artist" in question.lower():
        return random.choice(["Taylor Swift", "Ed Sheeran", "Drake", "BTS", "The Beatles"])
    elif "movie genre" in question.lower():
        return random.choice(["Action", "Comedy", "Drama", "Sci-Fi", "Horror"])
    elif "food cuisine" in question.lower():
        return random.choice(["Italian", "Chinese", "Mexican", "Indian", "Japanese"])
    elif "vacation" in question.lower():
        return random.choice(["Beach", "Mountains", "City", "Countryside", "Islands"])
    elif "hobby" in question.lower():
        return random.choice(["Reading", "Gaming", "Cooking", "Sports", "Photography"])
    elif "season" in question.lower():
        return random.choice(["Spring", "Summer", "Fall", "Winter"])
    elif "book genre" in question.lower():
        return random.choice(["Fantasy", "Mystery", "Romance", "Sci-Fi", "Non-Fiction"])
    else:
        return f"Test response {random.randint(1, 100)}"

def main():
    print("Starting simulation of 20 users...")
    for i in range(20):
        print(f"Simulating user {i+1}/20")
        simulate_user()
        sleep(random.uniform(1, 2))  # Wait between users
    print("Simulation complete!")

if __name__ == "__main__":
    from question import PreferenceQuestionnaire
    main()
