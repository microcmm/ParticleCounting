import os

MAX_GRID_SIZE = 5  # 5x5 square grid
NUM_WIDE = 19

IN_DATA_DIR = "R:\ARRAY01-A5881\Alison\Antaria\S2a"
files = os.listdir(IN_DATA_DIR)
print(files)
print(len(files))


def group_files():
    for file in files:
        file_path = os.path.join(IN_DATA_DIR, file)
        if os.path.isdir(file_path):
            continue

        file_name, _, file_type = file.partition('.')
        file_num = int(file_name.split('_')[-1])

        # if file_num > 189:
        #   continue

        col = file_num % NUM_WIDE

        folders_per_row = int(19 // 5)

        row_group = int(file_num // 95)

        folder_num = int(col // 5) + row_group * 5

        # print(f"{file_name}\t{col}\t{folder_num}\t{row_group}")

        folder_name, folder_path = create_directory(folder_num)

        #print(f"{file_name}\t{folder_path}")

        print(file)

        move_file_to_dir(file, file_path, folder_path)


def create_directory(dir_id):
    folder_name = f"group_{dir_id}"
    folder_path = os.path.join(IN_DATA_DIR, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_name, folder_path


def create_directories(num_folders):
    for i in range(num_folders):
        folder_name = f"group_{i:02}"
        folder_path = os.path.join(IN_DATA_DIR, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def move_file_to_dir(file_name: str, file_path: str, folder_path: str) -> None:
    """Moves the files to the right directory."""
    new_path = os.path.join(folder_path, file_name)
    if os.path.exists(new_path):
        raise SystemExit(f"File exists - {new_path}")

    os.rename(file_path, new_path)


if __name__ == "__main__":
    group_files()
