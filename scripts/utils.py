import os
from stat import S_IWRITE
from typing import Callable


def on_rm_error(func: Callable[[str], None], path: str):
    os.chmod(path, S_IWRITE)
    func(path)
