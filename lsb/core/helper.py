import csv
import os
import logging
import glob
import pandas as pd
import numpy as np
from dateutil.parser import parse

""" User defined Helper functions. Temporary Location."""
def write_csv(filename, header, data_dict):
    with open(filename, 'w+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(data_dict)

def remove_old_lead_files(list_of_files):
        if len(list_of_files) > 3:
            oldest_file = min(list_of_files, key=os.path.getmtime)
            print(f'Removing {oldest_file}')
            logging.info(f'Removing {oldest_file}')
            os.remove(oldest_file)

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def is_new_feed(lead_list, temp_dir, county_name, columns):
    """
    Check temp drive and compare feeds. If feed is new return true, False if not.

    Send Email
    :return:
    """
    is_new = True

    # Compare latest existing feed, only create a new one if there are differences.
    list_of_files = glob.glob(f'{temp_dir}/{county_name}*')
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getmtime)
        logging.info(f'Latest feed found -> {latest_file}')

        # Create Dataframe from the previous lead file stored
        prev_leads_df = pd.read_csv(latest_file, index_col=False)
    else:
        logging.info(f'There is no existing feed for this county')
        prev_leads_df = pd.DataFrame()

    new_leads_df = pd.DataFrame(lead_list, columns=columns)

    new_lead_count = len(new_leads_df)
    prev_lead_count = len(prev_leads_df)

    logging.info(f'Found {new_lead_count} in the current pull compared to {prev_lead_count} in previous feed')

    if new_leads_df.equals(prev_leads_df):
        is_new = False
    # Check if every record in the existing leads feed exist in the old if they do, ignore results
    # False alert occurs when the old leads have fallen off since the results will not match.
    elif new_lead_count < prev_lead_count: 
        compare_df = pd.merge(new_leads_df, prev_leads_df, on=['LienDate','Taxpayer'], how='left', indicator='Exist')
        compare_df['New_Record'] = compare_df['Exist'] = np.where(compare_df.Exist == 'left_only', True, False)

        if compare_df.New_Record.sum() == 0:
            logging.info('New Feed has leads that have fallen out of current date range')
            is_new = False

    # If the two feeds are equal return False
    return is_new, new_leads_df 
