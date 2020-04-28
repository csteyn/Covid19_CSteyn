# Function to plot confirmed cases
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta, date

# from get_data import df_both
def plot_daily_confirmed (dfn, color_map):
    
    case_threshold = 100

    dfn = dfn.reset_index()
    dfn = dfn[['date', 'country', 'confirmed']].sort_values('date')
    dfn = dfn.reset_index()

    dfn = (dfn.assign(daily_new=dfn.groupby('country', as_index=False)[['confirmed']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))

    dfn = (dfn.assign(avg_daily_new=dfn.groupby('country', as_index=False)[['daily_new']]
                                    .rolling(2).mean()
                                    .reset_index(0, drop=True)))


    dfn['day'] = dfn.date.apply(lambda x: x.date()).apply(str)
    dfn = dfn.sort_values(by='day')
    dfn = dfn[dfn.confirmed >= case_threshold]

    days = dfn.day.unique().tolist()
    countries = dfn.country.unique().tolist()
    countries.sort()
    countries_length = len(countries)
    row_length = math.ceil(countries_length/4)

    fig = make_subplots(cols = 4, rows=row_length,
                                  # vertical_spacing=0.05,
                                 subplot_titles=countries) 
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

    for country in countries:
        yloc+=1
        if yloc == 5:
            yloc =1
            xloc+=1
        dataset_country = dfn[dfn["country"]==country]
        color = color_map[country]
        fig.append_trace(go.Bar(x=dataset_country['day'],y=dataset_country['daily_new'],name=country, 
                marker_color=color), 
                row=xloc, col=yloc)
        fig.append_trace(go.Scatter(x=dataset_country['day'],y=dataset_country['avg_daily_new'], name=country, 
                mode='lines', marker_color='lightgrey'),
                row=xloc, col=yloc)
        if country in ["South Africa", "South Africa Corrected"]:
            fig.add_shape(dict(   
            type="line",
            x0='2020-03-28',
            y0=0,
            x1='2020-03-28',
            y1=max(dataset_country['daily_new']),
            line=dict(
                color="LightGrey",
                width=2,
                dash="dash"
                ) 
            ), row=xloc, col=yloc)
    
            fig.add_annotation(dict(
                    x='2020-03-28',
                    y=max(dataset_country['daily_new']*0.6),
                    xref='x',
                    yref='y',
                    text= ("Lockdown Starts"),
                    font=dict(color="LightGrey"),
                    arrowcolor="LightGrey",
                    xanchor="left"            
                ), row=xloc, col=yloc) 

    fig.update_xaxes(tickformat = '%d/%m', tickfont=dict(size=8), tickangle=0, nticks=5)
    fig.update_yaxes(tickfont=dict(size=9))

      
   
    fig.add_annotation(text='Based on COVID Data Repository by Johns Hopkins CSSE ({})\nBy Carl Steyn'.format(max(days)), 
    x=1, y=-0.14, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
    yanchor='auto', xshift=0, yshift=0)
    
    return fig
    # fig.show()
    #plotly.offline.plot(fig, "file.html")