# Function to plot confirmed cases
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta, date

# from get_data import df_both
def plot_provinces_confirmed(dfp, color_mapSA):
    
    case_threshold = 10

    dfp= dfp.reset_index()
    dfp = dfp[['date', 'province', 'confirmed']].sort_values('date')
    dfp = dfp[dfp['province'] != 'Unknown']
    dfp = dfp.reset_index()

    dfp = (dfp.assign(daily_new=dfp.groupby('province', as_index=False)[['confirmed']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))

    dfp = (dfp.assign(avg_daily_new=dfp.groupby('province', as_index=False)[['daily_new']]
                                    .rolling(7).mean()
                                    .reset_index(0, drop=True)))


    dfp['day'] = dfp.date.apply(lambda x: x.date()).apply(str)
    dfp = dfp.sort_values(by='day')
    dfp = dfp[dfp.confirmed >= case_threshold]

    days = dfp.day.unique().tolist()
    provinces = dfp.province.unique().tolist()
    provinces.sort()
    lockdown=dfp[dfp['date']== "2020-03-28"]
    
    max_axis = dfp.confirmed.max()
    max_yaxis = dfp.avg_daily_new.max()
    #Make a plot
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    # fig_dict["layout"]["height"] = 640
    # fig_dict["layout"]["width"] = 1000
    fig_dict["layout"]["title"] = {"text": "<b>Seven Day Average Rate of Change of New Confirmed COVID19 Infections vs Cumulative Total<b>",
                                    'y':0.90,'x':0.5,'xanchor': 'center','yanchor': 'top'}
    fig_dict["layout"]["titlefont"] = {'size': 16}                               
    fig_dict["layout"]["xaxis"] = {"range": [np.log10(case_threshold), np.log10(dfp['confirmed'].max() *1.3)], 
                                   "title": "Total Confirmed Cases (log scale)", "type": "log", "showline": True}
    fig_dict["layout"]["yaxis"] = {"range": [np.log10(case_threshold/10), np.log10(dfp['avg_daily_new'].max() *1.3)], 
                                    "title": "Seven (7) Day Average Of Daily New Confirmed Cases (log scale)", "type": "log", "showline": True}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["sliders"] = {
        "args": [
            "transition", {
                "duration": 100,
                "easing": "cubic-in-out"
            }
        ],
        "initialValue": min(days),
        "plotlycommand": "animate",
        "values": days,
        "visible": True
    }

    # buttons
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 100, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 100,
                                                                        "easing": "linear"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 5, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.05,
            "xanchor": "right",
            "y": 0.05,
            "yanchor": "top"
        }
    ]

    # sliders
    sliders_dict = {
        "active": len(days)-1,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
    #         "prefix": "Date: ",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 100},
        "pad": {"b": 10, "t": 30},
        "len": 0.9,
        "x": 0.05,
        "y": 0,
        "steps": []
    }
    
    # make data
    day = max(days)
    for province in provinces:
        dataset_by_day = dfp[dfp["day"] <= day]
        dataset_by_day_and_province = dataset_by_day[dataset_by_day["province"]==province]
        color = color_mapSA[province]

        data_dict = {
            "x": list(dataset_by_day_and_province["confirmed"]),
            "y": list(dataset_by_day_and_province["avg_daily_new"]),            
            "mode": "lines",
            "line": {"color": color},
            "text": dataset_by_day_and_province[['confirmed', 'avg_daily_new']],
            "name": province,
            'hoverlabel': {'namelength': 0},
            'hovertemplate': '<b>%{hovertext}</b><br>Confirmed: %{x:,d}<br>Average Daily: %{y:,.0f}',
            'hovertext': dataset_by_day_and_province['province']
        }
        fig_dict["data"].append(data_dict)

        dataset_by_current_day = dfp[dfp["day"] == day]
        dataset_by_current_day_and_province = dataset_by_current_day[ dataset_by_current_day["province"]==province ]
        data_dict2 = {
            "x": list(dataset_by_current_day_and_province["confirmed"]),
            "y": list(dataset_by_current_day_and_province["avg_daily_new"]),
            "mode": "markers+text",
            "marker": {"color": color, "size": 10}, 
            "cliponaxis": False,
            "text": dataset_by_current_day_and_province[["province"]],
            "textposition": "middle right",
            "textfont": { "size": 14, "color":color}, 
            "name": province,
            'hoverlabel': {'namelength': 0},
            'hovertemplate': '<b>%{hovertext}</b><br>Confirmed: %{x:,d}<br>Average Daily: %{y:,.0f}',
            'hovertext': dataset_by_day_and_province['province']
        }
        fig_dict["data"].append(data_dict2)


    # make frames
    for day in days:
        frame = {"data": [], "name": day}
        for province in provinces:
            color = color_mapSA[province]
            dataset_by_day = dfp[dfp["day"] <= day]
            dataset_by_day_and_province = dataset_by_day[dataset_by_day["province"] == province]

            data_dict = {
                "x": list(dataset_by_day_and_province["confirmed"]),
                "y": list(dataset_by_day_and_province["avg_daily_new"]),
                "mode": "lines",
                "line": {"color": color},
                "text": dataset_by_day_and_province[['confirmed', 'avg_daily_new']],
                "name": province
            }
            
            frame["data"].append(data_dict)

            dataset_by_current_day = dfp[dfp["day"] == day]
            dataset_by_current_day_and_province = dataset_by_current_day[dataset_by_current_day["province"] == province]

            data_dict2 = {
            "x": list(dataset_by_current_day_and_province["confirmed"]),
            "y": list(dataset_by_current_day_and_province["avg_daily_new"]),
            "mode": "markers+text",
            "marker": {"color": color, "size": 10},
            "cliponaxis": False,
            "text": dataset_by_current_day_and_province[["province"]],
            "textposition": "middle right",
            "textfont": {"size": 14, "color":color},
            "name": province
            }
            frame["data"].append(data_dict2)

        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [day],
            {"frame": {"duration": 200, "redraw": True},
            "mode": "immediate",
            "transition": {"duration": 200, 'easing': 'linear'}}
        ],
            "label": day,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)
    fig.update_layout(template= 'plotly_white', showlegend=False, autosize=True)
        
    fig.add_shape(
            # Line reference to the axes
                type="line",
                x0=10,
                y0=1,
                x1=max_axis*10,
                y1=max_axis,
                line=dict(
                    color="LightGrey",
                    width=2,
                    dash="dash"
                )
            )

    fig.add_annotation(
                x=math.log10(900),
                y=math.log10(90),
                xref='x',
                yref='y',
                text="10:1 Ratio",
                font=dict(color="LightGrey"),
                arrowcolor="LightGrey"
            )
    fig.add_annotation(text='Based on COVID Data Repository by the University of Pretoria ({})\nBy Carl Steyn'.format(day), 
        x=1, y=-0.30, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
        yanchor='auto', xshift=0, yshift=0)
    

    return fig
