# Made with help from GPT

import time
import tkinter as tk
from tkinter import filedialog
import os

from typing import Callable, List, Dict, Union
from io import TextIOWrapper

import numpy as np
from scipy import sparse

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


def parse_A_Dense(file: TextIOWrapper) -> List[List[float]]:
    A = []
    for line in file:
        stripped_line = line.strip()
        if stripped_line == "]":
            break
        # Parse the row of numbers and append to A
        A.append([float(x) for x in stripped_line.split()])
    return A


def parse_A(file: TextIOWrapper) -> sparse.csc_array:
    """
    Reads a matrix from a file in a dense format and converts it to a sparse CSC matrix.
    
    Parameters:
    -----------
    file : TextIOWrapper
        The file object to read the matrix from.
    
    Returns:
    --------
    sparse.csr_array
        The matrix in CSC (Compressed Sparse Column) format.
    """
    rows : list[int]    = []  # Stores the row indices of non-zero elements
    cols : list[int]    = []  # Stores the column indices of non-zero elements
    data : list[float]  = []  # Stores the non-zero values
    
    # Read the first non-empty line to determine the number of columns
    for line in file:
        stripped_line = line.strip()
        if stripped_line and stripped_line != "]":
            first_row_values = [float(x) for x in stripped_line.split()]
            num_cols = len(first_row_values)

            # Add the first row data to the matrix
            for col_index, value in enumerate(first_row_values):
                if value != 0.0:
                    rows.append(0)
                    cols.append(col_index)
                    data.append(value)

            break

    row_index = 1  # Track the row number in the matrix
    
    for line in file:
        stripped_line = line.strip()
        if stripped_line == "]":
            break
        
        # Convert the line into a list of floats
        row_values = [float(x) for x in stripped_line.split()]
        
        # Iterate over the row and store non-zero values
        for col_index, value in enumerate(row_values):
            if value != 0.0:  # Only consider non-zero elements
                rows.append(row_index)
                cols.append(col_index)
                data.append(value)
        
        row_index += 1
    
    # Create a CSC matrix from the collected data
    A_sparse_csc = sparse.csc_array((data, (rows, cols)), shape=(row_index, num_cols))

    print(A_sparse_csc)


    return A_sparse_csc

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
                b = parse_column_vector(file , A.get_shape()[0] )
            elif stripped_line.startswith("c=["):
                c = parse_column_vector(file , A.get_shape()[1])
            elif stripped_line.startswith("Eqin=["):
                Eqin = parse_column_vector(file , A.get_shape()[0])
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

    # Start measuring CPU time
    start_time = time.process_time()

    data = parse_file(selected_file)

    # Stop measuring CPU time
    end_time = time.process_time()

    # Calculate the total CPU time used
    cpu_time_used = end_time - start_time

    print(f"CPU time used: {cpu_time_used} seconds")

    print(data)

    


if __name__ == "__main__":

    main()

