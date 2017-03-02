# -*- coding: utf-8 -*-


def read_file(file_path, default_content = ''):

    try:
        handler = open(file_path, 'r')
        content = handler.read()
        handler.close()
        return content or default_content

    except IOError:
        return default_content

def write_file(file_path, content):

    try:
        handler = open(file_path, 'w+')
        handler.write(content)
        handler.close()
        return True

    except IOError:
        return False

