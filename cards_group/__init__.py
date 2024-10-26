from aqt import mw
from aqt.utils import showInfo, getFile
from aqt.qt import QAction
from aqt.reviewer import Reviewer
from aqt import gui_hooks
import os
import re
import datetime

GROUP_TAG_PREFIX = "group_"

'''
模板
011(2)writingA1

1.
sentence1
world1
world2

2.
sentence2
world3
world4

生成标签
011(2)writingA1 1 group_1
011(2)writingA1 2 group_1
011(2)writingA1 group_1 sentence
011(2)writingA1 1 group_2
011(2)writingA1 2 group_2
011(2)writingA1 group_2 sentence
'''
def get_group_number_from_index(index):
    """Generate group number based on the index (starting from 1)."""
    return index

def import_grouped_txt():
    """Import a .txt file with specific format, automatically adding tags and inserting cards into a specified deck."""

    def on_file_selected(file_path):
        if not file_path:
            return  # No file was selected or the dialog was cancelled

        # Create or get today's deck
        today = datetime.datetime.now()
        parent_deck_name = today.strftime("%Y-%m-%d")
        parent_deck_id = mw.col.decks.id(parent_deck_name)

        groups = []
        current_group = {'words': [], 'sentence': None}
        group_started = False
        identifier = None

        with open(file_path, 'r', encoding='utf-8') as infile:
            for line_num, line in enumerate(infile):
                line = line.strip()
                if line_num == 0:
                    # First line is the identifier
                    identifier = line
                elif re.match(r'^\d+\.', line):
                    # Detect a new group starting
                    if current_group['words'] or current_group['sentence']:
                        groups.append(current_group)
                        current_group = {'words': [], 'sentence': None}
                    group_started = True
                elif group_started:
                    if not line:
                        continue
                    # Detect sentence or word and remove the prefix
                    if line.startswith("Sentence: "):
                        current_group['sentence'] = line.replace("Sentence: ", "")
                    elif line.startswith("Word: "):
                        current_group['words'].append(line.replace("Word: ", ""))

            # Add the last group if there is any content left
            if current_group['words'] or current_group['sentence']:
                groups.append(current_group)

        for idx, group in enumerate(groups, start=1):
            group_tag = f'group_{get_group_number_from_index(idx)}'
            sentence_tag = 'sentence'

            # Add word cards first
            for word_idx, word in enumerate(group['words'], start=1):
                front = word
                back = word
                word_tags = [identifier, group_tag, str(word_idx)]
                add_note_to_deck(front, back, word_tags, parent_deck_id)

            # Add sentence card after all word cards
            if group['sentence']:
                front = group['sentence']
                back = group['sentence']
                tags = [identifier, group_tag, sentence_tag]
                add_note_to_deck(front, back, tags, parent_deck_id)

        showInfo("Successfully imported TXT file and created cards in the specified deck.")

    # Open file dialog to choose a .txt file
    getFile(mw, "选择要导入的 TXT 文件", on_file_selected, "Text Files (*.txt)")

def setup_menu():
    action = QAction("导入分组 TXT", mw)
    action.triggered.connect(import_grouped_txt)
    mw.form.menuTools.addAction(action)

gui_hooks.main_window_did_init.append(setup_menu)

def add_note_to_deck(front, back, tags, deck_id):
    model_name = "Grouped_cards"
    model = mw.col.models.byName(model_name)

    if not model:
        showInfo(f"模型 '{model_name}' 未找到。请确保使用的模型支持音频字段。")
        return

    note = mw.col.newNote()
    note.model()['name'] = model_name
    note.fields[0] = front
    note.fields[1] = back
    note.tags.extend(tags)
    note.model()['did'] = deck_id  # Set the deck ID for the note

    try:
        mw.col.addNote(note)
    except Exception as e:
        showInfo(f"添加卡片时出错: {e}")
