
import tkinter as tk
from tkinter import filedialog
import os
from typing import Any

import numpy as np
from scipy import sparse

import time

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

    # Compressed Sparse Column (CSC)        
    A_values : list[float] = []
    A_rows : list[int] = []     # Full all rows 
    A_cols : list[int] = []     # Points where it starts in A_values
    A_cols_names : list[str] = []
    last_column_name : str = ""
    nnz :int = 0  
    current_row :int 
    current_col :int = -1 
    zeros_in_c_in_a_row :int = 0

    b : np.typing.NDArray
    # b : list[float] = []
    c : list[float] = [] #np.array([])  np.typing.NDArray
    Eqin : list[int] = []
    MinMax :int = -1 
    Bounds = []
    
    # Helpful variables
    convert_dict = {"L": -1 , "E":0 , "G":1}
    problem_name : str = ""
    objective_fun : str = ""
    num_of_restrains : int  = 0 # equals to m / numbers of rows 
    Restrains_names : dict[str,int] = {}

    current_section = None

    with open(file_path, 'r') as file:
        for line in file:
            # Ignore comments and empty lines
            if line.startswith('*') or line.strip() == '':
                continue

            # Use "Match-Case" to make it faster 
            # Determine which section we are in
            if line.startswith("NAME"):
                current_section = "NAME"
                problem_name = line.split()[1]  # Extract problem name
            elif line.startswith("ROWS"):
                current_section = "ROWS"
            elif line.startswith("COLUMNS"):
                current_section = "COLUMNS"
            elif line.startswith("RHS"):
                b = np.zeros(num_of_restrains)
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
                    # Remove spaces
                    a = line.strip().split()
                    try:
                        Eqin.append( convert_dict[a[0]] ) 
                        Restrains_names[a[1]] = num_of_restrains
                        num_of_restrains += 1
                    except KeyError as e :
                        if str(e) == "'N'":
                            objective_fun = a[1]
                            
                            print("Objective fun name:" , objective_fun)
                        else:
                            raise  # Re-raise the exception if it's a different key
                elif current_section == "COLUMNS":
                    a = line.strip().split() 
                    #  Current column is current_col
                    #  a[0] is the column name (variable name ie X1) 
                    #  Current row is current_row
                    #  a[1] is the row name (restrictions)
                    #  a[2] is the value (coefficient of X1)
                    if a[0] != last_column_name :
                        last_column_name = a[0]
                        A_cols_names.append(a[0])
                        A_cols.append(nnz)
                        current_col += 1 
                        zeros_in_c_in_a_row += 1

                    
                    try:
                        current_row = Restrains_names[a[1]]
                        A_values.append(float(a[2]))
                        A_rows.append(current_row)
                        nnz += 1 
                    except KeyError as e:
                        if str(e) == "'" + objective_fun + "'" :
                            c.extend([0] * (zeros_in_c_in_a_row-1))
                            # c[current_col] = float(a[2])
                            zeros_in_c_in_a_row = 0 
                            c.append(float(a[2]))
                        else:
                            raise  # Re-raise the exception if it's a different key

                    try:
                        current_row = Restrains_names[a[3]]
                        A_values.append(float(a[4]))
                        A_rows.append(current_row)
                        nnz += 1 
                    except KeyError as e:
                        if str(e) == "'" + objective_fun + "'":
                            # c[current_col] = float(a[4])
                            c.extend([0] * (zeros_in_c_in_a_row-1))
                            zeros_in_c_in_a_row = 0 
                            c.append(float(a[4]))
                        else:
                            raise  # Re-raise the exception if it's a different key
                    except IndexError:
                        pass
                elif current_section == "RHS":
                    a = line.strip().split() 
                    
                    b[Restrains_names[a[1]]] = float(a[2])
                    try:
                        b[Restrains_names[a[3]]] = float(a[4])
                    except IndexError:
                        pass
                elif current_section == "BOUNDS":                    
                    # Process the line
                    a = line.strip().split()  # Split the line into a list of strings
                    # Create a new list excluding the second element
                    a = [a[0]] + a[2:]  # Create a new list without the second element

                    # Append "None" if the length is 2
                    if len(a) == 2:
                        a.append("None")

                    # Append the joined string to the Bounds list
                    Bounds.append(" ".join(a))
                else:
                    continue


                # elif current_section == "RANGES":
                #     mps_data["RANGES"].append(line.strip())

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csc_array.html#scipy.sparse.csc_array
    # Add the last index to the A_cols array 
    A_cols.append(nnz)
    c.extend([0] * zeros_in_c_in_a_row)

    # print("Num rows = ", num_of_restrains)
    # print("Objective fun name:" , objective_fun)
    # print(f"Restrains_names ({len(Restrains_names)}):" , Restrains_names)
    # print(f"A_cols_names/Varibales ({len(A_cols_names)}):" , A_cols_names)

    print("Parsing Done")

    A_sparse_csc = sparse.csc_array((A_values,A_rows,A_cols))

    # print(f"A_sparse_csc: ({A_sparse_csc.shape}) =>",A_sparse_csc)
    
    print("Stored in CSC")

    # Convert to CSR (Compressed Sparse Row)
    A_sparse_csr = A_sparse_csc.tocsr()
    print("Stored in CSR")
    
    # print(f"A_sparse_csr: ({A_sparse_csr.shape}) =>",A_sparse_csr)


    # print("A = [" , end="")
    # for i in range(A_sparse_csr.shape[0]):  # Rows
    #     for j in range(A_sparse_csr.shape[1]):  # Columns
    #         # Format each element to a fixed width (e.g., 8 characters wide)
    #         print(f"{A_sparse_csr[i, j]:>8}", end="  ")  # Right-align elements in a 8-character field
    #     print()
    # print("]\n")



    with open("output_matrix.txt", "w") as file:  # Open a file in write mode

        # Write A 
        file.write("A=[\n")  # Start the matrix format
        for i in range(A_sparse_csr.shape[0]):  # Iterate over rows
            row_start = A_sparse_csr.indptr[i]
            row_end = A_sparse_csr.indptr[i + 1]
            col_indices = A_sparse_csr.indices[row_start:row_end]
            data = A_sparse_csr.data[row_start:row_end]
            
            # Initialize an empty row and fill with zeros
            row = np.zeros(A_sparse_csr.shape[1], dtype=A_sparse_csr.dtype)
            
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

        # Write BS
        if Bounds :
            file.write("BS=[\n " + "\n ".join(Bounds) + "\n]\n")  # Format and write all values in one go





    return {"MinMax":MinMax, "A":[A_values,A_rows,A_cols] , "b":b , "c":c , "Eqin":Eqin , "BS":Bounds}


def main() -> None:

    # selected_file = "Test_Datasets/afiro.mps"
    selected_file = "Test_Datasets/ex1.mps"
    # selected_file = select_file()    
    print(f"Selected file: {selected_file}")

    
    # Start measuring CPU time
    start_time = time.process_time()

    parsed_data = parse_mps_file(selected_file)

    # Stop measuring CPU time
    end_time = time.process_time()

    # Calculate the total CPU time used
    cpu_time_used = end_time - start_time

    print(f"CPU time used: {cpu_time_used} seconds")
    # print(parsed_data)

    # print(f"A_values ({len(parsed_data['A'][0])}) => ",parsed_data["A"][0])
    # print(f"A_rows ({len(parsed_data['A'][1])})=> ",parsed_data["A"][1])
    # print(f"A_cols ({len(parsed_data['A'][2])})=> ",parsed_data["A"][2])
    # print()    
    # print(f"c ({len(parsed_data['c'])}) => ",parsed_data["c"])
    # print()
    # print(f"b ({len(parsed_data['b'])}) => ",parsed_data["b"])
    # print()
    # print(f"Eqin ({len(parsed_data['Eqin'])})=> ",parsed_data["Eqin"])
    # print()
    # print(f"BS ({len(parsed_data['BS'])})=> ",parsed_data["BS"])


if __name__ == "__main__":

    main()

