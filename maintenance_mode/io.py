import fsutil


def read_file(filepath, default_content=""):
    """
    Read file at the specified path.
    If file doesn't exist, it will be created with default-content.
    Returns the file content.
    """
    if not fsutil.exists(filepath):
        write_file(filepath, default_content)
    return fsutil.read_file(filepath) or default_content


def set_file_permissions(filepath):
    """
    Sets the file permissions by inheriting
    them from the directory that contains it.
    """
    dirpath, _ = fsutil.split_filepath(filepath)
    dirpath_permissions = fsutil.get_permissions(dirpath)
    fsutil.set_permissions(filepath, dirpath_permissions)


def write_file(filepath, content):
    """
    Write file at the specified path with content.
    If file exists, it will be overwritten.
    """
    fsutil.write_file(filepath, content, atomic=True)
    set_file_permissions(filepath)
