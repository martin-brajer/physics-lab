"""
IO
"""
# __all__ =


import os


def gather_files(extension, folder, key_edit=None, trim_extension=True):
    """ Gather all files of the given :attr:`extension` located
    in or under :attr:`folder`.

    :param str extension: File extension to look for
    :param str folder: Look in that folder and all its subfolders
    :param key_edit: If supplied, this function will be applied to the
        `filename` stem, defaults to None
    :type key_edit: function, optional
    :param trim_extension: Cut the extension from `filename` to be used as key,
        defaults to True
    :type trim_extension: bool, optional
    :return: Dictionary form {filename : path}
    :rtype: dict
    """
    if extension[0] == '.':
        del extension[0]

    found = {}
    for path, subfolders, files in os.walk(folder):
        for file_ in files:
            if file_.endswith('.' + extension):
                trim = len(extension) + (1 if trim_extension else 0)
                stem = file_[:-trim]
                if key_edit is not None:
                    stem = key_edit(stem)
                found[stem] = os.path.join(path, file_)
    return found
