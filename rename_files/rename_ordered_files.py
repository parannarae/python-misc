import os.path as path

from os import (
    listdir,
    makedirs,
    rename,
)
from shutil import copyfile
from typing import List


def get_cwd_files_without_py_script(path_name: str) -> List[str]:
    """Given a file path path_name, get all files in path_name directory
    excluding py script.

    Args:
        path_name (str): a file direction to search

    Returns:
        list[str]: list containing all file names
    """
    return [path.join(path_name, f) for f in listdir(path_name)
            if (path.isfile(path.join(path_name, f)) and not f.endswith('.py'))]


def _is_time_to_log(
        current_iteration: int,
        number_of_files: int,
        percentile_to_log: float = 0.2) -> bool:

    return current_iteration % int(number_of_files * percentile_to_log) == 0


def rename_ordered_files(
        src_file_path: str,
        dst_file_path: str,
        filename_fmt: str) -> None:
    """Get all files in src_file_path and change file names and save them to
    dst_file_path.

    Args:
        src_file_path (str): a source file path
        dst_file_path (str): a destination file path
        filename_fmt (str): a format string to be used for a file renaming

    Returns:
        None

    """
    file_list = get_cwd_files_without_py_script(src_file_path)

    # sort the list by the filename
    file_list.sort()
    num_of_files = len(file_list)

    # create folder if not exists
    if not path.exists(dst_file_path):
        makedirs(dst_file_path)

    # rename files in order (by number)
    for i in range(num_of_files):
        # zero fill up to the number of digits in num_of_files
        cur_file_num = str(i + 1).zfill(len(str(num_of_files)))

        new_file_name = filename_fmt.format(cur_file_num)
        cur_new_name = path.join(
            dst_file_path, "{}.{}".format(
                new_file_name,
                file_list[i].split('.')[-1]))

        if _is_time_to_log(i, num_of_files):
            print("Renaming {}th file({})".format(cur_file_num, cur_new_name))
        copyfile(file_list[i], cur_new_name)

if __name__ == '__main__':
    src_file_path = './source-folder'
    dst_file_path = src_file_path + '/temp'
    filename_fmt = 'some-file-name-{}'
    rename_ordered_files(src_file_path, dst_file_path, filename_fmt)
