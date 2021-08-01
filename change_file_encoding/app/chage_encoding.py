import codecs
import os.path as path

from os import (
    listdir,
    makedirs,
)
from typing import List

BLOCKSIZE = 1048576 # or some other, desired size in bytes

def change_encoding(src_filename: str, src_file_encoding: str, dst_file_path: str) -> None:
    """Change a file with src_filename to UTF-8 encoding and store to a new file.

    Logic is from https://stackoverflow.com/questions/191359/how-to-convert-a-file-to-utf-8-in-python
    """
    with codecs.open(src_filename, "r", src_file_encoding) as sourceFile:
        target_filename = f"{dst_file_path}/{path.basename(src_filename)}"
        with codecs.open(target_filename, "w", "UTF-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)


def get_smi_files(src_folder_name: str) -> List[str]:
    """Get all `.smi` files in the current directory.
    """
    return [
        f'{src_folder_name}/{f}'
        for f in listdir(f'{src_folder_name}')
        if f.endswith('.smi')
    ]


if __name__ == '__main__':
    current_dir = path.dirname(path.realpath(__file__))

    src_file_encoding = 'EUC-KR'
    src_file_path = f'{current_dir}/../sources'
    dst_file_path = f'{current_dir}/../results'
    print(f"src_file_path: {src_file_path}")

    # create folder if not exists
    if not path.exists(dst_file_path):
        makedirs(dst_file_path)

    file_names = get_smi_files(src_file_path)

    print("Changing Encodings...")
    weired_files = []
    for file_name in file_names:
        print(f"Changing: {basename(file_name)}")
        try:
            change_encoding(file_name, src_file_encoding, dst_file_path)
        except UnicodeDecodeError:
            weired_files.append(file_name)

    if weired_files:
        print("Unchanged files:\n{}".format('\n'.join(path.basename(weired_files))))
