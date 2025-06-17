import pandas as pd
import csv
import os

def read_benchmark_file(file_path, desired_forms):
    df = pd.read_csv(file_path, quoting=csv.QUOTE_ALL, low_memory=False)
    return df[df['FormName'].isin(desired_forms)]

def read_cascade_file(file_path):
    """
    Reads the cascade file and replaces "Clear Capital" with "ClearAVMv3".
    """
    df = pd.read_csv(file_path)
    df.replace('Clear Capital', 'ClearAVMv3', inplace=True)
    return df

def get_avm_model_files(cascade_df, state, county):
    """
    Retrieves AVM model files based on state and county from the cascade DataFrame.
    Adjusted to handle "ClearAVMv3" as "Clear Capital" as well as variable model columns.
    
    - Handles cases where some cascades may have empty counties or states (NaN or missing).
    - If a particular cascade row has a NaN in County, we allow a fallback to the row that has County == NaN.
    """

    # Safely lowercase the incoming state and county, handling None
    state = str(state).lower() if state else ""
    county = str(county).lower() if county else ""

    # Replace "Clear Capital" -> "ClearAVMv3" for consistency
    cascade_df = cascade_df.replace({'Clear Capital': 'ClearAVMv3'})

    # Identify all cascade columns that start with "Model"
    model_columns = [col for col in cascade_df.columns if col.startswith('Model')]

    # 1) Try to match rows where State matches and County matches (case-insensitive)
    county_filtered = cascade_df[
        (cascade_df['State'].fillna("").astype(str).str.lower() == state) &
        (cascade_df['County'].fillna("").astype(str).str.lower() == county)
    ]
    if not county_filtered.empty:
        # Found a row for specific county
        models = {col: county_filtered.iloc[0][col] for col in model_columns}
        return models

    # 2) Otherwise, try to match rows where State matches and County is NaN
    #    (i.e., a default row for that state but no specific county)
    state_filtered = cascade_df[
        (cascade_df['State'].fillna("").astype(str).str.lower() == state) &
        (cascade_df['County'].isna())
    ]
    if not state_filtered.empty:
        # Found a row for that state with no county
        models = {col: state_filtered.iloc[0][col] for col in model_columns}
        return models

    # 3) If nothing matched, return all model columns as None
    return {col: None for col in model_columns}

def get_keyword_from_model(model):
    if isinstance(model, str):
        keywords = {
            'VeroVALUE': 'VeroValue',
            'VeroValue Pref': 'VeroValue',
            'Total Home ValueX Risk Management': 'THVx RM',
            'Quantarium': 'QM1',
            'CA Value MC': 'CA Value MC',
            'HouseCanary Value Report': 'HouseCanary',  # Alternate for HouseCanary
            'HouseCanary': 'HouseCanary',  # Alternate for HouseCanary
            'CA Value': 'CA Value',
            'Total Home ValueX Originations': 'THVx Orig',
            'Freddie Mac Home Value Explorer': 'Freddie',  # HVE
            'HVE': 'Freddie',
            'Freddie Mac Home Value Explorer': 'HVE',      # Alternate for Freddie Mac
            'iAVM': 'iAVM',
            'SiteXValue': 'BKFS',
            'RVM': 'BKFS',
            'ValueSure': 'BKFS',
            'FiveBridges': 'FiveBridges',
            'ClearAVMv3': 'ClearAVMv3',
        }
        return keywords.get(model, model)
    else:
        return None

def find_file_with_keyword(folder_path, keyword):
    if not keyword:
        return None
    for file in os.listdir(folder_path):
        if keyword.lower() in file.lower():
            return file
    return None

def read_files_once(unique_models, avm_folder):
    model_file_data = {}
    for model in unique_models:
        keyword = get_keyword_from_model(model)
        if keyword:
            file_name = find_file_with_keyword(avm_folder, keyword)
            if file_name:
                file_path = os.path.join(avm_folder, file_name)
                if file_path.endswith('.csv'):
                    model_df = pd.read_csv(file_path, low_memory=False)
                elif file_path.endswith('.xlsx'):
                    model_df = pd.read_excel(file_path)
                else:
                    continue  # Skip unsupported file formats

                # For these specific models, only keep rows whose 'AVM Model Name' matches
                if model in ['SiteXValue', 'RVM', 'ValueSure']:
                    model_df = model_df[model_df['AVM Model Name'] == model]

                model_file_data[model] = model_df
    return model_file_data
