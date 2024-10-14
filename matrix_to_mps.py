# Made with help from GPT

import time
import tkinter as tk
from tkinter import filedialog
import os

from typing import Callable, List, Dict, Union
from io import TextIOWrapper

import numpy as np

def select_file(window_title: str = "Select a file") -> str:
    """
    Opens a file selection dialog to allow the user to choose a file. 
    The dialog starts in the current working directory and filters file types to `.txt` files by default.

    Args:
        window_title (str): The title of the file selection dialog window. Defaults to "Select a file".

    Returns:
        str: The full path of the selected file as a string. If the user cancels the selection, an empty string is returned.

    Notes:
        - The function hides the root `tkinter` window.
        - The dialog restricts the file selection to `.txt` files by default, but allows selecting any file type.
        - The initial directory is set to the current working directory.
    """ 
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
        filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]  # Restrict to .txt files by default
    )

    # Return the file path
    return file_path


def select_save_file_path(default_name: str = "untitled.mps", save_dir: str = os.getcwd()) -> str:
    """
    Opens a "Save As" dialog to allow the user to select a file path and filename for saving a file.
    The dialog will start in a specified directory and suggest a default filename and file type (.mps).

    Args:
        default_name (str): The default file name to suggest in the "Save As" dialog. Defaults to "untitled.mps".
        save_dir (str): The directory to open the dialog in. Defaults to the current working directory.

    Returns:
        str: The full path of the selected file, including the file name and extension. If the user cancels
             the operation, an empty string is returned.

    Notes:
        - The function hides the root `tkinter` window.
        - The dialog filters the file types, showing `.mps` files by default, but allows selecting any file type.
        - The `.mps` extension is added automatically if the user does not specify one.
    """

    # Create a root window (it won't be displayed)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open a save file dialog and get the selected file path
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        initialdir=save_dir,
        initialfile=default_name,
        defaultextension="mps",  # Add the default extension
        filetypes=[("MPS files", "*.mps"), ("All files", "*.*")]  # Restrict file types
    )

    # Return the selected file path
    return file_path


def parse_A(file: TextIOWrapper) -> List[List[float]]:
    # A = [[float(x) for x in first_stripped_line.split()[1:]]]
    A = []
    for line in file:
        stripped_line = line.strip()
        if stripped_line == "]":
            break
        # Parse the row of numbers and append to A
        A.append([float(x) for x in stripped_line.split()])
    return A

def parse_column_vector(file: TextIOWrapper, v_size : int ) -> np.ndarray : # np.typing.NDArray[float]:
    # Pre-allocate numpy array with the specified size
    v = np.zeros(v_size, dtype=float)
    
    # Fill in the first value from the stripped line
    # v[0] = float(first_stripped_line.split()[1])
    
    # Read exactly (b_size - 1) more lines
    for i in range(v_size):
        stripped_line = next(file).strip()  # Read the next line and strip it
        v[i] = float(stripped_line)        # Parse the number and insert it into the array

    return v

def parse_BS(file: TextIOWrapper) -> List[str]:
    # BS = [first_stripped_line.split(maxsplit=1)[1]]
    BS = []
    for line in file:
        stripped_line = line.strip()
        if stripped_line == "]":
            break
        BS.append(stripped_line)  # Append each BS line as is
    return BS

def parse_file(file_path: str) -> Dict[str, Union[List ,np.ndarray ]]:
    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line.startswith("A=["):
                A = parse_A(file)
            elif stripped_line.startswith("b=["):
                b = parse_column_vector(file , len(A))
            elif stripped_line.startswith("c=["):
                c = parse_column_vector(file , len(A[0]))
            elif stripped_line.startswith("Eqin=["):
                Eqin = parse_column_vector(file , len(A))
            elif stripped_line.startswith("MinMax="):
                MinMax = stripped_line.split()[1]
            elif stripped_line.startswith("BS=["):
                Bounds = parse_BS(file)
            else:
                continue
                
    return {
        "A": A,
        "b": b,
        "c": c,
        "Eqin": Eqin,
        "MinMax": [MinMax],
        "BS": Bounds
    }

def main() -> None:

    # selected_file = select_file()    
    selected_file = "output_matrix.txt"
    print(f"Selected file: {selected_file}")


    data = parse_file(selected_file)
    print(data)

    return
    
    # Start measuring CPU time
    start_time = time.process_time()

    parsed_data = parse_matrix_file(selected_file)

    # Stop measuring CPU time
    end_time = time.process_time()

    # Calculate the total CPU time used
    cpu_time_used = end_time - start_time

    print(f"CPU time used: {cpu_time_used} seconds")


if __name__ == "__main__":

    main()

