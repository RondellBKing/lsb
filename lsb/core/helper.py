import csv
import os
import logging
import glob
import pandas as pd
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

    # Compare latest existing feed, only create a new one if there are differences.
    list_of_files = glob.glob(f'{temp_dir}/{county_name}*')
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getmtime)
        logging.info(f'Latest feed found -> {latest_file}')

        # Create Dataframe from the previous lead source and the new
        latest_data_feed_df = pd.read_csv(latest_file, index_col=False)
    else:
        logging.info(f'There is no existing feed for this county')
        latest_data_feed_df = pd.DataFrame()

    leads_df = pd.DataFrame(lead_list, columns=columns)

    new_lead_count = len(leads_df)
    prev_lead_count = len(latest_data_feed_df)

    logging.info(f'Found {new_lead_count} in latest pull compared to {prev_lead_count} in previous feed')

    # If the two feeds are equal return False
    return not leads_df.equals(latest_data_feed_df), leads_df 
