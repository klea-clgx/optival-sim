import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging
def read_file(file_path):
    """
    Reads a file into a DataFrame. Applies special logic for files with "Freddie" in the name.

    Parameters:
    - file_path (str): The path to the file to be read.

    Returns:
    - DataFrame: The DataFrame containing the file's data.
    """
    if os.stat(file_path).st_size == 0:
        logging.warning(f"Skipping empty file: {file_path}")
        return pd.DataFrame()

    try:
        # Check if the file name contains "Freddie"
        if 'Freddie' in os.path.basename(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                first_line = f.readline().strip()
            if not first_line.startswith('RefNum'):
                return pd.read_csv(file_path, skiprows=26)
            else:
                return pd.read_csv(file_path)
        elif file_path.endswith('.csv'):  # Handle CSV files
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                first_line = f.readline().strip()
            return pd.read_csv(file_path, delimiter='|' if '|' in first_line else ',')
        elif file_path.endswith(('.xlsx', '.xls')):  # Handle Excel files
            return pd.read_excel(file_path)
        else:
            logging.warning(f"Unsupported file format: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return pd.DataFrame()


def combine_files(folder_path, start_num, end_num, output_folder):
    """
    Combines multiple CSV and Excel files into a single CSV file.

    Parameters:
    - folder_path (str): The path to the folder containing the files to be combined.
    - start_num (int): The start number for filtering files by name.
    - end_num (int): The end number for filtering files by name.
    - output_folder (str): The path to the folder where the combined file will be saved.

    Returns:
    - None
    """
    files_to_process = []
    # Iterate through files in the folder
    for file in os.listdir(folder_path):
        # Filter files by extension and name containing numbers in the specified range
        if file.endswith(('.csv', '.xlsx', '.xls')) and any(str(num) in file for num in range(start_num, end_num + 1)):
            files_to_process.append(os.path.join(folder_path, file))

    combined_df = pd.DataFrame()
    # Use ThreadPoolExecutor to read files in parallel
    with ThreadPoolExecutor() as executor:
        # Read each file and concatenate the resulting DataFrames
        for df in executor.map(read_file, files_to_process):
            combined_df = pd.concat([combined_df, df])

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Construct the output file name and path
    output_file_name = f"{os.path.basename(folder_path)}_{start_num}-{end_num}.csv"
    output_file_path = os.path.join(output_folder, output_file_name)
    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(output_file_path, index=False)
    print(f"Combined file created: {output_file_path}")
