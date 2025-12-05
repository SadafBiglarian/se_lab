import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QRadioButton, QMessageBox
from PyQt5.QtCore import Qt

class LanguageLearningApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Sample data for demonstration
        self.words = [
            {"word": "Hello", "translation": "سلام", "category": "Basics"},
            {"word": "Goodbye", "translation": "خداحافظ", "category": "Basics"},
            {"word": "Thank you", "translation": "ممنون", "category": "Basics"},
            {"word": "Please", "translation": "لطفا", "category": "Basics"},
            {"word": "Water", "translation": "آب", "category": "Food"},
            {"word": "Bread", "translation": "نان", "category": "Food"},
            {"word": "Coffee", "translation": "قهوه", "category": "Food"},
            {"word": "Hotel", "translation": "هتل", "category": "Travel"},
            {"word": "Airport", "translation": "فرودگاه", "category": "Travel"},
            {"word": "One", "translation": "یک", "category": "Numbers"},
            {"word": "Two", "translation": "دو", "category": "Numbers"},
            {"word": "Buy", "translation": "خریدن", "category": "Basics"},
        ]
        
        self.current_flashcard_index = 0  # Initialize the flashcard index here
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Language Learning Flashcards')
        self.setGeometry(100, 100, 800, 600)

        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self.createDashboardTab(), "Dashboard")
        tabs.addTab(self.createLearnTab(), "Learn")
        tabs.addTab(self.createWordsTab(), "Words")
        tabs.addTab(self.createQuizTab(), "Quiz")

        self.setCentralWidget(tabs)

    def createDashboardTab(self):
        # Code for Dashboard remains the same
        pass

    def createLearnTab(self):
        learn = QWidget()
        layout = QVBoxLayout()

        # Display current word
        self.word_label = QLabel(self.words[self.current_flashcard_index]['word'])
        self.category_label = QLabel(f"Category: {self.words[self.current_flashcard_index]['category']}")

        # Buttons for interaction
        self.show_word_button = QPushButton('Show Word')
        self.know_button = QPushButton('I Know This')
        self.need_practice_button = QPushButton('Need Practice')

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.know_button)
        button_layout.addWidget(self.need_practice_button)

        # Navigation buttons
        self.previous_button = QPushButton('◁ Previous')
        self.next_button = QPushButton('Next ▷')

        layout.addWidget(self.word_label)
        layout.addWidget(self.category_label)
        layout.addWidget(self.show_word_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.previous_button)
        layout.addWidget(self.next_button)

        # Button connections
        self.show_word_button.clicked.connect(self.showWord)
        self.know_button.clicked.connect(self.knowThis)
        self.need_practice_button.clicked.connect(self.needPractice)
        self.previous_button.clicked.connect(self.previousFlashcard)
        self.next_button.clicked.connect(self.nextFlashcard)

        learn.setLayout(layout)
        return learn

    def showWord(self):
        # Show translation of the current word
        self.word_label.setText(self.words[self.current_flashcard_index]['translation'])

    def knowThis(self):
        # Logic when user marks the word as known
        print(f"Word {self.words[self.current_flashcard_index]['word']} marked as known.")
        self.nextFlashcard()  # Move to next word

    def needPractice(self):
        # Logic when user needs more practice for the word
        print(f"Word {self.words[self.current_flashcard_index]['word']} marked as needing practice.")
        self.nextFlashcard()  # Move to next word

    def previousFlashcard(self):
        # Show previous flashcard
        if self.current_flashcard_index > 0:
            self.current_flashcard_index -= 1
            self.updateFlashcard()

    def nextFlashcard(self):
        # Show next flashcard
        if self.current_flashcard_index < len(self.words) - 1:
            self.current_flashcard_index += 1
            self.updateFlashcard()

    def updateFlashcard(self):
        # Update the word and category labels
        self.word_label.setText(self.words[self.current_flashcard_index]['word'])
        self.category_label.setText(f"Category: {self.words[self.current_flashcard_index]['category']}")

    def createWordsTab(self):
        words = QWidget()
        layout = QVBoxLayout()

        # Add new word form
        add_word_label = QLabel('Add New Word:')
        word_input = QLineEdit()
        translation_input = QLineEdit()
        category_input = QComboBox()
        category_input.addItems(['Basics', 'Food', 'Travel', 'Numbers'])

        add_button = QPushButton('Add Word')

        layout.addWidget(add_word_label)
        layout.addWidget(word_input)
        layout.addWidget(translation_input)
        layout.addWidget(category_input)
        layout.addWidget(add_button)

        # Your vocabulary list
        vocabulary_label = QLabel('Your Vocabulary:')
        vocabulary_list = QListWidget()
        self.updateVocabularyList(vocabulary_list)

        layout.addWidget(vocabulary_label)
        layout.addWidget(vocabulary_list)

        words.setLayout(layout)
        return words

    def createQuizTab(self):
        quiz = QWidget()
        layout = QVBoxLayout()

        # Quiz Question
        question_label = QLabel(f"Question {self.current_flashcard_index + 1}/10\n"
                                f"What is the translation of: '{self.words[self.current_flashcard_index]['word']}'?")
        
        options_layout = QVBoxLayout()
        correct_answer = self.words[self.current_flashcard_index]['translation']
        incorrect_answers = ["آب", "قهوه", "نان"]  # Sample incorrect answers

        # Shuffle answers to make it random
        answers = [correct_answer] + incorrect_answers
        answers = sorted(answers, key=lambda x: random.random())

        # Create radio buttons for the answers
        self.answer_buttons = []
        for answer in answers:
            radio_button = QRadioButton(answer)
            self.answer_buttons.append(radio_button)
            options_layout.addWidget(radio_button)

        # Submit button
        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(lambda: self.checkAnswer(correct_answer))

        layout.addWidget(question_label)
        layout.addLayout(options_layout)
        layout.addWidget(submit_button)

        quiz.setLayout(layout)
        return quiz

    def checkAnswer(self, correct_answer):
        # Check selected answer
        selected_answer = None
        for button in self.answer_buttons:
            if button.isChecked():
                selected_answer = button.text()

        if selected_answer == correct_answer:
            self.showMessageBox("Correct", "Well done! You answered correctly.", "green")
        else:
            self.showMessageBox("Incorrect", f"Sorry! '{self.words[self.current_flashcard_index]['word']}' = {correct_answer}", "red")

        self.nextQuestion()

    def showMessageBox(self, title, message, color):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information if color == "green" else QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        # Set the color of the message box based on correct/incorrect
        msg_box.setStyleSheet(f"QMessageBox {{ background-color: {color}; }}")

        msg_box.exec_()

    def nextQuestion(self):
        # Move to next question
        if self.current_flashcard_index < len(self.words) - 1:
            self.current_flashcard_index += 1
            self.initUI()  # Recreate UI to show next question
        else:
            self.showMessageBox("Quiz Finished", "You've completed the quiz!", "green")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LanguageLearningApp()
    window.show()
    sys.exit(app.exec_())
