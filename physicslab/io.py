""" Filesystem manipulation.

"""
# __all__ =


import os
import re


def gather_files(extension, folder, key_edit=None, trim_extension=True):
    """ Gather all files of the given :attr:`extension` located
    in or under :attr:`folder`.

    :param str extension: File extension to look for
    :param str folder: Look in that folder and all its subfolders
    :param key_edit: If supplied, this function will be applied to the
        `filename` stem, defaults to None
    :type key_edit: callable, optional
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


def subfolder(folder, look_for):
    """ Look for a subfolder containing :attr:`look_for` in its name.

    :param str folder: Search there
    :param str look_for: Part of the folder name to look for. Can be RegEx.
    :raises OSError: If no subfolder found
    :raises OSError: If multiple subfolders found
    :return: Path to the found subfolder
    :rtype: str
    """
    subfolders = os.walk(folder).__next__()[1]  # [1] => folders only.
    matching = [subfolder for subfolder in subfolders
                if re.search(look_for, subfolder)]
    if not matching:
        raise OSError('"{}" not found in "{}".'.format(look_for, folder))
    if len(matching) > 1:
        raise OSError('Multiple "{}" found in "{}".'.format(look_for, folder))

    return os.path.join(folder, matching[0])  # len(matching) == 1
