# from scrapers import *

from scrapers import tuscola_mi
from scrapers import jackson_mi
from scrapers import shiawassee_mi
from scrapers import san_fran
from scrapers import sacremento_county
from scrapers import orange_fl
from scrapers import orange_ca
from scrapers import don_ana # Need to run once periodically to get passed security settings

''' Do We Need'''
from scrapers import lenawee_mi 
from scrapers import placer_ca
from scrapers import snohomish_wa
from scrapers import berrien_mi 
from scrapers import eaton_mi # Needs to be fixed

''' Need to be fixed'''
from scrapers import franklin_oh # Needs to be fixed
from scrapers import costa_ca # Needs to be fixed


if __name__ == "__main__":
    orange_ca.OrangeCA(delta=30).run(send_alert=True)