# -*- coding: utf-8 -*-


def read_file(file_path):

    try:
        handler = open(file_path, 'r')
        content = handler.read()
        handler.close()
        return content or ''

    except IOError:
        return None

def write_file(file_path, content):

    try:
        handler = open(file_path, 'w+')
        handler.write(content)
        handler.close()
        return True

    except IOError:
        return False

