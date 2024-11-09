import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime

class PreferenceQuestionnaire:
    def __init__(self, root):
        self.root = root
        self.root.title("Preference Questionnaire")
        self.root.geometry("600x500")
        
        self.questions = [
            "What is your favorite color?",
            "Who is your favorite music artist?",
            "What is your favorite movie genre?",
            "What is your favorite food cuisine?",
            "What is your ideal vacation destination?",
            "What is your preferred hobby?",
            "What is your favorite season?",
            "What is your favorite book genre?"
        ]
        
        self.answers = {}
        self.current_question = 0
        
        # Create and pack widgets
        self.question_label = ttk.Label(root, text="", wraplength=500, font=("Arial", 12))
        self.question_label.pack(pady=20)
        
        self.answer_entry = ttk.Entry(root, width=40)
        self.answer_entry.pack(pady=10)
        
        self.next_button = ttk.Button(root, text="Next", command=self.next_question)
        self.next_button.pack(pady=10)
        
        # Start with first question
        self.show_question()
    
    def show_question(self):
        if self.current_question < len(self.questions):
            self.question_label.config(text=self.questions[self.current_question])
            if self.current_question == len(self.questions) - 1:
                self.next_button.config(text="Submit")
        
    def next_question(self):
        # Save current answer
        current_answer = self.answer_entry.get().strip()
        if current_answer:
            self.answers[self.questions[self.current_question]] = current_answer
            self.answer_entry.delete(0, tk.END)
            
            if self.current_question < len(self.questions) - 1:
                self.current_question += 1
                self.show_question()
            else:
                self.save_to_csv()
                self.root.destroy()
        
    def save_to_csv(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"preferences_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Question', 'Answer'])
            for question, answer in self.answers.items():
                writer.writerow([question, answer])

if __name__ == "__main__":
    root = tk.Tk()
    app = PreferenceQuestionnaire(root)
    root.mainloop()

