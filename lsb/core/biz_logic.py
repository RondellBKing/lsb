# Identify Business Leads
import pandas as pd
from pathlib import Path
import os

def is_business(row, text_column = 'Taxpayer'):
    parent_dir = os.fspath(Path(__file__).resolve().parents[1].resolve()) # Relative to point of execution
    biz_loc = os.path.join(parent_dir, 'Business Key Words.csv')
    biz_key_words = pd.read_csv(biz_loc)
    biz_word_list = biz_key_words['Keyword'].tolist()
    pattern = '|'.join(biz_word_list)
    # leads_df['IsBiz'] = leads_df.Taxpayer.str.contains(pattern, case=False)

    return row.Taxpayer.contains(pattern, case=False, na=False)

def is_business(df, text_column = 'Taxpayer'):
    # Prioritized List
    parent_dir = os.fspath(Path(__file__).resolve().parents[1].resolve()) # Relative to point of execution
    biz_loc = os.path.join(parent_dir, 'Business Key Words.csv')
    biz_key_words = pd.read_csv(biz_loc)
    biz_word_list = biz_key_words['Keyword'].tolist()
    pattern = '|'.join(biz_word_list)

    df['IsBiz'] = df.Taxpayer.str.contains(pattern, case=False)

    return df
# test = pd.read_csv('test_biz.csv')