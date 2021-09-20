import glob
import os
from typing import List

from .misc import remove_quotes


def get_files(source: str, max_count: int = 0) -> List[str]:
    """
    Get files from source with limit
    """
    source = remove_quotes(source)
    if os.path.isdir(source):
        source = os.path.join(source, '*')
    max_count = 0 if not isinstance(max_count, int) else max_count
    files = [os.path.abspath(file) for file in glob.glob(source)
             if os.path.isfile(file) and not os.path.isdir(file)]
    if max_count > 0:
        files = files[0:max_count]
    return files
