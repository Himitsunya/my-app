import json
import os
import random

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabsBase
from kivy.lang import Builder

DB_FILE = "my_dictionary.json"

# Вшиваем разметку KV прямо в Python-код
KV_INTERFACE = '''
MDBoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "Мой Словарь"
        elevation: 4

    MDTabs:
        id: tabs

        Tab:
            title: "Добавить"
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                MDTextField:
                    id: word_input
                    hint_text: "Слово / Фраза"
                    mode: "rectangle"

                MDTextField:
                    id: trans_input
                    hint_text: "Перевод"
                    mode: "rectangle"

                MDTextField:
                    id: context_input
                    hint_text: "Контекст / Пример (необязательно)"
                    mode: "rectangle"

                MDRaisedButton:
                    text: "СОХРАНИТЬ СЛОВО"
                    pos_hint: {"center_x": .5}
                    on_release: app.add_word()

                Widget:

        Tab:
            title: "Все слова"
            MDScrollView:
                MDList:
                    id: word_list_container

        Tab:
            title: "Карточки"
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"

                MDCard:
                    size_hint: (1, 0.5)
                    elevation: 2
                    radius: [15, ]
                    padding: "15dp"

                    MDLabel:
                        id: card_label
                        text: "Нажми 'Следующая карточка'"
                        halign: "center"
                        font_style: "H5"

                MDRectangleFlatButton:
                    text: "ПОКАЗАТЬ ПЕРЕВОД"
                    pos_hint: {"center_x": .5}
                    on_release: app.show_translation()

                MDRaisedButton:
                    text: "СЛЕДУЮЩАЯ КАРТОЧКА"
                    pos_hint: {"center_x": .5}
                    on_release: app.next_card()

                Widget:
'''

def load_words():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_words(words):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=4)

class Tab(MDScreen, MDTabsBase):
    pass

class VocabularyApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"
        self.words = load_words()
        self.current_card = None
        self.dialog = None
        return Builder.load_string(KV_INTERFACE)

    def on_start(self):
        self.refresh_word_list()

    def add_word(self):
        word_input = self.root.ids.word_input
        trans_input = self.root.ids.trans_input
        context_input = self.root.ids.context_input

        word = word_input.text.strip()
        translation = trans_input.text.strip()
        context = context_input.text.strip()

        if not word or not translation:
            self.show_alert("Ошибка", "Заполните слово и перевод!")
            return

        new_entry = {
            "word": word,
            "translation": translation,
            "context": context,
        }
        self.words.append(new_entry)
        save_words(self.words)

        word_input.text = ""
        trans_input.text = ""
        context_input.text = ""

        self.show_alert("Успех!", f"Слово '{word}' добавлено!")
        self.refresh_word_list()

    def refresh_word_list(self):
        container = self.root.ids.word_list_container
        container.clear_widgets()

        from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget

        for item in self.words:
            list_item = TwoLineAvatarIconListItem(
                text=item["word"], secondary_text=item["translation"]
            )
            delete_btn = IconRightWidget(
                icon="delete",
                on_release=lambda x, w=item["word"]: self.delete_word(w),
            )
            list_item.add_widget(delete_btn)
            container.add_widget(list_item)

    def delete_word(self, word_to_remove):
        self.words = [w for w in self.words if w["word"] != word_to_remove]
        save_words(self.words)
        self.refresh_word_list()

    def next_card(self):
        if not self.words:
            self.root.ids.card_label.text = "Словарь пуст!\nДобавьте слова."
            return

        self.current_card = random.choice(self.words)
        self.root.ids.card_label.text = self.current_card["word"]

    def show_translation(self):
        if self.current_card:
            text = f"{self.current_card['word']}\n\n—\n\n{self.current_card['translation']}"
            if self.current_card.get("context"):
                text += f"\n\n({self.current_card['context']})"
            self.root.ids.card_label.text = text

    def show_alert(self, title, text):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDRaisedButton(
                        text="ОК", on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
        else:
            self.dialog.title = title
            self.dialog.text = text
        self.dialog.open()

if __name__ == "__main__":
    VocabularyApp().run()
