import tkinter as tk
from avm_app.combine_files import combine_files
from avm_app.profiles import load_profiles, save_profiles, load_profile
from avm_app.gui import AVMApp
from avm_app import read_benchmark_file, read_cascade_file, read_files_once, find_avm_score_parallel, write_results_to_excel, column_phrases

# Load profiles
profiles = load_profiles(
    default_min_conf_scores={
        'VeroVALUE': 90,
        'Total Home ValueX Risk Management': 0,
        'Quantarium': 0,
        'CA Value MC': 0,
        'HouseCanary Value Report': 87,
        'CA Value': 0,
        'Total Home ValueX Originations': 0,
        'Freddie Mac Home Value Explorer': 0,
        'iAVM': 90,
        'SiteXValue': 87,
        'RVM': 89,
        'ValueSure': 89,
        'FiveBridges': 0,
        'ClearAVMv3': 0
    },
    default_desired_forms=[
        '1004_agvn', '1004_05uad', '1004_05', '1004_20huad', '1004_20uad',
        '1004c_05', 'FHA Appraisal (FNMA 1004)', 'Ptadi15_1004',
        'Ptdai16_1004', 'Uniform Residential Appraisal (FNMA 1004)',
        'USDA Appraisal (FNMA 1004)'
    ],
    default_max_fsd_values={
        'VeroVALUE': 0.10,
        'Total Home ValueX Risk Management': 0.13,
        'Quantarium': 1,
        'CA Value MC': 0.10,
        'HouseCanary Value Report': 0.10,
        'CA Value': 0.10,
        'Total Home ValueX Originations': 0.13,
        'Freddie Mac Home Value Explorer': 1,
        'iAVM': 0.08,
        'SiteXValue': 0.08,
        'RVM': 0.08,
        'ValueSure': 0.08,
        'FiveBridges': 0.10,
        'ClearAVMv3': 0.13
    },
    default_available_forms=[
        '1004_agvn', '1004_05uad', '1004_05', '1004_20huad', '1004_20uad',
        '1004c_05', 'FHA Appraisal (FNMA 1004)', 'Ptadi15_1004',
        'Ptdai16_1004', 'Uniform Residential Appraisal (FNMA 1004)',
        'USDA Appraisal (FNMA 1004)', 'FormA', 'FormB', 'FormC', 'FormD', 'FormE'
    ]
)

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AVMApp(root, profiles, combine_files,
                 read_benchmark_file, read_cascade_file, read_files_once, find_avm_score_parallel,
                 write_results_to_excel, column_phrases)
    root.mainloop()
