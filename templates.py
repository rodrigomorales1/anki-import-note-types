from . import gui, utils
from aqt import mw as window
import aqt
from os import path
import os

# key names used by Anki
_anki_css = "css"
_anki_templates = "tmpls"
_anki_name = "name"
_anki_front = "qfmt"
_anki_back = "afmt"

# config
_delimiter = None
_css_name = None
_tmpl_ext = None


def _reload_config():
    utils.reload_config()
    global _delimiter, _css_name, _tmpl_ext
    _delimiter = utils.cfg("delimiter")
    _css_name = utils.cfg("cssName")
    _tmpl_ext = utils.cfg("tmplExt")


def import_tmpls():
    root = gui.get_dir()
    _reload_config()

    notetypes = [item for item in os.listdir(root) if os.path.isdir(path.join(root, item))]

    count_notetype = 0
    count_template = 0
    for name in notetypes:
        nt = window.col.models.byName(name)
        if not nt: continue

        count = 0
        file = path.join(root, name, _css_name)
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                nt[_anki_css] = f.read()
        for tmpl in nt.get(_anki_templates, []):
            if _anki_name not in tmpl: continue
            file = path.join(root, name, tmpl[_anki_name] + _tmpl_ext)
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    tmpl[_anki_front], _, tmpl[_anki_back] = f.read().partition(_delimiter)
                count += 1
        try:
            window.col.models.save(nt)
        except Exception:
            gui.show_error("note type \"{}\" contains errors!!".format(name))
            continue
        count_notetype += 1
        count_template += count
    aqt.utils.tooltip("imported (Template: {} from NoteType:{})".format(count_template, count_notetype), 5000)


def export_tmpls():
    root = gui.get_dir()
    _reload_config()

    count_notetype = 0
    count_template = 0
    for nt in window.col.models.all():
        try:
            notetype_name = nt.get(_anki_name)
        except KeyError:
            gui.show_error("The notetype has no name!!")
            continue
        notetype_path = path.join(root, notetype_name)
        os.makedirs(notetype_path, exist_ok=True)
        if _anki_css in nt:
            with open(path.join(notetype_path, _css_name), "w", encoding="utf-8") as f:
                f.write(nt[_anki_css])
        for tmpl in nt.get(_anki_templates, []):
            try:
                tmpl_name = tmpl.get(_anki_name)
            except KeyError:
                gui.show_error("A template in notetype \"{}\" has no name!!".format(notetype_name))
                continue
            with open(path.join(notetype_path, tmpl_name + _tmpl_ext), "w", encoding="utf-8") as f:
                if _anki_front in tmpl and _anki_back in tmpl:
                    f.write(tmpl[_anki_front] + _delimiter + tmpl[_anki_back])
            count_template += 1
        count_notetype += 1
    aqt.utils.tooltip("exported (Template: {} from NoteType:{})".format(count_template, count_notetype), 5000)
