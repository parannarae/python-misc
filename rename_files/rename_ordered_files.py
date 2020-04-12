from os import (
    listdir,
    makedirs,
    rename,
)
import os.path as path
from shutil import copyfile


def get_cwd_files_without_py_script(path_name):
    """Given a file path path_name, get all files in path_name directory
    excluding py script.

    Args:
        path_name (str): a file direction to search

    Returns:
        list[str]: list containing all file names
    """
    return [f for f in listdir(path_name)
            if (path.isfile(f) and not f.endswith('.py'))]


def rename_ordered_files(src_file_path, dst_file_path, prefix_num=None):
    """Get all files in src_file_path and change file names (to an ordered 
    number) and save them to dst_file_path.

    Args:
        src_file_path (str): a source file path
        dst_file_path (str): a destination file path
        prefix_num (int): a prefix number to append at the beginning of all 
            the files

    Returns:
        None

    """
    file_list = get_cwd_files_without_py_script(src_file_path)
    num_of_files = len(file_list)

    # create folder if not exists
    if not path.exists(dst_file_path):
        makedirs(dst_file_path)
    
    # rename files in order (by number)
    for i in range(num_of_files):
        # zero fill up to the number of digits in num_of_files
        cur_file_num = str(i + 1).zfill(len(str(num_of_files)))
        
        # if prefix_num exists, append it to the beginning
        cur_new_name = path.join(
            dst_file_path, "{}{}.{}".format(
                prefix_num if prefix_num else '', 
                cur_file_num, 
                file_list[i].split('.')[-1]))
        print("copying {} to {}".format(file_list[i], cur_new_name))
        copyfile(file_list[i], cur_new_name)

if __name__ == '__main__':
    src_file_path = '.'
    rename_ordered_files(src_file_path, 'temp', 1)
