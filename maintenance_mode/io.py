# -*- coding: utf-8 -*-

import os


def read_file(file_path, default_content=''):
    """
    Read file at the specified path.
    If file doesn't exist, it will be created with default-content.
    Returns the file content.
    """
    if not os.path.exists(file_path):
        write_file(file_path, default_content)

    handler = open(file_path, 'r')
    content = handler.read()
    handler.close()
    return content or default_content


def write_file(file_path, content):
    """
    Write file at the specified path with content.
    If file exists, it will be overwritten.
    """
    handler = open(file_path, 'w+')
    handler.write(content)
    handler.close()
