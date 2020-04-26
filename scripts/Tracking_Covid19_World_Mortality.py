# Bar plot for mortality rate
import math

import pandas as pd
import numpy as np

from datetime import datetime

import plotly.graph_objects as go
from datetime import timedelta, date

def plot_mortality(dfm, color_map):
    
    case_threshold = 100
    dfm = dfm[dfm['confirmed']>=case_threshold]
    dfm.loc[:,"mortality"] = dfm["deaths"]/dfm['confirmed']*100
     

    dfm = dfm.reset_index()
    dfm = dfm[['date', 'country', 'mortality']].sort_values('country')
    dfm = dfm.reset_index()
    ave_mortality = dfm.mortality.median()

    dfm['mortality'] = dfm.mortality.fillna(0)

    #Documentation for make_bar_chart_function

    '''
        This function can be used with a dataset whose one column
        is categorical for which bar chart is required and other columns
        are various years which will serve as a frame rate.
    '''
    start_date = dfm.date.min()
    end_date =dfm.date.max()  

    ave_mortality = dfm[dfm['date']==end_date].mortality.median()

    countries = dfm.country.unique().tolist()
    
    max_axis = dfm.mortality.max()

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    listOfFrames = []
    for day in daterange(start_date,end_date+timedelta(days=1)):
        dataset_by_day = dfm[dfm["date"] == day]
        dataset_by_day_sort=dataset_by_day.sort_values(by='mortality')
        dataset_by_day_sort["color"] = dataset_by_day_sort["country"].apply(lambda x: color_map.get(x))
        
        listOfFrames.append(go.Frame(dict(data = [go.Bar(dict(x = dataset_by_day_sort["mortality"], y = dataset_by_day_sort["country"],
                                                    marker_color = dataset_by_day_sort["color"], orientation='h',
                                                    text = dataset_by_day_sort["country"],
                                                    hoverinfo = "none",textposition = "outside",
                                                    texttemplate = "%{x:,.1f}<br>%{y}",cliponaxis = False))], 
                                        layout = go.Layout(dict(
                                            font = {"size":12},
                                            #height = 640,
                                            # width = 1000,
                                            xaxis = {"showline":True,"visible":True, "dtick": 1, 
                                            "showgrid":True,"zeroline":True, "range":[0, max_axis], "title": "Mortality Rate %"},
                                            yaxis = {"showline":True, "visible":False},
                                            title = "Mortality Rate For: "+ datetime.strftime(day, "%Y-%m-%d"),
                                            titlefont={"size":22})))))

    end_data = dfm[dfm["date"]==end_date].sort_values(by='mortality')
    end_data["color"] = end_data["country"].apply(lambda x: color_map.get(x))

    fig = go.Figure(dict(
            data = [go.Bar(dict(x = end_data["mortality"], y = end_data["country"],
                    marker_color = end_data["color"],text = end_data["country"], orientation='h',
                    hoverinfo = "none",textposition = "outside",
                    texttemplate = "%{x:,.1f}<br>%{y}",cliponaxis = False ))],
            layout=go.Layout(dict(
                title="Mortality Rate For: "+ datetime.strftime(end_date, "%Y-%m-%d"),
                titlefont={"size":22},
                font = {"size":12},
                height = 600,
                width = 1000,
                xaxis = {"showline":True, "visible":True, "range":[0, max_axis],
                "showgrid":True,"zeroline":True, "title": "Mortality Rate %", "dtick": 1},
                yaxis = {"showline":True, "visible":False},
                updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                            method="animate",
                            args=[None])])]
                )),
            frames=list(listOfFrames)
            ))
    fig.add_annotation(dict(text='Based on COVID Data Repository by Johns Hopkins CSSE ({})\nBy Carl Steyn'.format(dfm.date.max().strftime('%B %d, %Y')), 
        x=1, y=-0.18, xref="paper", yref="paper", font=dict(color="LightGrey"), showarrow=False, xanchor='right', 
        yanchor='auto', xshift=0, yshift=0))
    # Line reference to the axes
    fig.add_shape(dict(   
            type="line",
            x0=ave_mortality,
            y0=-0.5,
            x1=ave_mortality,
            y1=len(countries),
            line=dict(
                color="Grey",
                width=2,
                dash="dash"
            )
        ))
    
    fig.add_annotation(dict(
            x=ave_mortality,
            y=1,
            xref='x',
            yref='y',
            text= ("Median Mortality Rate<br>for countries selected:  "+ str(round(ave_mortality,1))),
            font=dict(color="Grey"),
            arrowcolor="Grey",
            xanchor="left",
            ax=ave_mortality+0.8,
            ay=1.5
        )) 
    fig.update_layout(template= 'plotly_white', autosize=True)
    
    return fig
    #  fig.show()
   




