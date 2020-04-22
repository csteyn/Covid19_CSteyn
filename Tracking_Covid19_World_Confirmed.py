# Function to plot confirmed cases
import math
import pandas as pd
import numpy as np

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta, date

# from get_data import df_both
def plot_confirmed (dfc, color_map):
    
    case_threshold = 100

    dfc = dfc.reset_index()
    dfc = dfc[['date', 'country', 'confirmed']].sort_values('date')
    dfc = dfc.reset_index()

    dfc = (dfc.assign(daily_new=dfc.groupby('country', as_index=False)[['confirmed']]
                                .diff().fillna(0)
                                .reset_index(0, drop=True)))

    dfc = (dfc.assign(avg_daily_new=dfc.groupby('country', as_index=False)[['daily_new']]
                                    .rolling(7).mean()
                                    .reset_index(0, drop=True)))


    dfc['day'] = dfc.date.apply(lambda x: x.date()).apply(str)
    dfc = dfc.sort_values(by='day')
    dfc = dfc[dfc.confirmed > case_threshold]

    days = dfc.day.unique().tolist()
    countries = dfc.country.unique().tolist()
    countries.sort()

    max_axis = dfc.confirmed.max()

    #Make a plot
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    fig_dict["layout"]["height"] = 600
    fig_dict["layout"]["width"] = 1000
    fig_dict["layout"]["title"] = {"text": "<b>Seven Day Average Rate of Change of New Confirmed Covide-19 Infections vs Cumulative Total<b>",
                                    'y':0.90,'x':0.5,'xanchor': 'center','yanchor': 'top'}
    fig_dict["layout"]["titlefont"] = {'size': 16}                               
    fig_dict["layout"]["xaxis"] = {"range": [np.log10(case_threshold), np.log10(dfc['confirmed'].max() *1.3)], 
                                   "title": "Total Confirmed Cases (log scale)", "type": "log", "showline": True}
    fig_dict["layout"]["yaxis"] = {"range": [np.log10(case_threshold/10), np.log10(dfc['avg_daily_new'].max() *1.3)], 
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
    for country in countries:
        dataset_by_day = dfc[dfc["day"] <= day]
        dataset_by_day_and_country = dataset_by_day[ dataset_by_day["country"]==country ]
        color = color_map[country]
        data_dict = {
            "x": list(dataset_by_day_and_country["confirmed"]),
            "y": list(dataset_by_day_and_country["avg_daily_new"]),
            "mode": "lines",
            "line": {"color": color},
            "text": dataset_by_day_and_country[['confirmed', 'avg_daily_new']],
            "name": country,
            'hoverlabel': {'namelength': 0},
            'hovertemplate': '<b>%{hovertext}</b><br>Confirmed: %{x:,d}<br>Average Daily: %{y:,.0f}',
            'hovertext': dataset_by_day_and_country['country']
        }
        fig_dict["data"].append(data_dict)

        dataset_by_current_day = dfc[dfc["day"] == day]
        dataset_by_current_day_and_country = dataset_by_current_day[ dataset_by_current_day["country"]==country ]
        data_dict2 = {
            "x": list(dataset_by_current_day_and_country["confirmed"]),
            "y": list(dataset_by_current_day_and_country["avg_daily_new"]),
            "mode": "markers+text",
            "marker": {"color": color,"size":12},
            "text": dataset_by_current_day_and_country[["country"]],
            "textposition": "middle right",
            "textfont": {"size":16, "color":color},
            "name": country,
            'hoverlabel': {'namelength': 0},
            'hovertemplate': '<b>%{hovertext}</b><br>Confirmed: %{x:,d}<br>Average Daily: %{y:,.0f}',
            'hovertext': dataset_by_day_and_country['country']
        }
        fig_dict["data"].append(data_dict2)


    # make frames
    for day in days:
        frame = {"data": [], "name": day}
        for country in countries:
            color = color_map[country]
            dataset_by_day = dfc[dfc["day"] <= day]
            dataset_by_day_and_country = dataset_by_day[dataset_by_day["country"] == country]

            data_dict = {
                "x": list(dataset_by_day_and_country["confirmed"]),
                "y": list(dataset_by_day_and_country["avg_daily_new"]),
                "mode": "lines",
                "line": {"color": color},
                "text": dataset_by_day_and_country[['confirmed', 'avg_daily_new']],
                "name": country
            }
            
            frame["data"].append(data_dict)

            dataset_by_current_day = dfc[dfc["day"] == day]
            dataset_by_current_day_and_country = dataset_by_current_day[dataset_by_current_day["country"] == country]

            data_dict2 = {
            "x": list(dataset_by_current_day_and_country["confirmed"]),
            "y": list(dataset_by_current_day_and_country["avg_daily_new"]),
            "mode": "markers+text",
            "marker": {"color": color, "size":12},
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
    # fig_dict['layout']['annotations'] = {"x": math.log(190000), "y": math.log(22000), "text": "10:1 Ratio",
    #                 "font": {"size": 20, "color": "LightGray"}}
    fig = go.Figure(fig_dict)
    fig.update_layout(template= 'plotly_white', showlegend=False)
        
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
                x=math.log10(250000),
                y=math.log10(25000),
                xref='x',
                yref='y',
                text="10:1 Ratio",
                font=dict(color="LightGrey"),
                arrowcolor="LightGrey"
            )
    fig.add_annotation(text='Based on COVID Data Repository by Johns Hopkins CSSE ({})\nBy Carl Steyn'.format(day), 
        x=1, y=-0.34, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
        yanchor='auto', xshift=0, yshift=0)
    #fig.update_layout(showlegend=True)

    
    return fig
    # fig.show()
    #plotly.offline.plot(fig, "file.html")