# Function to plot confirmed cases
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta, date

# from get_data import df_both
def plot_daily_confirmed_province (dfn, color_mapSA):
    
    case_threshold = 1

    dfn = dfn.reset_index()
    dfn = dfn[['date', 'province', 'confirmed']].sort_values('date')
    dfn = dfn[dfn['province'] != 'Unknown']
    dfn = dfn.reset_index()

    dfn = (dfn.assign(daily_new=dfn.groupby('province', as_index=False)[['confirmed']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))

    dfn = (dfn.assign(avg_daily_new=dfn.groupby('province', as_index=False)[['daily_new']]
                                    .rolling(2).mean()
                                    .reset_index(0, drop=True)))


    dfn['day'] = dfn.date.apply(lambda x: x.date()).apply(str)
    dfn = dfn.sort_values(by='day')
    dfn = dfn[dfn.confirmed >= case_threshold]

    days = dfn.day.unique().tolist()
    provinces = dfn.province.unique().tolist()
    provinces.sort()
    province_length = len(provinces)
    row_length = math.ceil(province_length/3)

    fig = make_subplots(cols = 3, rows=row_length,
                                  # vertical_spacing=0.05,
                                 subplot_titles=provinces) 
    #Make a plot
    fig.update_layout(#height=640,# width=1000,
                  title_text="<b>Daily New Confirmed COVID19 Infections<b>",
                  titlefont={'size': 20}, 
                  hovermode="closest",
                  title_xanchor= 'center',
                  title_yanchor= 'bottom',
                  title_xref= "container",
                  title_x= 0.5,
                  title_y=0.90,
                  autosize=True)


    fig.update_layout(template= 'plotly_white', showlegend=False)
    # make data
    xloc = 1
    yloc = 0

    for province in provinces:
        yloc+=1
        if yloc == 4:
            yloc =1
            xloc+=1
        dataset_province = dfn[dfn["province"]==province]
        color = color_mapSA[province]
        fig.append_trace(go.Bar(x=dataset_province['day'],y=dataset_province['daily_new'],name=province, 
                marker_color=color), 
                row=xloc, col=yloc)
        fig.append_trace(go.Scatter(x=dataset_province['day'],y=dataset_province['avg_daily_new'], name=province, 
                mode='lines', marker_color='lightgrey'),
                row=xloc, col=yloc)
       
        fig.add_shape(dict(   
        type="line",
        x0='2020-03-28',
        y0=0,
        x1='2020-03-28',
        y1=max(dataset_province['daily_new']),
        line=dict(
            color="LightGrey",
            width=2,
            dash="dash"
            ) 
        ), row=xloc, col=yloc)

        fig.add_annotation(dict(
                x='2020-03-28',
                y=max(dataset_province['daily_new']*0.7),
                xref='x',
                yref='y',
                text= ("Lockdown Starts"),
                font=dict(color="LightGrey"),
                arrowcolor="LightGrey",
                xanchor="left"            
            ), row=xloc, col=yloc) 

    fig.update_xaxes(tickformat = '%d/%m', tickfont=dict(size=8), tickangle=0, nticks=5)
    fig.update_yaxes(tickfont=dict(size=9))

      
   
    fig.add_annotation(text='Based on COVID Data Repository by the University of Pretoria ({})\nBy Carl Steyn'.format(max(days)), 
    x=1, y=-0.14, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
    yanchor='auto', xshift=0, yshift=0)
    
    return fig
