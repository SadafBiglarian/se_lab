import sys
import json
import os
import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QGridLayout,
    QStyle,
)

DATA_FILE = "flashcards_data.json"
DAILY_GOAL = 10

DEFAULT_WORDS = [
    {"word": "Hello", "translation": "سلام", "category": "Basics", "known": False},
    {"word": "Goodbye", "translation": "خداحافظ", "category": "Basics", "known": False},
    {"word": "Thank you", "translation": "ممنون", "category": "Basics", "known": False},
    {"word": "Please", "translation": "لطفاً", "category": "Basics", "known": False},
    {"word": "Water", "translation": "آب", "category": "Food", "known": False},
    {"word": "Bread", "translation": "نان", "category": "Food", "known": False},
    {"word": "Coffee", "translation": "قهوه", "category": "Food", "known": False},
    {"word": "Hotel", "translation": "هتل", "category": "Travel", "known": False},
    {"word": "Airport", "translation": "فرودگاه", "category": "Travel", "known": False},
    {"word": "One", "translation": "یک", "category": "Numbers", "known": False},
    {"word": "Two", "translation": "دو", "category": "Numbers", "known": False},
    {"word": "Buy", "translation": "خریدن", "category": "Basics", "known": False},
]


@dataclass
class AppMeta:
    last_activity_date: Optional[str] = None
    streak_days: int = 0
    last_added_word: str = "Buy"
    last_added_translation: str = "خریدن"


class Storage:
    @staticmethod
    def load():
        if not os.path.exists(DATA_FILE):
            return DEFAULT_WORDS.copy(), AppMeta()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            words = data.get("words", DEFAULT_WORDS.copy()) or DEFAULT_WORDS.copy()
            meta_dict = data.get("meta", {})
            meta = AppMeta(**meta_dict) if isinstance(meta_dict, dict) else AppMeta()
            return words, meta
        except Exception:
            return DEFAULT_WORDS.copy(), AppMeta()

    @staticmethod
    def save(words, meta: AppMeta):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"words": words, "meta": asdict(meta)},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass


def make_panel(title: str) -> QFrame:
    panel = QFrame()
    panel.setObjectName("panel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(10)
    lbl = QLabel(title)
    lbl.setObjectName("panelTitle")
    layout.addWidget(lbl)
    return panel


def make_big_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    f = QFont()
    f.setPointSize(22)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setObjectName("bigTitle")
    return lbl


def btn(text: str, kind: str = "primary") -> QPushButton:
    b = QPushButton(text)
    b.setCursor(Qt.PointingHandCursor)
    b.setMinimumHeight(40)
    b.setObjectName(f"btn_{kind}")
    return b


class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Language Learning Flashcards")
        self.setMinimumSize(920, 560)

        self.words, self.meta = Storage.load()

        self.learn_index = 0
        self.learn_showing_translation = True

        self.quiz_active = False
        self.quiz_questions = []
        self.quiz_index = 0
        self.quiz_score = 0
        self.quiz_correct_translation = ""
        self.quiz_current_word = ""

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.build_dashboard_tab()
        self.build_learn_tab()
        self.build_words_tab()
        self.build_quiz_tab()

        self.tabs.setTabIcon(0, self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tabs.setTabIcon(1, self.style().standardIcon(QStyle.SP_DialogYesButton))
        self.tabs.setTabIcon(2, self.style().standardIcon(QStyle.SP_FileIcon))
        self.tabs.setTabIcon(
            3, self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        )

        self.apply_styles()
        self.refresh_all()

    def touch_activity(self):
        today = date.today()
        last = None
        if self.meta.last_activity_date:
            try:
                y, m, d = self.meta.last_activity_date.split("-")
                last = date(int(y), int(m), int(d))
            except Exception:
                last = None

        if last is None:
            self.meta.last_activity_date = today.isoformat()
            self.meta.streak_days = 0
        else:
            if last == today:
                pass
            elif last == today - timedelta(days=1):
                self.meta.streak_days += 1
                self.meta.last_activity_date = today.isoformat()
            else:
                self.meta.streak_days = 0
                self.meta.last_activity_date = today.isoformat()

    def total_words(self):
        return len(self.words)

    def learned_words(self):
        return sum(1 for w in self.words if w.get("known"))

    def daily_progress(self):
        return min(self.learned_words(), DAILY_GOAL)

    def build_dashboard_tab(self):
        tab = QWidget()
        root = QVBoxLayout(tab)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(16)

        root.addWidget(make_big_title("Language Learning Dashboard"))

        self.progress_panel = make_panel("☑  Your Progress")
        pl = self.progress_panel.layout()

        stats_row = QHBoxLayout()
        stats_row.setSpacing(40)

        left = QVBoxLayout()
        right = QVBoxLayout()

        self.lbl_total = QLabel("Total Words: 0")
        self.lbl_streak = QLabel("Current Streak: 0 days")
        self.lbl_learned = QLabel("Words Learned: 0")
        self.lbl_daily = QLabel("Daily Progress: 0/10")

        for w in [self.lbl_total, self.lbl_streak, self.lbl_learned, self.lbl_daily]:
            w.setObjectName("statLine")

        left.addWidget(self.lbl_total)
        left.addWidget(self.lbl_streak)
        right.addWidget(self.lbl_learned)
        right.addWidget(self.lbl_daily)

        stats_row.addLayout(left)
        stats_row.addStretch(1)
        stats_row.addLayout(right)
        pl.addLayout(stats_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progressLikeImage")
        pl.addWidget(self.progress_bar)

        root.addWidget(self.progress_panel)

        self.recent_panel = make_panel("📋  Recent Activity")
        rl = self.recent_panel.layout()

        self.recent_box = QLabel()
        self.recent_box.setObjectName("recentBox")
        self.recent_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.recent_box.setWordWrap(True)
        rl.addWidget(self.recent_box)

        root.addWidget(self.recent_panel)
        root.addStretch(1)

        self.tabs.addTab(tab, "Dashboard")

    def refresh_dashboard(self):
        total = self.total_words()
        learned = self.learned_words()
        daily = self.daily_progress()

        self.lbl_total.setText(f"Total Words: {total}")
        self.lbl_streak.setText(f"Current Streak: {self.meta.streak_days} days")
        self.lbl_learned.setText(f"Words Learned: {learned}")
        self.lbl_daily.setText(f"Daily Progress: {daily}/{DAILY_GOAL}")

        percent = int((daily / DAILY_GOAL) * 100) if DAILY_GOAL else 0
        self.progress_bar.setValue(percent)

        self.recent_box.setText(
            "Recent Activity:\n"
            f"• Total words in library: {total}\n"
            f"• Words mastered: {learned}\n"
            f"• Learning streak: {self.meta.streak_days} days\n"
            f"• Daily goal: {DAILY_GOAL} words\n"
            f"• Last added: {self.meta.last_added_word} ({self.meta.last_added_translation})"
        )

    def build_learn_tab(self):
        tab = QWidget()
        root = QVBoxLayout(tab)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(16)

        title = QLabel("Flashcard Learning")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("learnTitle")
        root.addWidget(title)

        card_outer = QFrame()
        card_outer.setObjectName("cardOuter")
        card_outer_layout = QVBoxLayout(card_outer)
        card_outer_layout.setContentsMargins(16, 16, 16, 16)
        card_outer_layout.setSpacing(10)

        self.card_main = QLabel("...")
        self.card_main.setAlignment(Qt.AlignCenter)
        self.card_main.setObjectName("cardMain")

        self.card_cat = QLabel("Category: ...")
        self.card_cat.setAlignment(Qt.AlignCenter)
        self.card_cat.setObjectName("cardCat")

        card_outer_layout.addWidget(self.card_main)
        card_outer_layout.addWidget(self.card_cat)

        center_row = QHBoxLayout()
        center_row.addStretch(1)
        center_row.addWidget(card_outer)
        center_row.addStretch(1)
        root.addLayout(center_row)

        self.btn_flip = btn("👁  Show Word", "info")
        self.btn_flip.clicked.connect(self.flip_card_like_image)
        root.addWidget(self.btn_flip)

        row2 = QHBoxLayout()
        self.btn_known = btn("✅  I Know This", "success")
        self.btn_unknown = btn("❌  Need Practice", "danger")
        self.btn_known.clicked.connect(lambda: self.mark_current_word(True))
        self.btn_unknown.clicked.connect(lambda: self.mark_current_word(False))
        row2.addWidget(self.btn_known)
        row2.addWidget(self.btn_unknown)
        root.addLayout(row2)

        self.learn_feedback = QLabel("")
        self.learn_feedback.setAlignment(Qt.AlignCenter)
        self.learn_feedback.setObjectName("learnFeedback")
        root.addWidget(self.learn_feedback)

        bottom = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_next = QPushButton("Next ▶")
        self.btn_prev.setObjectName("btn_small")
        self.btn_next.setObjectName("btn_small")
        self.btn_prev.clicked.connect(self.prev_card)
        self.btn_next.clicked.connect(self.next_card)
        bottom.addWidget(self.btn_prev)
        bottom.addWidget(self.btn_next)
        bottom.addStretch(1)
        root.addLayout(bottom)

        root.addStretch(1)
        self.tabs.addTab(tab, "Learn")

    def refresh_learn(self):
        if not self.words:
            self.card_main.setText("No Words")
            self.card_cat.setText("Category: -")
            for b in [
                self.btn_flip,
                self.btn_known,
                self.btn_unknown,
                self.btn_prev,
                self.btn_next,
            ]:
                b.setEnabled(False)
            if hasattr(self, "learn_feedback"):
                self.learn_feedback.setText("")
            return

        self.learn_index %= len(self.words)
        w = self.words[self.learn_index]

        self.learn_showing_translation = True
        self.card_main.setText(w["translation"])
        self.card_cat.setText(f"Category: {w['category']}")
        self.btn_flip.setText("👁  Show Word")

        for b in [
            self.btn_flip,
            self.btn_known,
            self.btn_unknown,
            self.btn_prev,
            self.btn_next,
        ]:
            b.setEnabled(True)

    def flip_card_like_image(self):
        if not self.words:
            return
        w = self.words[self.learn_index]
        if self.learn_showing_translation:
            self.card_main.setText(w["word"])
            self.btn_flip.setText("👁  Show Translation")
        else:
            self.card_main.setText(w["translation"])
            self.btn_flip.setText("👁  Show Word")
        self.learn_showing_translation = not self.learn_showing_translation

        self.touch_activity()
        Storage.save(self.words, self.meta)
        self.refresh_dashboard()

    def next_card(self):
        if not self.words:
            return
        self.learn_index = (self.learn_index + 1) % len(self.words)
        self.refresh_learn()

    def prev_card(self):
        if not self.words:
            return
        self.learn_index = (self.learn_index - 1) % len(self.words)
        self.refresh_learn()

    def mark_current_word(self, known: bool):
        if not self.words:
            return

        prev = bool(self.words[self.learn_index].get("known"))
        self.words[self.learn_index]["known"] = known

        if prev == known:
            self.learn_feedback.setText("No change (already set)")
        else:
            self.learn_feedback.setText(
                "Saved ✅" if known else "Marked for Practice ❌"
            )

        QTimer.singleShot(1200, lambda: self.learn_feedback.setText(""))

        self.touch_activity()
        Storage.save(self.words, self.meta)
        self.refresh_dashboard()
        self.refresh_words_list()
        self.next_card()

    def build_words_tab(self):
        tab = QWidget()
        root = QVBoxLayout(tab)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        self.add_panel = QFrame()
        self.add_panel.setObjectName("panel")
        addL = QVBoxLayout(self.add_panel)
        addL.setContentsMargins(14, 12, 14, 12)
        addL.setSpacing(10)

        t = QLabel("Add New Word")
        t.setObjectName("sectionTitleSimple")
        addL.addWidget(t)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        lbl_w = QLabel("Word:")
        lbl_t = QLabel("Translation:")
        lbl_c = QLabel("Category:")
        for x in [lbl_w, lbl_t, lbl_c]:
            x.setObjectName("fieldLabel")

        self.in_word = QLineEdit()
        self.in_trans = QLineEdit()
        self.in_cat = QComboBox()
        self.in_cat.addItems(["Basics", "Food", "Travel", "Numbers"])

        self.in_word.setObjectName("inputLight")
        self.in_trans.setObjectName("inputLight")
        self.in_cat.setObjectName("inputLight")

        grid.addWidget(lbl_w, 0, 0)
        grid.addWidget(self.in_word, 0, 1)
        grid.addWidget(lbl_t, 1, 0)
        grid.addWidget(self.in_trans, 1, 1)
        grid.addWidget(lbl_c, 2, 0)
        grid.addWidget(self.in_cat, 2, 1)
        addL.addLayout(grid)

        self.btn_add = btn("➕  Add Word", "success")
        self.btn_add.clicked.connect(self.add_word)
        addL.addWidget(self.btn_add)

        root.addWidget(self.add_panel)

        self.vocab_panel = QFrame()
        self.vocab_panel.setObjectName("panel")
        vocabL = QVBoxLayout(self.vocab_panel)
        vocabL.setContentsMargins(14, 12, 14, 12)
        vocabL.setSpacing(10)

        t2 = QLabel("Your Vocabulary")
        t2.setObjectName("sectionTitleSimple")
        vocabL.addWidget(t2)

        self.list_vocab = QListWidget()
        self.list_vocab.setObjectName("vocabList")
        vocabL.addWidget(self.list_vocab, 1)

        self.btn_delete = btn("🗑  Delete Selected", "danger")
        self.btn_delete.clicked.connect(self.delete_selected)
        vocabL.addWidget(self.btn_delete)

        root.addWidget(self.vocab_panel, 1)
        self.tabs.addTab(tab, "Words")

    def refresh_words_list(self):
        self.list_vocab.clear()
        for w in self.words:
            self.list_vocab.addItem(
                QListWidgetItem(
                    f"⌛  {w['word']} - {w['translation']} ({w['category']})"
                )
            )

    def add_word(self):
        w = self.in_word.text().strip()
        t = self.in_trans.text().strip()
        c = self.in_cat.currentText().strip()
        if not w or not t:
            QMessageBox.warning(
                self, "Missing Info", "Please enter word + translation."
            )
            return
        self.words.append({"word": w, "translation": t, "category": c, "known": False})
        self.meta.last_added_word = w
        self.meta.last_added_translation = t
        self.in_word.clear()
        self.in_trans.clear()
        self.touch_activity()
        Storage.save(self.words, self.meta)
        self.refresh_all()

    def delete_selected(self):
        row = self.list_vocab.currentRow()
        if row < 0:
            return
        del self.words[row]
        self.touch_activity()
        Storage.save(self.words, self.meta)
        self.refresh_all()

    def build_quiz_tab(self):
        tab = QWidget()
        root = QVBoxLayout(tab)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        self.quiz_title = QLabel("Press Start Quiz")
        self.quiz_title.setAlignment(Qt.AlignCenter)
        self.quiz_title.setObjectName("quizTitle")
        root.addWidget(self.quiz_title)

        self.quiz_panel = QFrame()
        self.quiz_panel.setObjectName("quizPanel")
        ql = QVBoxLayout(self.quiz_panel)
        ql.setContentsMargins(12, 12, 12, 12)
        ql.setSpacing(10)

        self.quiz_options = QListWidget()
        self.quiz_options.setObjectName("quizList")
        self.quiz_options.itemClicked.connect(self.quiz_pick_option)
        ql.addWidget(self.quiz_options)

        root.addWidget(self.quiz_panel, 1)

        self.btn_start_quiz = btn("Start Quiz", "primary")
        self.btn_start_quiz.clicked.connect(self.start_quiz)
        root.addWidget(self.btn_start_quiz)

        self.tabs.addTab(tab, "Quiz")

    def start_quiz(self):
        if len(self.words) < 5:
            QMessageBox.warning(
                self, "Not Enough Words", "Add at least 5 words to start the quiz."
            )
            return
        self.quiz_active = True
        self.quiz_score = 0
        self.quiz_questions = random.sample(self.words, min(10, len(self.words)))
        self.quiz_index = 0
        self.show_quiz_question()
        self.touch_activity()
        Storage.save(self.words, self.meta)
        self.refresh_dashboard()

    def show_quiz_question(self):
        w = self.quiz_questions[self.quiz_index]
        self.quiz_current_word = w["word"]
        self.quiz_correct_translation = w["translation"]

        self.quiz_title.setText(
            f"Question {self.quiz_index + 1}/{len(self.quiz_questions)}\n"
            f"What is the translation of: '{w['word']}'?"
        )

        opts = {w["translation"]}
        while len(opts) < 4:
            opts.add(random.choice(self.words)["translation"])
        opts = list(opts)
        random.shuffle(opts)

        self.quiz_options.clear()
        for o in opts:
            self.quiz_options.addItem(QListWidgetItem(o))

    def quiz_pick_option(self, item: QListWidgetItem):
        if not self.quiz_active:
            return
        chosen = item.text()
        if chosen == self.quiz_correct_translation:
            self.quiz_score += 1
            QMessageBox.information(self, "Correct", "Good job!")
        else:
            QMessageBox.warning(
                self,
                "Incorrect",
                f"Sorry! '{self.quiz_current_word}' = '{self.quiz_correct_translation}'",
            )

        self.quiz_index += 1
        if self.quiz_index >= len(self.quiz_questions):
            self.quiz_active = False
            QMessageBox.information(
                self,
                "Quiz Complete",
                f"Score: {self.quiz_score}/{len(self.quiz_questions)}",
            )
            self.quiz_title.setText("Press Start Quiz")
            self.quiz_options.clear()
        else:
            self.show_quiz_question()

        self.touch_activity()
        Storage.save(self.words, self.meta)
        self.refresh_dashboard()

    def apply_styles(self):
        self.setStyleSheet(
            """
        QMainWindow { background: #2c3f52; }
        QTabWidget::pane { border: 0px; background: #2c3f52; }
        QTabBar::tab {
            background: #34495e; color: #ecf0f1; padding: 10px 18px; margin-right: 4px;
            border: 1px solid #22313f; min-width: 110px; font-weight: 600;
        }
        QTabBar::tab:selected { background: #3498db; color: white; }

        QLabel#bigTitle { color: #ecf0f1; font-size: 26px; font-weight: 700; }
        QLabel#learnTitle, QLabel#quizTitle {
            color: #ecf0f1; font-size: 20px; font-weight: 700; padding: 8px 0;
        }

        QFrame#panel {
            background: #34495e; border: 2px solid #3498db; border-radius: 10px;
        }
        QLabel#panelTitle { color: #ecf0f1; font-size: 18px; font-weight: 700; }
        QLabel#statLine { color: #ecf0f1; font-size: 14px; }

        QProgressBar#progressLikeImage {
            background: #ffffff; border: 1px solid #1f2d3a; border-radius: 4px;
            height: 22px; text-align: center; font-weight: 800; color: #ffffff;
        }
        QProgressBar#progressLikeImage::chunk {
            background: #27ae60; border-radius: 4px;
        }

        QLabel#recentBox {
            background: #2b3a49; color: #ecf0f1; border: 1px solid #22313f;
            border-radius: 8px; padding: 10px; min-height: 210px; font-size: 13px;
        }

        QFrame#cardOuter {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                                        stop:0 #4d7bd6, stop:1 #7d5bd6);
            border: 2px solid #1f2d3a; border-radius: 12px;
            min-width: 260px; max-width: 320px;
        }
        QLabel#cardMain {
            background: rgba(0,0,0,0.15);
            border: 2px solid rgba(0,0,0,0.35);
            border-radius: 10px;
            padding: 22px 12px;
            color: #ecf0f1;
            font-size: 26px;
            font-weight: 800;
        }
        QLabel#cardCat {
            background: rgba(0,0,0,0.15);
            border: 2px solid rgba(0,0,0,0.35);
            border-radius: 10px;
            padding: 14px 12px;
            color: #ecf0f1;
            font-size: 14px;
            font-weight: 700;
        }

        QPushButton#btn_primary, QPushButton#btn_info {
            background: #3498db; color: white; border: 0px;
            border-radius: 8px; font-weight: 800;
        }
        QPushButton#btn_primary:hover, QPushButton#btn_info:hover {
            background: #2d86c2;
        }
        QPushButton#btn_success {
            background: #27ae60; color: white; border: 0px;
            border-radius: 8px; font-weight: 800;
        }
        QPushButton#btn_success:hover { background: #219a54; }
        QPushButton#btn_danger {
            background: #e74c3c; color: white; border: 0px;
            border-radius: 8px; font-weight: 800;
        }
        QPushButton#btn_danger:hover { background: #d64537; }

        QPushButton#btn_small {
            background: #3b8ec6; color: white; border: 0px;
            border-radius: 8px; padding: 10px 16px;
            font-weight: 800; min-height: 36px;
        }
        QPushButton#btn_small:hover { background: #347fb2; }

        QLabel#sectionTitleSimple { color: #ecf0f1; font-size: 16px; font-weight: 800; }
        QLabel#fieldLabel { color: #ecf0f1; font-weight: 700; }
        QLineEdit#inputLight, QComboBox#inputLight {
            background: white; color: #0b0f14; border: 1px solid #22313f;
            border-radius: 4px; padding: 8px 10px; min-height: 30px;
        }

        QListWidget#vocabList {
            background: #2b3a49; color: #ecf0f1;
            border: 1px solid #22313f; border-radius: 8px;
            padding: 6px; font-size: 14px;
        }
        QListWidget#vocabList::item { padding: 6px; }
        QListWidget#vocabList::item:selected {
            background: #3498db; color: white;
        }

        QFrame#quizPanel {
            background: #34495e; border: 0px; border-radius: 8px;
        }
        QListWidget#quizList {
            background: #2b3a49; color: #ecf0f1;
            border: 1px solid #22313f; border-radius: 6px;
            padding: 6px; font-size: 16px; min-height: 240px;
        }
        QListWidget#quizList::item { padding: 6px; }
        QListWidget#quizList::item:selected {
            background: #ffffff; color: #0b0f14;
        }

        QLabel#learnFeedback {
            color: #ecf0f1;
            font-weight: 800;
            padding: 6px;
        }
    """
        )

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_learn()
        self.refresh_words_list()

    def closeEvent(self, event):
        Storage.save(self.words, self.meta)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FlashcardApp()
    win.show()
    sys.exit(app.exec_())
