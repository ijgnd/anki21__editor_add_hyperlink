# this is a small modification of the hyperlink/unlink function
# from the Power Format Pack: Copyright 2014-2017 Stefan van den Akker <neftas@protonmail.com>

# the code from the PFP (mostfly from hyperlink.py and utilities.py)
# is mostly from L47-L169 and the icons.
# the function setupEditorButtonsFilter is taken from "Auto Markdown"
# from https://ankiweb.net/shared/info/1030875226 which was 
# released anonymously on 2018-11-01


##This is the original comment from the file hyperlink.py from PFP:
    # Copyright 2014-2017 Stefan van den Akker <neftas@protonmail.com>
    #
    # This file is part of Power Format Pack.
    #
    # Power Format Pack is free software: you can redistribute it
    # and/or modify it under the terms of the GNU General Public License as
    # published by the Free Software Foundation, either version 3 of the
    # License, or (at your option) any later version.
    #
    # Power Format Pack is distributed in the hope that it will be
    # useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
    # Public License for more details.
    #
    # You should have received a copy of the GNU General Public License along
    # with Power Format Pack. If not, see http://www.gnu.org/licenses/.


import json
import os
from anki import version
from aqt import mw
from anki.hooks import addHook, wrap

from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QShortcut, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QLineEdit
from PyQt5.QtGui import QKeySequence


addon_path = os.path.dirname(__file__)


def load_config(conf):
    global config
    config=conf

load_config(mw.addonManager.getConfig(__name__))
mw.addonManager.setConfigUpdatedAction(__name__,load_config) 





def escape_html_chars(s):
    """
    Escape HTML characters in a string. Return a safe string.
    >>> escape_html_chars(u"this&that")
    u'this&amp;that'
    >>> escape_html_chars(u"#lorem")
    u'#lorem'
    """
    if not s:
        return ""

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }

    result = "".join(html_escape_table.get(c, c) for c in s)
    return result


# size of the dialog windows
DIALOG_SIZE_X         = 350
DIALOG_SIZE_Y         = 200
MIN_COMBOBOX_WIDTH    = 140



class Hyperlink(object):
    def __init__(self, other, parent_window, selected_text):
        self.editor_instance    = other
        self.parent_window      = parent_window
        self.selected_text      = selected_text
        self.hyperlink_dialog()

    def hyperlink_dialog(self):
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Create a hyperlink")
        dialog.resize(DIALOG_SIZE_X, DIALOG_SIZE_Y)

        ok_button_anchor = QPushButton("&OK", dialog)
        ok_button_anchor.setEnabled(False)
        ok_button_anchor.clicked.connect(lambda: self.insert_anchor(
            url_edit.text(), urltext_edit.text()))
        ok_button_anchor.clicked.connect(dialog.hide)

        ok_button_anchor.setAutoDefault(True)

        cancel_button_anchor = QPushButton("&Cancel", dialog)
        cancel_button_anchor.clicked.connect(dialog.hide)
        cancel_button_anchor.setAutoDefault(True)

        url_label = QLabel("Link to:")
        url_edit = QLineEdit()
        url_edit.setPlaceholderText("URL")
        url_edit.textChanged.connect(lambda: self.enable_ok_button(
            ok_button_anchor, url_edit.text(), urltext_edit.text()))

        urltext_label = QLabel("Text to display:")
        urltext_edit = QLineEdit()
        urltext_edit.setPlaceholderText("Text")
        urltext_edit.textChanged.connect(lambda: self.enable_ok_button(
            ok_button_anchor, url_edit.text(), urltext_edit.text()))

        # if user already selected text, put it in urltext_edit
        if self.selected_text:
            urltext_edit.setText(self.selected_text)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(cancel_button_anchor)
        button_box.addWidget(ok_button_anchor)

        dialog_vbox = QVBoxLayout()
        dialog_vbox.addWidget(url_label)
        dialog_vbox.addWidget(url_edit)
        dialog_vbox.addWidget(urltext_label)
        dialog_vbox.addWidget(urltext_edit)
        dialog_vbox.addLayout(button_box)

        dialog.setLayout(dialog_vbox)

        # give url_edit focus
        url_edit.setFocus()

        dialog.exec_()

    @staticmethod
    def enable_ok_button(button, url, text):
        if url and text:
            button.setEnabled(True)
        else:
            button.setEnabled(False)

    @staticmethod
    def create_anchor(url, text):
        """
        Create a hyperlink string, where `url` is the hyperlink reference
        and `text` the content of the tag.
        """
        text = escape_html_chars(text)

        return "<a href=\"{0}\">{1}</a>".format(url, text)

    def insert_anchor(self, url, text):
        """
        Inserts a HTML anchor `<a>` into the text field.
        """
        replacement = self.create_anchor(url, text)
        self.editor_instance.web.eval(
                "document.execCommand('insertHTML', false, %s);"
                % json.dumps(replacement))
 

def unlink(editor):
    editor.web.eval("setFormat('unlink')")


def toggle_hyperlink(editor):
    selected = editor.web.selectedText()
    Hyperlink(editor, editor.parentWindow, selected)


def setupEditorButtonsFilter(buttons, editor):
    global editor_instance
    editor_instance = editor

    key = QKeySequence(config['shortcut_insert_link'])
    keyStr = key.toString(QKeySequence.NativeText)

    if config['link_function']:
        b = editor.addButton(
            os.path.join(addon_path, "icons", "hyperlink.png"), 
            "hyperlinkbutton", 
            toggle_hyperlink, 
            tip="Insert Hyperlink ({})".format(keyStr),
            keys=config['shortcut_insert_link']) 
        buttons.append(b)

    key2 = QKeySequence(config['shortcut_unlink'])
    key2Str = key2.toString(QKeySequence.NativeText)

    if config['unlink_function']:
        c = editor.addButton(
            os.path.join(addon_path, "icons", "remove_hyperlink.png"), 
            "remove_hyperlink_button", 
            unlink, 
            keys=config['shortcut_unlink'], 
            tip="remove hyperlink ({})".format(key2Str))
        buttons.append(c)

    return buttons

addHook("setupEditorButtons", setupEditorButtonsFilter)