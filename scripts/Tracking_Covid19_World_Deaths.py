# Function to plot Covid 19 world deths
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.graph_objects as go
from datetime import timedelta, date



def plot_deaths (dfd, color_map):
    
    # from get_data import df

    case_threshold = 5 
    dfd = dfd.reset_index()
    dfd = dfd[['date', 'country', 'deaths']].sort_values('date')
       
    dfd = dfd.reset_index()
    # dfd = dfd[dfd['country'] != "South Africa Corrected"]
    dfd = (dfd.assign(daily_new=dfd.groupby('country', as_index=False)[['deaths']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))

    dfd = (dfd.assign(avg_daily_new=dfd.groupby('country', as_index=False)[['daily_new']]
                                    .rolling(7).mean()
                                    .reset_index(0, drop=True)))

   
    dfd['day'] = dfd.date.apply(lambda x: x.date()).apply(str)
    dfd = dfd.sort_values(by='day')
    dfd = dfd[dfd.deaths >= case_threshold]

    days = dfd.day.unique().tolist()
    countries = dfd.country.unique().tolist()
    countries.sort()

    max_axis = dfd.deaths.max()

    #Make a plot
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    #fig_dict["layout"]["height"] = 640
    # fig_dict["layout"]["width"] = 1000
    fig_dict["layout"]["title"] = {"text": "<b>Seven Day Average Rate of Change in COVID19 Related Deaths vs Cumulative Total Deaths<b>",
                                    'y':0.90,'x':0.5,'xanchor': 'center','yanchor': 'top'}
    fig_dict["layout"]["titlefont"] = {'size': 16}                               
    fig_dict["layout"]["xaxis"] = {"range": [np.log10(case_threshold), np.log10(dfd['deaths'].max() *1.2)], 
                                    "title": "Total Deaths (log scale)", "type": "log", "showline": True}
    fig_dict["layout"]["yaxis"] = {"range": [np.log10(case_threshold/10), np.log10(dfd['avg_daily_new'].max() *1.2)], 
                                    "title": "Seven (7) Day Average Of Daily Deaths (log scale)", "type": "log", "showline": True}
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
    for country in countries:
        dataset_by_day = dfd[dfd["day"] <= day]
        dataset_by_day_and_country = dataset_by_day[ dataset_by_day["country"]==country ]
        color = color_map[country]
        data_dict = {
            "x": list(dataset_by_day_and_country["deaths"]),
            "y": list(dataset_by_day_and_country["avg_daily_new"]),
            "mode": "lines",
            "line": {"color": color},
            "text": dataset_by_day_and_country[['deaths', 'avg_daily_new']],
            "name": country,
            'hoverlabel': {'namelength': 0},
            'hovertemplate': '<b>%{hovertext}</b><br>Deaths: %{x:,d}<br>Average Daily: %{y:,.0f}',
            'hovertext': dataset_by_day_and_country['country']
        }
        fig_dict["data"].append(data_dict)

        dataset_by_current_day = dfd[dfd["day"] == day]
        dataset_by_current_day_and_country = dataset_by_current_day[ dataset_by_current_day["country"]==country ]
        data_dict2 = {
            "x": list(dataset_by_current_day_and_country["deaths"]),
            "y": list(dataset_by_current_day_and_country["avg_daily_new"]),
            "mode": "markers+text",
            "marker": {"color": color,"size":12}, 
            "cliponaxis": False,
            "text": dataset_by_current_day_and_country[["country"]],
            "textposition": "middle right",
            "textfont": {"size":16,"color":color}, 
            "name": country,
            'hoverlabel': {'namelength': 0},
            'hovertemplate': '<b>%{hovertext}</b><br>Deaths: %{x:,d}<br>Average Daily: %{y:,.0f}',
            'hovertext': dataset_by_day_and_country['country']
        }
        fig_dict["data"].append(data_dict2)


    # make frames
    for day in days:
        frame = {"data": [], "name": day}
        for country in countries:
            color = color_map[country]
            dataset_by_day = dfd[dfd["day"] <= day]
            dataset_by_day_and_country = dataset_by_day[dataset_by_day["country"] == country]

            data_dict = {
                "x": list(dataset_by_day_and_country["deaths"]),
                "y": list(dataset_by_day_and_country["avg_daily_new"]),
                "mode": "lines",
                "line": {"color": color},
                "text": dataset_by_day_and_country[['deaths', 'avg_daily_new']],
                "name": country
            }
            
            frame["data"].append(data_dict)

            dataset_by_current_day = dfd[dfd["day"] == day]
            dataset_by_current_day_and_country = dataset_by_current_day[dataset_by_current_day["country"] == country]

            data_dict2 = {
            "x": list(dataset_by_current_day_and_country["deaths"]),
            "y": list(dataset_by_current_day_and_country["avg_daily_new"]),
            "mode": "markers+text",
            "marker": {"color": color, "size":12},
             "cliponaxis": False,
            "text": dataset_by_current_day_and_country[["country"]],
            "textposition": "middle right",
            "textfont": {"size":16, "color":color},
            "name": country
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

    fig.add_shape(dict(
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
            ))

    fig.add_annotation(dict(
                x=math.log10(20000),
                y=math.log10(2000),
                xref='x',
                yref='y',
                text="10:1 Ratio",
                font=dict(color="LightGrey"),
                arrowcolor="LightGrey"
            ))
    fig.add_annotation(text='Based on COVID Data Repository by Johns Hopkins CSSE ({})\nBy Carl Steyn'.format(day), 
        x=1, y=-0.30, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
        yanchor='auto', xshift=0, yshift=0)
        
    return fig