import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pandas as pd
import glob
from concurrent.futures import ThreadPoolExecutor
import os
# Import functions from the other modules
from avm_app.profiles import save_profiles, load_profile
from avm_app.combine_files import combine_files
from avm_app.avm_utils import read_benchmark_file, read_cascade_file, get_avm_model_files, read_files_once
from avm_app.data_processing import find_avm_score_parallel, column_phrases  # Ensure this is imported correctly 
from avm_app.file_operations import write_results_to_excel

class AVMApp:
    def __init__(self, root, profiles_data, combine_files, read_benchmark_file, read_cascade_file, read_files_once, find_avm_score_parallel, write_results_to_excel, column_phrases):
        self.root = root
        self.root.title("AVM Application")
        self.root.geometry("1700x800")  # Make the UI larger
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(7, weight=1)
        for i in range(20):  # adjust based on actual number of rows
            self.root.rowconfigure(i, weight=0)
        self.root.rowconfigure(6, weight=1)
        self.root.rowconfigure(8, weight=1)


        self.profiles_data = profiles_data
        self.profiles = profiles_data["profiles"]
        self.available_forms = profiles_data["available_forms"]

        self.current_profile = "Default"

        self.combine_files_func = combine_files
        self.read_benchmark_file = read_benchmark_file
        self.read_cascade_file = read_cascade_file
        self.read_files_once = read_files_once
        self.find_avm_score_parallel = find_avm_score_parallel
        self.write_results_to_excel = write_results_to_excel
        self.column_phrases = column_phrases

        self.create_widgets()
        self.load_profile(self.current_profile)

    def create_widgets(self):
        # Make columns expandable
        for col in [1, 7]:  # Primary input columns
            self.root.columnconfigure(col, weight=1)
        self.root.rowconfigure(6, weight=1)  # Allow the main section (row 6) to grow

        # Benchmark File
        tk.Label(self.root, text="Benchmark File").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.benchmark_file_entry = tk.Entry(self.root)
        self.benchmark_file_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse", command=self.select_benchmark_file).grid(row=0, column=2, padx=10, pady=5)

        # Cascade Folder
        tk.Label(self.root, text="Cascade Folder").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.cascade_folder_entry = tk.Entry(self.root)
        self.cascade_folder_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse", command=self.select_cascade_folder).grid(row=1, column=2, padx=10, pady=5)

        # AVM Folder
        tk.Label(self.root, text="AVM Folder").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.avm_folder_entry = tk.Entry(self.root)
        self.avm_folder_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse", command=self.select_avm_folder).grid(row=2, column=2, padx=10, pady=5)

        # Output Directory
        tk.Label(self.root, text="Output Directory").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.output_directory_entry = tk.Entry(self.root)
        self.output_directory_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse", command=self.select_output_directory).grid(row=3, column=2, padx=10, pady=5)

        # Profile management
        tk.Label(self.root, text="Profile").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.profile_var = tk.StringVar(value=self.current_profile)
        self.profile_dropdown = ttk.Combobox(self.root, textvariable=self.profile_var, values=list(self.profiles.keys()))
        self.profile_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        tk.Button(self.root, text="Load Profile", command=self.load_selected_profile).grid(row=4, column=2, padx=10, pady=5, sticky='w')
        tk.Button(self.root, text="Save Profile", command=self.save_current_profile).grid(row=4, column=3, padx=10, pady=5, sticky='w')
        tk.Button(self.root, text="Create Profile", command=self.create_new_profile).grid(row=4, column=4, padx=10, pady=5, sticky='w')

        # Min confidence scores
        tk.Label(self.root, text="Min Conf Scores").grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.conf_score_entries = {}
        conf_scores_frame = tk.Frame(self.root)
        conf_scores_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        for i in range(10):
            conf_scores_frame.rowconfigure(i, weight=1)
        row_num = 0
        for model in self.profiles[self.current_profile]["min_conf_scores"]:
            tk.Label(conf_scores_frame, text=model).grid(row=row_num, column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(conf_scores_frame, width=10)
            entry.grid(row=row_num, column=1, padx=10, pady=5, sticky='w')
            self.conf_score_entries[model] = entry
            row_num += 1

        # FSD Thresholds
        tk.Label(self.root, text="Max FSD Values").grid(row=5, column=2, padx=10, pady=5, sticky='w')
        self.fsd_entries = {}
        fsd_frame = tk.Frame(self.root)
        fsd_frame.grid(row=6, column=2, columnspan=2, padx=10, pady=5, sticky='nsew')
        row_num = 0
        for model in self.profiles[self.current_profile]["max_fsd_values"]:
            tk.Label(fsd_frame, text=model).grid(row=row_num, column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(fsd_frame, width=10)
            entry.grid(row=row_num, column=1, padx=10, pady=5, sticky='w')
            self.fsd_entries[model] = entry
            row_num += 1

        # Desired forms
        tk.Label(self.root, text="Desired Forms").grid(row=5, column=4, padx=10, pady=5, sticky='w')
        self.forms_frame = tk.Frame(self.root)
        self.forms_frame.grid(row=6, column=4, columnspan=2, padx=10, pady=5, sticky='nsew')
        self.forms_frame.columnconfigure(0, weight=1)

        self.form_vars = {form: tk.BooleanVar(value=form in self.profiles[self.current_profile]["desired_forms"]) for form in self.available_forms}
        self.form_checkbuttons = {}
        for form, var in self.form_vars.items():
            chk = tk.Checkbutton(self.forms_frame, text=form, variable=var)
            chk.pack(anchor='w')
            self.form_checkbuttons[form] = chk

        self.new_form_var = tk.StringVar()
        self.new_form_dropdown = ttk.Combobox(self.forms_frame, textvariable=self.new_form_var)
        self.new_form_dropdown['values'] = self.available_forms
        self.new_form_dropdown.pack(side='top', padx=5, pady=5, fill='x')
        tk.Button(self.forms_frame, text="Add Form", command=self.add_form).pack(side='top', padx=5, pady=5)

        # Start button
        tk.Button(self.root, text="Start Processing", command=self.start_processing).grid(row=7, column=1, padx=10, pady=20, sticky='w')

        # Combine files section
        tk.Label(self.root, text="Combine Files - Folder").grid(row=0, column=6, padx=10, pady=5, sticky='w')
        self.combine_folder_entry = tk.Entry(self.root)
        self.combine_folder_entry.grid(row=0, column=7, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse", command=self.select_combine_folder).grid(row=0, column=8, padx=10, pady=5)

        tk.Label(self.root, text="Start Number").grid(row=1, column=6, padx=10, pady=5, sticky='w')
        self.start_num_entry = tk.Entry(self.root, width=10)
        self.start_num_entry.grid(row=1, column=7, padx=10, pady=5, sticky='w')

        tk.Label(self.root, text="End Number").grid(row=2, column=6, padx=10, pady=5, sticky='w')
        self.end_num_entry = tk.Entry(self.root, width=10)
        self.end_num_entry.grid(row=2, column=7, padx=10, pady=5, sticky='w')

        tk.Label(self.root, text="Output Folder").grid(row=3, column=6, padx=10, pady=5, sticky='w')
        self.combine_output_folder_entry = tk.Entry(self.root)
        self.combine_output_folder_entry.grid(row=3, column=7, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse", command=self.select_combine_output_folder).grid(row=3, column=8, padx=10, pady=5)

        tk.Button(self.root, text="Combine Files", command=self.combine_files).grid(row=4, column=7, padx=10, pady=20, sticky='w')

        # Progress bar
        # self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        # self.progress.grid(row=8, column=1, columnspan=2, pady=10, sticky='ew')



    def load_profile(self, profile_name):
        self.current_profile = profile_name
        min_conf_scores, desired_forms, max_fsd_values, self.available_forms = load_profile(self.profiles_data, profile_name)

        for model, score in min_conf_scores.items():
            self.conf_score_entries[model].delete(0, tk.END)
            self.conf_score_entries[model].insert(0, str(score))

        for model, fsd_value in max_fsd_values.items():
            self.fsd_entries[model].delete(0, tk.END)
            self.fsd_entries[model].insert(0, str(fsd_value))

        for form, var in self.form_vars.items():
            var.set(form in desired_forms)

        self.new_form_dropdown['values'] = self.available_forms

    def load_selected_profile(self):
        self.load_profile(self.profile_var.get())

    def save_current_profile(self):
        profile_name = self.profile_var.get()
        min_conf_scores = {model: float(entry.get()) for model, entry in self.conf_score_entries.items()}
        max_fsd_values = {model: float(entry.get()) for model, entry in self.fsd_entries.items()}
        desired_forms = {form for form, var in self.form_vars.items() if var.get()}

        self.profiles_data["profiles"][profile_name] = {
            "min_conf_scores": min_conf_scores,
            "desired_forms": list(desired_forms),
            "max_fsd_values": max_fsd_values
        }

        save_profiles(self.profiles_data)
        self.profile_dropdown['values'] = list(self.profiles_data["profiles"].keys())
        messagebox.showinfo("Profile Saved", f"Profile '{profile_name}' saved successfully!")

    def create_new_profile(self):
        new_profile_name = tk.simpledialog.askstring("Create Profile", "Enter new profile name:")
        if new_profile_name and new_profile_name not in self.profiles_data["profiles"]:
            self.profiles_data["profiles"][new_profile_name] = {
                "min_conf_scores": {},
                "desired_forms": [],
                "max_fsd_values": {}
            }
            save_profiles(self.profiles_data)
            self.profile_dropdown['values'] = list(self.profiles_data["profiles"].keys())
            self.profile_var.set(new_profile_name)
            self.load_profile(new_profile_name)
            messagebox.showinfo("Profile Created", f"Profile '{new_profile_name}' created successfully!")
        elif new_profile_name in self.profiles_data["profiles"]:
            messagebox.showerror("Error", f"Profile '{new_profile_name}' already exists!")

    def select_benchmark_file(self):
        self.benchmark_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.benchmark_file_entry.insert(0, self.benchmark_file)

    def select_cascade_folder(self):
        self.cascade_folder = filedialog.askdirectory()
        self.cascade_folder_entry.insert(0, self.cascade_folder)

    def select_avm_folder(self):
        self.avm_folder = filedialog.askdirectory()
        self.avm_folder_entry.insert(0, self.avm_folder)

    def select_output_directory(self):
        self.output_directory = filedialog.askdirectory()
        self.output_directory_entry.insert(0, self.output_directory)

    def select_combine_folder(self):
        folder_path = filedialog.askdirectory()
        self.combine_folder_entry.insert(0, folder_path)

    def select_combine_output_folder(self):
        folder_path = filedialog.askdirectory()
        self.combine_output_folder_entry.insert(0, folder_path)

    def add_form(self):
        new_form = self.new_form_var.get().strip()
        if new_form and new_form not in self.form_vars:
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(self.forms_frame, text=new_form, variable=var)
            chk.pack(anchor='w', before=self.new_form_dropdown)
            self.form_vars[new_form] = var
            self.form_checkbuttons[new_form] = chk
            if new_form not in self.available_forms:
                self.available_forms.append(new_form)
                self.profiles_data["available_forms"] = self.available_forms
                save_profiles(self.profiles_data)
            self.new_form_var.set('')
            self.new_form_dropdown['values'] = self.available_forms

    def start_processing(self):
        if not self.benchmark_file or not self.cascade_folder or not self.avm_folder or not self.output_directory:
            messagebox.showerror("Error", "Please select all required files and folders.")
            return

        self.min_conf_scores = {model: float(entry.get()) for model, entry in self.conf_score_entries.items()}
        self.max_fsd_values = {model: float(entry.get()) for model, entry in self.fsd_entries.items()}
        self.desired_forms = {form for form, var in self.form_vars.items() if var.get()}

        benchmark_df = self.read_benchmark_file(self.benchmark_file, self.desired_forms)
        cascade_files = glob.glob(os.path.join(self.cascade_folder, '*.csv'))
        os.makedirs(self.output_directory, exist_ok=True)

        for cascade_path in cascade_files:
            cascade_df = self.read_cascade_file(cascade_path)
            available_models = [col for col in ['Model 1', 'Model 2', 'Model 3'] if col in cascade_df.columns]
            unique_models = pd.unique(cascade_df[available_models].values.ravel('K'))
            model_file_data = self.read_files_once(unique_models, self.avm_folder)
            new_excel_file = f"{self.output_directory}/{os.path.basename(self.avm_folder)}_{os.path.basename(cascade_path).replace('.csv', '')}.xlsx"

            results = self.process_benchmark(benchmark_df, cascade_df, model_file_data)
            self.write_results_to_excel(results, new_excel_file, self.min_conf_scores, self.max_fsd_values)




    def process_benchmark(self, benchmark_df, cascade_df, model_file_data):
        results = []

        def process_batch(batch):
            batch_results = []
            for _, row in batch.iterrows():
                ref_id, state, county = row['Ref ID'], row['State'], row['County']
                appraised_value = row['ContractPrice'] if 'ContractPrice' in row and not pd.isna(row['ContractPrice']) and row['ContractPrice'] != 0 else row['AppraisedValue']
                model_files = get_avm_model_files(cascade_df, state, county)
                avm_score, conf_score, fsd_value, model_num, model_name = self.find_avm_score_parallel(model_files, ref_id, model_file_data, self.column_phrases, self.min_conf_scores, self.max_fsd_values)
                batch_results.append((ref_id, state, county, appraised_value, avm_score, (avm_score - appraised_value) / appraised_value if avm_score is not None else None, model_name, conf_score, fsd_value, model_num))
            return batch_results

        batch_size = 10000
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            for i in range(0, len(benchmark_df), batch_size):
                batch = benchmark_df.iloc[i:i + batch_size]
                futures.append(executor.submit(process_batch, batch))

            for future in futures:
                results.extend(future.result())

        results_df = pd.DataFrame(results, columns=['Ref ID', 'State', 'County', 'Benchmark Value', 'AVM Value', '% Diff between AVM and Benchmark', 'AVM Name', 'AVM Conf Score', 'FSD Value', 'Model Position'])
        return results_df

    def combine_files(self):
        folder_path = self.combine_folder_entry.get()
        start_num = self.start_num_entry.get()
        end_num = self.end_num_entry.get()
        output_folder = self.combine_output_folder_entry.get()

        if not folder_path or not start_num or not end_num or not output_folder:
            messagebox.showerror("Error", "Please provide all inputs for combining files.")
            return

        try:
            start_num = int(start_num)
            end_num = int(end_num)
        except ValueError:
            messagebox.showerror("Error", "Start Number and End Number must be integers.")
            return

        self.combine_files_func(folder_path, start_num, end_num, output_folder)
