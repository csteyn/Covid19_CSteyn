# Function to plot confirmed cases
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta, date

# from get_data import df_both
def table_country (df, dfSA, country="South Africa"):
    
    # case_threshold = 100
    current_dateSA =df.date.max()  

    dfc = df.loc[df['country']==country]
    dfc = dfc.sort_values('date')
    dfc = dfc.reset_index()

    dfc = (dfc.assign(daily_new=dfc[['confirmed']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))

    dfc = (dfc.assign(avg_daily_new=dfc[['daily_new']]
                                    .rolling(7).mean()
                                    .reset_index(0, drop=True)))
    dfc = (dfc.assign(growth_factor=(dfc.avg_daily_new/dfc.avg_daily_new.shift(1)).round(2)))

    dfc = (dfc.assign(daily_new_deaths=dfc[['deaths']]
                                .diff().fillna(method = 'ffill')
                                .reset_index(0, drop=True)))

    dataSA = dfc[['country', 'confirmed', 'daily_new', 'deaths', 'daily_new_deaths', 'growth_factor']].loc[dfc['date']==current_dateSA]
    dataSA.rename(columns={'country': 'province'}, inplace=True)  


    dfp = dfSA[['date', 'province', 'confirmed', 'deaths']].sort_values('date')
    dfp = dfp[dfp['province'] != 'Unknown']
    dfp = dfp.reset_index()
    current_date_prov =dfp.date.max()  
    dfp = (dfp.assign(daily_new=dfp.groupby('province', as_index=False)[['confirmed']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))
    

    dfp = (dfp.assign(avg_daily_new=dfp.groupby('province', as_index=False)[['daily_new']]
                                    .rolling(7).mean()
                                    .reset_index(0, drop=True)))

    dfp = (dfp.assign(growth_factor=(dfp.avg_daily_new/dfp.avg_daily_new.shift(1)).round(2)))

    dfp = (dfp.assign(daily_new_deaths=dfp.groupby('province', as_index=False)[['deaths']]
                                .diff().fillna(method = 'ffill')
                                .reset_index(0, drop=True)))
    
    dfp['deaths'] = dfp.groupby('province', as_index=False)[['deaths']].fillna(method = 'ffill')
    # dfp.deaths.fillna(method = 'ffill', inplace = True)
    dataProvince = dfp[['province', 'confirmed', 'daily_new', 'deaths', 'daily_new_deaths', 'growth_factor']].loc[dfp['date']==current_date_prov]
    dataProvince.sort_values(by=['confirmed'], ascending = False, inplace=True)                    

    tabledata = pd.concat([dataSA, dataProvince])
    tabledata.rename(columns={'province': 'Province/Country', 'confirmed': 'Cumulative Cases',
                     'daily_new': 'New Cases', 'deaths': 'Cumulative Deaths', 'daily_new_deaths': 'New Deaths',
                     'growth_factor': '7 Day Ave Growth Factor'}, inplace=True)
    

    return tabledata
    # fig.show()
    #plotly.offline.plot(fig, "file.html")