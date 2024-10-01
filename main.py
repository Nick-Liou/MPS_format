
import tkinter as tk
from tkinter import filedialog

# Made using GPT
def select_file(window_title: str = "Select a file") -> str:
    # Create a root window (it won't be displayed)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Set the title of the file dialog window
    root.title(window_title)

    # Open a file dialog and store the selected file path
    file_path = filedialog.askopenfilename(title=window_title)

    # Return the file path
    return file_path


def main() -> None:

    # Example usage
    selected_file = select_file()
    print(f"Selected file: {selected_file}")
    pass


if __name__ == "__main__":

    main()

