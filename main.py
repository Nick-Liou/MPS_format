# Made with help from GPT

import tkinter as tk
from tkinter import filedialog
import os
from typing import Any

import numpy as np
from scipy import sparse

import time

def select_file(window_title: str = "Select a file") -> str:
    """
    Opens a file selection dialog to allow the user to choose a file. 
    The dialog starts in the current working directory and filters file types to `.mps` files by default.

    Args:
        window_title (str): The title of the file selection dialog window. Defaults to "Select a file".

    Returns:
        str: The full path of the selected file as a string. If the user cancels the selection, an empty string is returned.

    Notes:
        - The function hides the root `tkinter` window.
        - The dialog restricts the file selection to `.mps` files by default, but allows selecting any file type.
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
        filetypes=[("MPS files", "*.mps"), ("All files", "*.*")]  # Restrict to .mps files by default
    )

    # Return the file path
    return file_path


def select_save_file_path(default_name: str = "untitled.txt", save_dir: str = os.getcwd()) -> str:
    """
    Opens a "Save As" dialog to allow the user to select a file path and filename for saving a file.
    The dialog will start in a specified directory and suggest a default filename and file type (.txt).

    Args:
        default_name (str): The default file name to suggest in the "Save As" dialog. Defaults to "untitled.txt".
        save_dir (str): The directory to open the dialog in. Defaults to the current working directory.

    Returns:
        str: The full path of the selected file, including the file name and extension. If the user cancels
             the operation, an empty string is returned.

    Notes:
        - The function hides the root `tkinter` window.
        - The dialog filters the file types, showing `.txt` files by default, but allows selecting any file type.
        - The `.txt` extension is added automatically if the user does not specify one.
    """

    # Create a root window (it won't be displayed)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open a save file dialog and get the selected file path
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        initialdir=save_dir,
        initialfile=default_name,
        defaultextension="txt",  # Add the default extension
        filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]  # Restrict file types
    )

    # Return the selected file path
    return file_path



def parse_mps_file(input_file_path: str) -> dict:
    """
    Parses the content of an .mps file and returns its components in a structured format. 
    The function extracts information related to constraints, objective function, bounds, and matrix data, 
    and organizes them into appropriate sparse matrix representations.

    Parameters:
    input_file_path : str
        The path to the .mps file to be parsed.

    Returns:
    dict: A dictionary containing the parsed data from the .mps file with the following keys:    
        - 'MinMax' (int): Indicates if the problem is a minimization (-1) or maximization (1).
        - 'A' (scipy.sparse.csr_matrix): The constraint matrix `A` stored in CSR (Compressed Sparse Row) format.
        - 'b' (np.ndarray): The right-hand side vector `b` for the constraints.
        - 'c' (list[float]): The coefficient vector `c` for the objective function.
        - 'Eqin' (list[int]): A list indicating the equality type of each constraint (-1 for <=, 0 for =, 1 for >=).
        - 'Bounds' (list[str]): A list of bounds for variables extracted from the BOUNDS section of the file.

    Notes:
    - The function uses the CSC (Compressed Sparse Column) format to build the matrix `A` before converting it to CSR format for easier row access.
    - The MPS file format is a fixed-width format, and this parser assumes well-formed MPS files.
    - Sections such as 'ROWS', 'COLUMNS', 'RHS', and 'BOUNDS' are processed accordingly.
    - `MinMax` is inferred based on the problem name (if indicated in the first line).
    
    Raises:
    -------
    KeyError:
        If a key error occurs when referencing unknown rows or columns in the MPS file.
    """

    
    # Initialize variables to store matrix components and other data
    # Compressed Sparse Column (CSC)        
    A_values: list[float] = []  # Stores non-zero values in the matrix A
    A_rows: list[int] = []      # Stores row indices of non-zero values in A
    A_cols: list[int] = []      # Stores cumulative number of non-zeros in each column
    A_cols_names: dict[str, int] = {}  # Maps column names to their respective indices
    last_column_name: str = ""   # Tracks the last processed column name
    nnz: int = 0                 # Counter for non-zero elements in matrix A
    current_row: int
    current_col: int = -1        # Tracks the current column index in A
    zeros_in_c_in_a_row: int = 0  # Tracks consecutive zeros in the objective function vector c


    # Initialize vectors and other data structures
    b: np.ndarray
    c: list[float] = []          # Objective function coefficients
    Eqin: list[int] = []         # Stores equality type for each constraint (<=, =, >=)
    MinMax: int = -1             # Default is minimization (-1), can be updated for maximization
    Bounds: list[str] = []       # Stores variable bounds extracted from the BOUNDS section

    # Helper dictionary to convert 'L', 'E', 'G' in ROWS section to numerical values
    convert_dict = {"L": -1, "E": 0, "G": 1}
    
    # Problem metadata
    problem_name: str = ""
    objective_fun: str = ""      # Name of the objective function
    num_of_restrains: int = 0    # Number of constraints (rows)
    Restrains_names: dict[str, int] = {}  # Maps row names to row indices

    # Variable to keep track of the current section in the .mps file
    current_section = None


    # Open the input file and start processing line by line
    with open(input_file_path, 'r') as file:
        for line in file:
            # Ignore comment lines (starting with '*') and empty lines
            if line.startswith('*') or line.strip() == '':
                continue

            # Check if the line indicates a new section in the .mps file
            if line.startswith(("NAME", "ROWS", "COLUMNS", "RHS", "BOUNDS", "RANGES", "ENDATA")):
                if line.startswith("NAME"):
                    # NAME section: Get the problem name and infer if it's a maximization problem
                    current_section = "NAME"
                    problem_name = line.split()[1]  # Extract the problem name
                    if len(line.split()) == 3:
                        MinMax = 1  # If there's an indicator for maximization
                elif line.startswith("ROWS"):
                    current_section = "ROWS"  # Transition to ROWS section
                elif line.startswith("COLUMNS"):
                    current_section = "COLUMNS"  # Transition to COLUMNS section
                elif line.startswith("RHS"):
                    b = np.zeros(num_of_restrains)  # Initialize the RHS vector b
                    current_section = "RHS"  # Transition to RHS section
                elif line.startswith("BOUNDS"):
                    current_section = "BOUNDS"  # Transition to BOUNDS section
                elif line.startswith("RANGES"):
                    current_section = "RANGES"  # RANGES section (not handled in detail here)
                elif line.startswith("ENDATA"):
                    break  # End of file marker, stop processing
            else:
                # Process data based on the current section
                if current_section == "ROWS":
                    # ROWS section: Determine the equality type and set up constraint row mapping
                    a = line.split()
                    try:
                        # Add the equality type (L/E/G) and map row names to indices
                        Eqin.append( convert_dict[a[0]] ) 
                        Restrains_names[a[1]] = num_of_restrains
                        num_of_restrains += 1
                    except KeyError as e :
                        #  EAFP (Easier to Ask for Forgiveness than Permission)
                        if str(e) == "'N'": # 'N' indicates the objective function row
                            objective_fun = a[1]
                        else:
                            raise   # Re-raise any unexpected KeyErrors
                elif current_section == "COLUMNS":
                    # COLUMNS section: Parse the matrix A and objective function coefficients
                    
                    a = line.strip().split() 
                    #  Current column is current_col
                    #  a[0] is the column name (variable name ie X1) 
                    #  Current row is current_row
                    #  a[1] is the row name (restrictions)
                    #  a[2] is the value (coefficient of X1)
                    #  a[3] is the row name (restrictions)   (if they exist)
                    #  a[4] is the value (coefficient of X1) (if they exist)
                    if a[0] != last_column_name :
                         # New column detected, update column index and track its start position
                        last_column_name = a[0]
                        current_col += 1 
                        A_cols_names[a[0]] = current_col
                        A_cols.append(nnz)
                        zeros_in_c_in_a_row += 1

                    
                    # Add matrix elements or update the objective function c
                    try:
                        current_row = Restrains_names[a[1]]
                        A_values.append(float(a[2])) # Add value to A
                        A_rows.append(current_row) # Add row index for the value
                        nnz += 1  # Increment non-zero counter
                    except KeyError as e:
                        if str(e) == "'" + objective_fun + "'" :
                            # Update the objective function coefficient for the current column
                            c.extend([0] * (zeros_in_c_in_a_row-1)) # Fill in missing zeros
                            # c[current_col] = float(a[2])
                            zeros_in_c_in_a_row = 0 
                            c.append(float(a[2])) # Add the coefficient value
                        else:
                            raise  # Re-raise the exception if it's a different key

                    # Handle possible second value in the same line (optional column entry)
                    try:
                        current_row = Restrains_names[a[3]]
                        A_values.append(float(a[4])) # Add another value to A
                        A_rows.append(current_row) # Add row index for the value
                        nnz += 1  # Increment non-zero counter
                    except KeyError as e:
                        if str(e) == "'" + objective_fun + "'":
                            # c[current_col] = float(a[4])
                            c.extend([0] * (zeros_in_c_in_a_row-1))
                            zeros_in_c_in_a_row = 0 
                            c.append(float(a[4]))  # Add second coefficient value
                        else:
                            raise  # Re-raise the exception if it's a different key
                    except IndexError:
                        pass # Handle cases where second entry is missing
                elif current_section == "RHS":
                    # RHS section: Assign values to the right-hand side vector b
                    a = line.strip().split() 
                    
                    b[Restrains_names[a[1]]] = float(a[2])  # Assign value to the appropriate row
                    try:
                        b[Restrains_names[a[3]]] = float(a[4]) # Handle optional second value
                    except IndexError:
                        pass
                elif current_section == "BOUNDS":      
                    # BOUNDS section: Parse variable bounds and store them              
                    a = line.split()  # Split the line into a list of strings
                    if len(a) == 3:
                        a_string = f"{a[0]} {A_cols_names[a[2]]} None" # Bound with no explicit value
                    else:
                        a_string = f"{a[0]} {A_cols_names[a[2]]} {a[3]}" # Bound with value

                    # Append the string to the Bounds list
                    Bounds.append(a_string) 
                else:
                    continue


    # Finalize column data and add last index to A_cols
    A_cols.append(nnz)
    c.extend([0] * zeros_in_c_in_a_row) # Ensure the objective function has all coefficients


    print("Parsing Completed")
    # Convert matrix A to compressed sparse column format (CSC) and then to CSR format for efficiency    
    A_sparse_csc = sparse.csc_array((A_values,A_rows,A_cols)) 
    A_sparse_csr = A_sparse_csc.tocsr()

    # Return the parsed data as a dictionary
    return {"MinMax":MinMax, "A":A_sparse_csr , "b":b , "c":c , "Eqin":Eqin , "Bounds":Bounds}


def save_txt_file(file_path: str , MinMax:int , A : sparse.csr_array , b: np.ndarray , c: list[float], Eqin: list[int] , Bounds:list[str] ) -> None:
    """
    Saves the linear programming problem data to a text file in a structured format, including the constraint matrix, 
    objective function, bounds, and constraint types.

    Parameters:
    -----------
    file_path : str
        The path where the text file will be saved.
    MinMax : int
        Indicates whether the problem is a minimization (-1) or maximization (1).
    A : sparse.csr_array
        The sparse constraint matrix A in CSR format.
    b : np.ndarray
        The right-hand side vector for the constraints.
    c : list[float]
        The coefficients of the objective function.
    Eqin : list[int]
        List indicating the type of each constraint (-1 for <=, 0 for =, 1 for >=).
    Bounds : list[str]
        List of bounds for variables, if any.

    Returns:
    --------
    None

    Notes:
    ------
    - The constraint matrix `A` is written as a dense matrix with appropriate formatting.
    - The bounds section is only written if the `Bounds` list is not empty.
    
    Example:
    --------
    >>> save_txt_file("output.txt", MinMax, A_sparse, b, c, Eqin, Bounds)
    """
    with open(file_path, "w") as file:  # Open a file in write mode

        # Write A 
        file.write("A=[\n")  # Start the matrix format
        for i in range(A.shape[0]):  # Iterate over rows
            row_start = A.indptr[i]
            row_end = A.indptr[i + 1]
            col_indices = A.indices[row_start:row_end]
            data = A.data[row_start:row_end]
            
            # Initialize an empty row and fill with zeros
            row = np.zeros(A.shape[1], dtype=A.dtype)
            
            # Place the non-zero elements into the row
            row[col_indices] = data
            
            # Write the formatted row to the file
            file.write("  ".join(f"{elem:>11}" for elem in row) + "\n")
        
        file.write("]\n\n")  # Close the matrix format

        # Write b 
        file.write("b=[\n " + "\n ".join(f"{value:>11}" for value in b) + "\n]\n\n")  # Format and write all values in one go

        # Write c 
        file.write("c=[\n " + "\n ".join(f"{value:>11}" for value in c) + "\n]\n\n")  # Format and write all values in one go

        # Write Eqin
        file.write("Eqin=[\n " + "\n ".join(f"{value:>2}" for value in Eqin) + "\n]\n\n")  # Format and write all values in one go

        # Write MinMax
        file.write(f"MinMax= {MinMax}\n\n") 

        # Write BS if they exist
        if Bounds :
            file.write("BS=[\n " + "\n ".join(Bounds) + "\n]\n")  # Format and write all values in one go


def main() -> None:

    selected_file = select_file()    
    print(f"Selected file: {selected_file}")

    
    # Start measuring CPU time
    start_time = time.process_time()

    parsed_data = parse_mps_file(selected_file)

    # Stop measuring CPU time
    end_time = time.process_time()

    # Calculate the total CPU time used
    cpu_time_used = end_time - start_time

    print(f"CPU time used: {cpu_time_used} seconds")


    save_file = select_save_file_path()    
    print(f"Data is being saved to: {save_file}")
    save_txt_file(save_file, **parsed_data )
    print("File saved successfully")



if __name__ == "__main__":

    main()

