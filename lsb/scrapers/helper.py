import csv
import os
import logging
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