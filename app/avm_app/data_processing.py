import pandas as pd
import numpy as np

column_phrases = {
    'AVM Value': [
        lambda col: any(phrase.lower() in col.lower() for phrase in ['AVM Value', 'AVM', 'ValPro', 'hc_avm', 'VEROVALUE', 'AVM Estimate', 'valuation', 'AVM_VALUE', 'Point']) and col != 'AVM Model Name'
    ],
    'Conf Score': [
        'Confidence Score', 'CONFIDENCESCORE', 'Confidence', 'hc_confidence_score', 'Score', 'VCS', 'Primary Confidence Score', 'SCORE', 'confidence', 'Confidence', 'Conf Score'
    ],
    'Ref ID': [
        'Ref ID', 'RefID', 'ID', 'REF_ID', 'ref_id', 'TESTREF', 'LOANID', 'RefNum', 'ref id'
    ],
    'FSD': [
        'FSD', 'FSD Value', 'Forecast Standard Deviation', 'Standard Deviation'
    ]
}

def calculate_fsd(conf_score):
    return (100 - conf_score) / 100

import logging

logging.basicConfig(level=logging.DEBUG)

def find_avm_score_parallel(model_files, ref_id, model_file_data, column_phrases, min_conf_scores, max_fsd_values):
    for model_num, model_name in model_files.items():
        if model_name in model_file_data:
            model_df = model_file_data[model_name]
            avm_column_name = next((col for col in model_df.columns if any((phrase(col) if callable(phrase) else phrase.lower() in col.lower()) for phrase in column_phrases['AVM Value'])), None)
            conf_column_name = next((col for col in model_df.columns if any(phrase.lower() in col.lower() for phrase in column_phrases['Conf Score'])), None)
            ref_id_column_name = next((col for col in model_df.columns if any(phrase.lower() in col.lower() for phrase in column_phrases['Ref ID'])), None)
            fsd_column_name = next((col for col in model_df.columns if any(phrase.lower() in col.lower() for phrase in column_phrases['FSD'])), None)

            logging.debug(f"Model: {model_name}, AVM Column: {avm_column_name}, Conf Column: {conf_column_name}, Ref ID Column: {ref_id_column_name}, FSD Column: {fsd_column_name}")

            if ref_id_column_name and avm_column_name:
                avm_value = model_df[model_df[ref_id_column_name] == ref_id][avm_column_name]
                conf_score = model_df[model_df[ref_id_column_name] == ref_id][conf_column_name] if conf_column_name else None
                fsd_value = model_df[model_df[ref_id_column_name] == ref_id][fsd_column_name] if fsd_column_name else pd.Series([calculate_fsd(cs) for cs in conf_score]) if conf_score is not None else None
                
                if not avm_value.empty and not pd.isna(avm_value.iloc[0]):
                    avm_val = avm_value.iloc[0]

                    fsd_value_numeric = pd.to_numeric(fsd_value.iloc[0], errors='coerce') if fsd_value is not None and not fsd_value.empty else None
                    if fsd_value_numeric is not None and fsd_value_numeric > 1:
                        fsd_value_numeric /= 100

                    max_fsd_value = max_fsd_values.get(model_name, float('inf'))

                    # Apply FSD filtering for all models
                    if fsd_value_numeric is not None and fsd_value_numeric <= max_fsd_value:
                        if model_name not in ['ClearAVMv3', 'Freddie Mac Home Value Explorer']:
                            if conf_score is not None and not conf_score.empty and not pd.isna(conf_score.iloc[0]):
                                conf_score_numeric = pd.to_numeric(conf_score.iloc[0], errors='coerce')

                                if model_name == 'iAVM':
                                    conf_score_numeric *= 100

                                min_conf_score = min_conf_scores.get(model_name, 0)

                                if conf_score_numeric >= min_conf_score:
                                    return avm_val, conf_score_numeric, fsd_value_numeric, model_num, model_name
                        else:
                            return avm_val, None, fsd_value_numeric, model_num, model_name
    return None, None, None, None, None
