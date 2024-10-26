from aqt import mw
from aqt.utils import showInfo, getFile
from aqt.qt import QAction
from aqt import gui_hooks
import os
import re

AUDIO_FOLDER = r"C:\Users\CNCHREN3\PythonProjects\WordsAudioDownload\TTS_audio_files"


def match_audio_to_cards():
    """Match audio files to existing cards based on tags and replace the front content with the audio."""
    # Ensure audio folder exists
    audio_folder_path = os.path.join(mw.pm.profileFolder(), AUDIO_FOLDER)
    if not os.path.exists(audio_folder_path):
        showInfo(f"音频文件夹 '{AUDIO_FOLDER}' 未找到，请确认音频文件夹存在。")
        return

    # Get all notes from the collection
    notes = mw.col.find_notes("")
    updated_notes = 0

    for note_id in notes:
        note = mw.col.getNote(note_id)
        tags = note.tags

        # Extract relevant tags
        identifier_tag = next((tag for tag in tags if re.match(r'^[a-zA-Z0-9()]+$', tag)), None)
        group_tag = next((tag for tag in tags if tag.startswith("group_")), None)
        word_index_tag = next((tag for tag in tags if tag.isdigit()), None)
        sentence_tag = 'sentence' if 'sentence' in tags else None

        if not identifier_tag or not group_tag:
            continue

        # Determine the audio filename based on tags
        if sentence_tag:
            audio_filename = f"{identifier_tag}_{group_tag}_sentence.mp3"
        elif word_index_tag:
            audio_filename = f"{identifier_tag}_{group_tag}_word_{word_index_tag}.mp3"
        else:
            continue

        audio_path = os.path.join(audio_folder_path, audio_filename)
        collection_media_path = os.path.join(mw.col.media.dir(), audio_filename)

        if os.path.exists(audio_path):
            # Copy the audio file to Anki's collection.media folder
            if not os.path.exists(collection_media_path):
                os.rename(audio_path, collection_media_path)

            # Update the note to use the copied audio file
            note.fields[0] = f"[sound:{audio_filename}]"
            note.flush()
            updated_notes += 1

    showInfo(f"成功将音频文件与 {updated_notes} 张卡片匹配并更新。")


def setup_menu():
    action = QAction("批量添加音频到卡片", mw)
    action.triggered.connect(match_audio_to_cards)
    mw.form.menuTools.addAction(action)

gui_hooks.main_window_did_init.append(setup_menu)
