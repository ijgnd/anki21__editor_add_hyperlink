# Anki add-on to insert hyperlinks from the editor

# Copyright 2018- ijgnd
#           2020 Arthur Milchior

# based on the add-on for anki 2.0 which had this copyright notice: 

# Copyright 2014-2017 Stefan van den Akker <neftas@protonmail.com>        

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import json
import os

from anki.hooks import addHook
from aqt import mw
from aqt.qt import QApplication, QKeySequence
from aqt.utils import openLink

from .config import gc
from .helper_functions import (
    combine_to_hyperlink,
    is_valid_url,
)
from .window import Hyperlink

addon_path = os.path.dirname(__file__)


def hlunlink(editor):
    editor.web.eval("setFormat('unlink')")


def toggle_hyperlink(editor):
    selected = editor.web.selectedText()
    h = Hyperlink(editor, editor.parentWindow, selected)
    if h.exec():
        # for details see issue #7,
        # https://github.com/ijgnd/anki21__editor_add_hyperlink/issues/7
        # relying on web.selectedText() means that I lose html formatting
        # and in 2.1 insertHTML into a e.g. a bold section means that the
        # inserted part is no longer bold.
        # A proper solution would mean that I'd also have to handle text
        # that a user changed. But then I can no longer use document.execCommand('CreateLink'
        # So I only document.execCommand('CreateLink when the user didn't change the link text
        # in the dialog.
        if selected == h.text:
            js = """ document.execCommand("CreateLink", false, %s); """ % json.dumps(h.url)
        else:
            js = """ document.execCommand("insertHTML", false, %s); """ % json.dumps(h.replacement)
        editor.web.eval(js)


def keystr(k):
    key = QKeySequence(k)
    return key.toString(QKeySequence.NativeText)


def setup_editor_buttons(buttons, editor):
    b = editor.addButton(
        os.path.join(addon_path, "icons", "hyperlink.png"),
        "hyperlinkbutton",
        toggle_hyperlink,
        tip="Insert Hyperlink ({})".format(
            keystr(gc("shortcut_insert_link", ""))),
        keys=gc('shortcut_insert_link')
    )
    buttons.append(b)

    if gc('unlink_button_and_shortcut', True):
        c = editor.addButton(
            os.path.join(addon_path, "icons", "remove_hyperlink.png"),
            "remove_hyperlink_button",
            hlunlink,
            tip="remove hyperlink ({})".format(
                keystr(gc("shortcut_unlink", ""))),
            keys=gc('shortcut_unlink', "")
        )
        buttons.append(c)

    return buttons
addHook("setupEditorButtons", setup_editor_buttons)  # noqa


def format_link_string_as_html_hyperlink(editor, data, selectedtext, query_link_text):
    url = selectedtext.strip()
    if query_link_text:
        h = Hyperlink(editor, editor.parentWindow, selectedtext, True)
        if h.exec():
            replacement = h.replacement
        else:
            return
    else:
        text = selectedtext.strip()
        replacement = combine_to_hyperlink(url, text)
    wspace = [' ', ]
    for i in wspace:
        if selectedtext.endswith(i):
            replacement = replacement + i
        if selectedtext.startswith(i):
            replacement = i + replacement
    editor.web.eval(
        "document.execCommand('insertHTML', false, %s);"
        % json.dumps(replacement))


def add_to_context(view, menu):
    # cf. https://doc.qt.io/qt-5/qwebenginepage.html#contextMenuData
    data = view.page().contextMenuData()
    selectedtext = view.editor.web.selectedText()    # data.selectedText() also gives plain text
    url = data.linkUrl()
    if not (url.toString() or data.linkText()):
        # not a html hyperlink
        if is_valid_url(selectedtext.strip()):
            if gc('contextmenu_show_transform_selected_url_to_hyperlink', False):
                a = menu.addAction("Hyperlink - transform to hyperlink")
                # a.setShortcut(QKeySequence("Ctrl+Alt+ö"))  #doesn't work
                a.triggered.connect(lambda _, e=view.editor, u=data, s=selectedtext:
                                    format_link_string_as_html_hyperlink(e, u, s, False))
            if gc('contextmenu_show_set_link_text', False):
                a = menu.addAction("Hyperlink - set link text ")
                a.triggered.connect(lambda _, e=view.editor, u=data, s=selectedtext:
                                    format_link_string_as_html_hyperlink(e, u, s, True))
    if (data.linkUrl().toString() or data.linkText()) and gc('contextmenu_show_unlink'):
        a = menu.addAction("Hyperlink - unlink ")
        a.triggered.connect(lambda _, e=view.editor: hlunlink(e))
    if url.isValid() and gc("contextmenu_show_copy_url"):
        a = menu.addAction("Copy URL")
        a.triggered.connect(lambda _, v="", u=url: set_clip(v, u))
    if url.isValid() and gc("contextmenu_show_open_in_browser"):
        a = menu.addAction("Open URL")
        a.triggered.connect(lambda _, u=url: openLink(u))
addHook("EditorWebView.contextMenuEvent", add_to_context)  # noqa


# reviewer
def set_clip(v, u):
    QApplication.clipboard().setText(u.url())  # noqa


def reviewer_context_menu(view, menu):
    if mw.state != "review":
        return
    context_data = view.page().contextMenuData()
    url = context_data.linkUrl()
    if url.isValid():
        a = menu.addAction("Copy URL")
        a.triggered.connect(lambda _, v=view, u=url: set_clip(v, u))
if gc("show_in_reviewer_context_menu"):  # noqa
    addHook('AnkiWebView.contextMenuEvent', reviewer_context_menu)
