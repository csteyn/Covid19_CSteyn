# https://github.com/dsfsi/covid19za/blob/master/data/covid19za_timeline_testing.csv
# https://github.com/dsfsi/covid19za/blob/master/data/district_data/provincial_wc_cumulative.csv
# https://github.com/dsfsi/covid19za/blob/master/data/district_data/provincial_nw_cumulative.csv
# https://github.com/dsfsi/covid19za/blob/master/data/district_data/provincial_lp_cumulative.csv
# https://github.com/dsfsi/covid19za/blob/master/data/district_data/provincial_gp_cumulative.csv
# https://github.com/dsfsi/covid19za/blob/master/data/district_data/district_wc_keys.csv
# https://github.com/dsfsi/covid19za/blob/master/data/district_data/district_lp_keys.csv


import sys
import requests
import pandas as pd
import numpy as np

from datetime import datetime
from datetime import timedelta, date
import io

def get_SA_data(base_url='https://raw.githubusercontent.com/dsfsi/covid19za/master/data'):
    def load_timeseries(name, 
                    base_url='https://raw.githubusercontent.com/dsfsi/covid19za/master/data'):
   
        url = f'{base_url}/covid19za_provincial_cumulative_timeline_{name}.csv'
        csv = requests.get(url).text
        col_names =['date', 'EC','FS','GP','KZN','LP','MP','NC','NW','WC','UNKNOWN']
        names_full = ['date', 'Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal', 'Limpopo', 
                        'Mpumalanga', 'Northern Cape', 'North West', 'Western Cape', 'Unknown']
        df = pd.read_csv(io.StringIO(csv), lineterminator="\n")
        
        df = df[col_names]
        df.columns = names_full
   
        df.columns.name = 'province'
            
        df = (df.set_index('date')
                 .stack()
                 .reset_index()
                .set_index('date')                               
               )
            
        df.index = pd.to_datetime(df.index, dayfirst=True)
        df.columns = ['province', name]
                       
        return df

    # def load_timeseries_tests( 
    #                 url='https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_timeline_testing.csv'):
   
    #     csv = requests.get(url).text
    #     col_names =['date','cumulative_tests', 'recovered', 'hospitalisation', 'critical_icu', 'ventilation']
    #     df = pd.read_csv(io.StringIO(csv), lineterminator="\n")
        
    #     df = df[col_names]
     
    #     df.index = pd.to_datetime(df.index, dayfirst=True)
                       
    #     return df


    df_confirmed = load_timeseries('confirmed')
    df_deaths = load_timeseries('deaths')

    df_both = pd.merge(df_confirmed, df_deaths, on=['date', 'province'], how='left')
    
    df_both = df_both.reset_index()
   
    return df_both



