import os

def get_all_file_paths(directory):
    """
    Get all file paths in the given directory and its subdirectories.
    """
    file_paths = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            file_paths.append(full_path)
            print(full_path)

    return file_paths

# Hardcoded path
folder_path = r"C:\\Project\\Semantic Kernel\\test\\Semantic"  # Add 'r' before string to handle backslashes

if os.path.isdir(folder_path):
    print("\nListing all files in folder:\n")
    all_files = get_all_file_paths(folder_path)
    print(f"\nTotal files found: {len(all_files)}")
else:
    print("The provided path is not a valid directory.")
