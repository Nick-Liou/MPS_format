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


# def parse_A_Dense(file: TextIOWrapper) -> List[List[float]]:
#     A = []
#     for line in file:
#         stripped_line = line.strip()
#         if stripped_line == "]":
#             break
#         # Parse the row of numbers and append to A
#         A.append([float(x) for x in stripped_line.split()])
#     return A


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

    return A_sparse_csc

def parse_column_vector(file: TextIOWrapper, v_size : int ) -> np.ndarray :
    # Pre-allocate numpy array with the specified size
    v = np.zeros(v_size, dtype=float)
        
    # Read exactly v_size lines
    for i in range(v_size):
        stripped_line = next(file).strip()  # Read the next line and strip it
        v[i] = float(stripped_line)        # Parse the number and insert it into the array

    return v

def parse_BS(file: TextIOWrapper) -> List[str]:
    BS = []
    for line in file:
        stripped_line = line.strip()
        if stripped_line == "]":
            break
        BS.append(stripped_line)  # Append each BS line as is
    return BS

def parse_file(file_path: str) -> Dict[str, Union[List[float],np.ndarray , int , sparse.csc_array  ]]:
    # MinMax = -1 
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
                MinMax = int(stripped_line.split()[1])
            elif stripped_line.startswith("BS=["):
                Bounds = parse_BS(file)
            else:
                continue
                
    return {
        "MinMax": MinMax,
        "A": A,
        "b": b,
        "c": c,
        "Eqin": Eqin,
        "Bounds": Bounds
    }


def save_mps_file(file_path: str , MinMax:int , A : sparse.csc_array , b: np.ndarray , c: np.ndarray, Eqin: np.ndarray , Bounds:list[str] ) -> None:
    
    OBJ_name  = "OBJ"
    with open(file_path, "w") as file:  # Open a file in write mode
        # NAME
        if MinMax == 1 :
            file.write("NAME  LP_PROBLEM_NAME   (MAX)\n")  # Write the problem name    
        else:
            file.write("NAME  LP_PROBLEM_NAME\n")  # Write the problem name

        # ROWS
        file.write("ROWS\n")
        convert_Eqin = {-1:"L" , 0:"E" , 1:"G"}
        for i , sign in enumerate(Eqin) :             
            file.write(f" {convert_Eqin[sign]}  ROW{i}\n")  
        file.write(f" N  {OBJ_name}\n")
        
        # COLUMNS
        file.write("COLUMNS\n")
        # Iterate over each column of the sparse matrix A
        for col_number in range(A.shape[1]):  # Iterate over columns
            # Write pairs of ROW and value for the current column
            # The loop increments by 2, handling two entries per line where possible
            for i in range(A.indptr[col_number] ,A.indptr[col_number+1]  - ((A.indptr[col_number+1] - A.indptr[col_number]) % 2) ,2):
                file.write(f" COL{col_number}  ROW{A.indices[i]}  {A.data[i]}  ROW{A.indices[i+1]}  {A.data[i+1]}\n")

            # Check if there is an unpaired last entry in this column
            if (A.indptr[col_number+1] - A.indptr[col_number]) % 2 :
                # If there's an odd number of entries, write the last entry separately
                if c[col_number] != 0:                    
                    # If the objective function coefficient for this column is non-zero, write it in the same line as the last entry
                    file.write(f" COL{col_number}  ROW{A.indices[A.indptr[col_number+1]-1]}  {A.data[A.indptr[col_number+1]-1]}  {OBJ_name}  {c[col_number]}\n")
                else:
                    # Write the last unpaired entry without the objective function coefficient
                    file.write(f" COL{col_number}  ROW{A.indices[A.indptr[col_number+1]-1]}  {A.data[A.indptr[col_number+1]-1]}\n")
            elif c[col_number] != 0:
                # If the number of entries is even and the objective function coefficient is non-zero, write it
                file.write(f" COL{col_number}  {OBJ_name}  {c[col_number]}\n")
        
        # RHS
        file.write("RHS\n")
        for i , value in enumerate(b) :
            if value != 0 :
                file.write(f" RHS1  ROW{i}  {value}\n")  

        # BOUNDS
        if Bounds:
            file.write("BOUNDS\n")
            for value in Bounds: 
                a = value.split()
                extra = a[2] if a[2] != "None" else ""                
                file.write(f"{a[0]} BND1  COL{a[1]}  {extra}\n")  
        
        file.write("ENDATA")
        


     
def main() -> None:

    # selected_file = select_file()    
    selected_file = "output_matrix.txt"
    print(f"Selected file: {selected_file}")

    # Start measuring CPU time
    start_time = time.process_time()

    parsed_data = parse_file(selected_file)

    # Stop measuring CPU time
    end_time = time.process_time()

    # Calculate the total CPU time used
    cpu_time_used = end_time - start_time

    print(f"CPU time used: {cpu_time_used} seconds")

    print(parsed_data)


    save_file = select_save_file_path()    
    print(f"Data is being saved to: {save_file}")
    save_mps_file(save_file, **parsed_data )
    print("File saved successfully")


    


if __name__ == "__main__":
    
    main()

