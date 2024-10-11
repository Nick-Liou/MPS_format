
import tkinter as tk
from tkinter import filedialog
import os

# Made with GPT
def select_file(window_title: str = "Select a file") -> str:
    # Create a root window (it won't be displayed)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Set the title of the file dialog window
    root.title(window_title)

    # Get the current working directory
    current_dir = os.getcwd()

    # Open a file dialog and store the selected file path
    file_path = filedialog.askopenfilename(
        title=window_title,
        initialdir=current_dir,  # Set the dialog to open in the current directory
        filetypes=[("MPS files", "*.mps"), ("All files", "*.*")]  # Restrict to .mps files by default
    )

    # Return the file path
    return file_path

def parse_mps_file(file_path: str) -> dict:
    """
    Parse the content of an .mps file and return its sections as a dictionary.

    Parameters:
    file_path (str): The path to the .mps file.

    Returns:
    dict: A dictionary containing the parsed sections of the .mps file.
    """
    mps_data = {
        "NAME": "",
        "ROWS": [],
        "COLUMNS": [],
        "RHS": [],
        "BOUNDS": [],
        "RANGES": []
    }

    current_section = None

    with open(file_path, 'r') as file:
        for line in file:
            # Ignore comments and empty lines
            if line.startswith('*') or line.strip() == '':
                continue

            # Determine which section we are in
            if line.startswith("NAME"):
                current_section = "NAME"
                mps_data["NAME"] = line.split()[1]  # Extract problem name
            elif line.startswith("ROWS"):
                current_section = "ROWS"
            elif line.startswith("COLUMNS"):
                current_section = "COLUMNS"
            elif line.startswith("RHS"):
                current_section = "RHS"
            elif line.startswith("BOUNDS"):
                current_section = "BOUNDS"
            elif line.startswith("RANGES"):
                current_section = "RANGES"
            elif line.startswith("ENDATA"):
                break  # End of file marker
            else:
                # Add data to the appropriate section
                if current_section == "ROWS":
                    mps_data["ROWS"].append(line.strip())
                elif current_section == "COLUMNS":
                    mps_data["COLUMNS"].append(line.strip())
                elif current_section == "RHS":
                    mps_data["RHS"].append(line.strip())
                elif current_section == "BOUNDS":
                    mps_data["BOUNDS"].append(line.strip())
                elif current_section == "RANGES":
                    mps_data["RANGES"].append(line.strip())

    return mps_data


def main() -> None:

    # Example usage
    selected_file = select_file()
    print(f"Selected file: {selected_file}")

    parsed_data = parse_mps_file(selected_file)
    print(parsed_data)
    pass


if __name__ == "__main__":

    main()

