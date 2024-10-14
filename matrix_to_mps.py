

import time
import tkinter as tk
from tkinter import filedialog
import os

from typing import Callable, List, Dict, Union
from io import TextIOWrapper

import numpy as np

# Made with help from GPT
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
        filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]  # Restrict to .mps files by default
    )

    # Return the file path
    return file_path



def parse_matrix_file(file_path: str) -> dict:
    mode = None  # Default mode is None

    # Define prefix-to-mode mapping
    prefix_to_mode = {
        "A=[": "Read_A",
        "b=[": "Read_b",
        "c=[": "Read_c",
        "Eqin=[": "Read_Eqin",
        "MinMax=": "Read_MinMax",
        "BS=[": "Read_BS",
    }
    
    line_prefixs =()
    with open(file_path, 'r') as file:        
        for line in file:
            # Remove leading and trailing whitespaces
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                continue

            # Try to find the matching mode by checking prefixes
            for prefix, new_mode in prefix_to_mode.items():
                if stripped_line.startswith(prefix):
                    mode = new_mode
                    break

            # Process the data based on current mode
            if mode == "Read_A":
                # Process "A" section
                pass
            elif mode == "Read_b":
                # Process "b" section
                pass
            elif mode == "Read_c":
                # Process "c" section
                pass
            # Continue for other modes...

            # # Ignore empty lines
            # if line.strip() == '':
            #     continue

            # if line.startswith("A=["):
            #     mode = "Read_A"
            # elif line.startswith("b=["):
            #     mode = "Read_b"
            # elif line.startswith("c=["):
            #     mode = "Read_c"
            # elif line.startswith("Eqin=["):
            #     mode = "Read_Eqin"
            # elif line.startswith("MinMax="):
            #     mode = "Read_MinMax"
            # elif line.startswith("BS=["):
            #     mode = "Read_BS"
            # else:
            #     if mode == "Read_A":
            #         pass
            #     elif mode == "Read_b":
            #         pass
            #     elif mode == "Read_c":
            #         pass
            #     # ...
            #     else:
            #         continue

    return {}

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

# def parse_b_old(file: TextIOWrapper, first_stripped_line : str , b_size : int) -> np.ndarray : # np.typing.NDArray[float]:
#     # Pre-allocate numpy array with the specified size
#     b = np.zeros(b_size, dtype=float)

#     # Fill in the first value from the stripped line
#     b[0] = float(first_stripped_line.split()[1])
    
#     # Use an index to keep track of where to insert the next value
#     index = 1
    
#     for line in file:
#         stripped_line = line.strip()
#         if stripped_line == "]":
#             break
#         # Parse the number and insert it into the pre-allocated array
#         b[index] = float(stripped_line)
#         index += 1
#     return b

# def parse_b(file: TextIOWrapper, first_stripped_line : str , b_size : int) -> np.ndarray : # np.typing.NDArray[float]:
#     # Pre-allocate numpy array with the specified size
#     b = np.zeros(b_size, dtype=float)
    
#     # Fill in the first value from the stripped line
#     b[0] = float(first_stripped_line.split()[1])
    
#     # Read exactly (b_size - 1) more lines
#     for i in range(1, b_size):
#         stripped_line = next(file).strip()  # Read the next line and strip it
#         b[i] = float(stripped_line)        # Parse the number and insert it into the array

#     return b

# def parse_c(file: TextIOWrapper, first_stripped_line : str , c_size : int ) -> np.ndarray:
#     # Pre-allocate numpy array with the specified size
#     c = np.zeros(c_size, dtype=float)

#     # Fill in the first value from the stripped line
#     c[0] = float(first_stripped_line.split()[1])
    
#     # Use an index to keep track of where to insert the next value
#     index = 1
    
#     for line in file:
#         stripped_line = line.strip()
#         if stripped_line == "]":
#             break
#         # Parse the number and insert it into the pre-allocated array
#         c[index] = float(stripped_line)
#         index += 1
#     return c

# def parse_Eqin(file: TextIOWrapper, first_stripped_line : str) -> List[int]:
#     Eqin = []
#     for line in file:
#         stripped_line = line.strip()
#         if stripped_line == "]":
#             break
#         Eqin.append(int(stripped_line))  # Parse the integer and append to Eqin
#     return Eqin

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

# def test_parse(file_path: str) -> None : 
#     with open(file_path, 'r') as file:
#         for line in file:
#             print("line is: " , line)
#             if line.strip().startswith("A=["):
#                 for A_line in file : 
#                     print("lines in A: " , A_line)

#                     if A_line.strip() == "]":
#                         print("A is overr!!!")
#                         break

#             else:
#                 break
                    
                

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

