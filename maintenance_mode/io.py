import os

import fsutil


def read_file(file_path, default_content=""):
    """
    Read file at the specified path.
    If file doesn't exist, it will be created with default-content.
    Returns the file content.
    """
    if not fsutil.exists(file_path):
        fsutil.write_file(file_path, default_content)
    return fsutil.read_file(file_path) or default_content


def write_file(file_path, content):
    """
    Write file at the specified path with content.
    If file exists, it will be overwritten.
    """
    fsutil.write_file(file_path, content)
