#Collet the Covid 19 World data from the Johns Hopkins github page

import sys
import requests
import pandas as pd
import numpy as np

from datetime import datetime
from datetime import timedelta, date
import io

def get_data(base_url='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'):
    def load_timeseries(name, 
                    base_url='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'):
   
        url = f'{base_url}/time_series_covid19_{name}_global.csv'
        csv = requests.get(url).text
        df = pd.read_csv(io.StringIO(csv), 
                        index_col=['Country/Region', 'Province/State', 'Lat', 'Long'])
                        
        df['type'] = name.lower()
        
        df.columns.name = 'date'
            
        df = (df.set_index('type', append=True)
                .reset_index(['Lat', 'Long'], drop=True)
                .stack()
                .reset_index()
                .set_index('date')
            )
            
        df.index = pd.to_datetime(df.index)
        
        df.columns = ['country', 'state', 'type', 'cases']
            
        # Move HK to country level
        df.loc[df.state =='Hong Kong', 'country'] = 'Hong Kong'
        df.loc[df.state =='Hong Kong', 'state'] = np.nan

        #UK and France add state to blank file
        df.loc[(df.state.isna()) & (df.country == 'United Kingdom'), 'state'] = 'Main'
        df.loc[(df.state.isna()) & (df.country == 'France'), 'state'] = 'Main'

        # Aggregate large countries split by states
        df = pd.concat([df,
                        (df.loc[~df.state.isna()]
                        .groupby(['country', 'date', 'type'])
                        .sum()
                        .rename(index=lambda x: x+' (total)', level=0)
                        .reset_index(level=['country', 'type']))
                    ])

                    
        return df

    df_confirmed = load_timeseries('confirmed')
    df_deaths = load_timeseries('deaths')
    df_both = pd.merge(df_confirmed, df_deaths, on=['date', 'country', 'state'])
    df_both = df_both.drop(["type_x", "type_y"], axis=1)
    df_both.rename(columns={'cases_x': 'confirmed',
                    'cases_y': 'deaths'},
                        inplace=True, errors='raise')

    df_both = df_both.reset_index()

    select = ['South Africa', 'US', 'Japan', 'Korea, South', 'Italy', 'Spain', 'Germany', 'United Kingdom (total)', 
                'Russia', 'India', 'Australia (total)','Turkey','Iran', 'Canada (total)', 'Hong Kong', 'Argentina', 
                'Brazil', 'Colombia', 'Chile', 'China (total)', 'France (total)', 'Sweden', 'Netherlands (total)', 
                'Belgium', 'New Zealand', 'Switzerland', 'Portugal', 'Pakistan', 'Mexico', 'Israel', 'Greece',
                'Finland', 'Egypt', 'Denmark (total)', 'Ecuador', 'Peru', 'Ireland', 'Austria', 'Saudi Arabia', 'Singapore',
                'Poland', 'Romania', 'Qatar', 'Belarus']
    df_both = df_both.loc[(df_both.country.isin (select))]

    df_both['country'].replace(to_replace ='United Kingdom (total)', value='UK', inplace=True)
    df_both['country'].replace(to_replace ='Australia (total)', value='Austrailia', inplace=True)
    df_both['country'].replace(to_replace ='Canada (total)', value='Canada', inplace=True)
    df_both['country'].replace(to_replace ='China (total)', value='China', inplace=True)
    df_both['country'].replace(to_replace ='France (total)', value='France', inplace=True)
    df_both['country'].replace(to_replace ='Korea, South', value='South Korea', inplace=True)
    df_both['country'].replace(to_replace ='Netherlands (total)', value='Netherlands', inplace=True)
    df_both['country'].replace(to_replace ='Denmark (total)', value='Denmark', inplace=True)
    
    return df_both

