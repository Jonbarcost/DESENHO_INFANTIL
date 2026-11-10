"""Portable FFmpeg filter paths: relative POSIX paths avoid Windows drive colons."""
import os
from pathlib import Path


def filter_path(path,root):
    relative=Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    return relative.replace('\\','\\\\').replace("'",r"'\''").replace(':',r'\:')


def bundled_font(root):
    return filter_path(Path(root)/'producao/fonts/DejaVuSans-Bold.ttf',root)
