# Function to plot confirmed cases
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta, date

# from get_data import df_both
def plot_daily_deaths (dfn, color_map):
    
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
    dfn = dfn[dfn.confirmed > case_threshold]

    days = dfn.day.unique().tolist()
    countries = dfn.country.unique().tolist()
    countries.sort()
    countries_length = len(countries)
    row_length = math.ceil(countries_length/4)
    #max_axis = dfn.confirmed.max()
    fig = make_subplots(cols = 4, rows=row_length,
                                  # vertical_spacing=0.05,
                                 subplot_titles=countries) 
    #Make a plot
    fig.update_layout(height=600, width=1000,
                  title_text="<b>Daily New Confirmed Covide-19 Infections<b>",
                  titlefont={'size': 20}, 
                  hovermode="closest",
                  title_xanchor= 'center',
                  title_yanchor= 'bottom',
                  title_xref= "container",
                  title_x= 0.5,
                  title_y=0.90 )
    # fig_dict = {
    #     "data": [],
    #     "layout": {}
    # }

    # # fill in most of layout
    # fig_dict["layout"]["height"] = 600
    # fig_dict["layout"]["width"] = 1000
    # fig_dict["layout"]["title"] = {"text": "<b>Daily New Confirmed Covide-19 Infections<b>",
    #                                 'y':0.90,'x':0.5,'xanchor': 'center','yanchor': 'top'}
    # fig_dict["layout"]["titlefont"] = {'size': 16}                               
    # fig_dict["layout"]["hovermode"] = "closest"


    fig.update_layout(template= 'plotly_white', showlegend=False)
    # make data
    xloc = 1
    yloc = 0
    #max_day = max(days)
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
                mode='lines', marker_color=color),
                row=xloc, col=yloc)
    fig.update_xaxes(tickformat = '%d/%m', tickfont=dict(size=8), tickangle=0, nticks=5)
    fig.update_yaxes(tickfont=dict(size=9))

      
   
    fig.add_annotation(text='Based on COVID Data Repository by Johns Hopkins CSSE ({})\nBy Carl Steyn'.format(max(days)), 
    x=1, y=-0.1, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
    yanchor='auto', xshift=0, yshift=0)
    #fig.update_layout(showlegend=True)

    
    return fig
    # fig.show()
    #plotly.offline.plot(fig, "file.html")
