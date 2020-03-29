# this is a small modification of the hyperlink/unlink function
# from the Power Format Pack: Copyright 2014-2017 Stefan van den Akker <neftas@protonmail.com>

# the code from the PFP (mostfly from hyperlink.py and utilities.py)
# is mostly from L47-L169 and the icons.
# the function setupEditorButtonsFilter is taken from "Auto Markdown"
# from https://ankiweb.net/shared/info/1030875226 which should be
# Copyright 2018 anonymous
#      probably reddit user /u/NavyTeal, see
#      https://www.reddit.com/r/Anki/comments/9t7acy/bringing_markdown_to_anki_21/


import json
import os

from anki.hooks import addHook
from anki.lang import _
from aqt import mw
from aqt.editor import Editor
from aqt.qt import *

from .helper_functions import escape_html_chars, is_valid_url
from .window import Hyperlink

addon_path = os.path.dirname(__file__)


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


def hlunlink(editor):
    editor.web.eval("setFormat('unlink')")


Editor.hlunlink = hlunlink


def toggle_hyperlink(editor):
    selected = editor.web.selectedText()
    h = Hyperlink(editor, editor.parentWindow, selected)
    if hasattr(h, "replacement"):
        editor.web.eval(
            "document.execCommand('insertHTML', false, %s);"
            % json.dumps(h.replacement))


Editor.toggle_hyperlink = toggle_hyperlink


def keystr(k):
    key = QKeySequence(k)
    return key.toString(QKeySequence.NativeText)


def setupEditorButtonsFilter(buttons, editor):
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


addHook("setupEditorButtons", setupEditorButtonsFilter)


def format_link_string_as_html_hyperlink(editor, data, selectedtext, QueryLinkText):
    url = selectedtext.strip()
    if QueryLinkText:
        h = Hyperlink(editor, editor.parentWindow, selectedtext, True)
        if hasattr(h, "replacement"):
            replacement = h.replacement
        else:
            return
    else:
        text = selectedtext.strip()
        replacement = Hyperlink.create_anchor(url, text)
    wspace = [' ', ]
    for i in wspace:
        if selectedtext.endswith(i):
            replacement = replacement + i
        if selectedtext.startswith(i):
            replacement = i + replacement
    editor.web.eval(
        "document.execCommand('insertHTML', false, %s);"
        % json.dumps(replacement))


Editor.format_link_string_as_html_hyperlink = format_link_string_as_html_hyperlink


def add_to_context(view, menu):
    # cf. https://doc.qt.io/qt-5/qwebenginepage.html#contextMenuData
    data = view.page().contextMenuData()
    selectedtext = view.editor.web.selectedText()
    url = data.linkUrl()
    if not (url.toString() or data.linkText()):
        # not a html hyperlink
        if is_valid_url(selectedtext.strip()):
            if gc('contextmenu_show_make_clickable', False):
                a = menu.addAction(_("Hyperlink - make clickable"))
                # a.setShortcut(QKeySequence("Ctrl+Alt+ö"))  #doesn't work
                a.triggered.connect(lambda _, e=view.editor, u=data, s=selectedtext:
                                    format_link_string_as_html_hyperlink(e, u, s, False))
            if gc('contextmenu_show_set_link_text', False):
                a = menu.addAction(_("Hyperlink - set link text "))
                a.triggered.connect(lambda _, e=view.editor, u=data, s=selectedtext:
                                    format_link_string_as_html_hyperlink(e, u, s, True))
    if (data.linkUrl().toString() or data.linkText()) and gc('contextmenu_show_unlink', False):
        a = menu.addAction(_("Hyperlink - unlink "))
        a.triggered.connect(lambda _, e=view.editor: hlunlink(e))
    if url.isValid():
        a = menu.addAction(_("Copy URL"))
        a.triggered.connect(lambda _, v="", u=url: set_clip(v, u))


addHook("EditorWebView.contextMenuEvent", add_to_context)


# reviewer
def set_clip(v, u):
    QApplication.clipboard().setText(u.url())


def _reviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    context_data = view.page().contextMenuData()
    url = context_data.linkUrl()
    if url.isValid():
        a = menu.addAction(_("Copy URL"))
        a.triggered.connect(lambda _, v=view, u=url: set_clip(v, u))


if gc("show_in_reviewer_context_menu"):
    addHook('AnkiWebView.contextMenuEvent', _reviewerContextMenu)
