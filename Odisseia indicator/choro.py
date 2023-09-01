# -*- coding: utf-8 -*-

import json
import pandas as pd
import geopandas as gpd
import plotly
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
#C:/Users/pablo/Documents/IRD/src/
# Import data 
od = pd.read_csv('od_mean.csv', encoding='cp1252')
#od_mean = pd.read_csv('od_mean.csv', encoding='cp1252')
with open('order_mun.geojson') as json_data:
    mun_data = json.load(json_data)
    # Convert the GeoJSON data to a GeoDataFrame
mun = gpd.GeoDataFrame.from_features(mun_data['features'])
# Reproject to EPSG 3857 (Web Mercator)
mun.crs = 'epsg:3857'
mun = mun.set_index('CD_MUN')
#mun = gpd.read_file('order_mun.geojson')
#mun = mun.set_index('CD_MUN')
# mapbox token
mapbox_accesstoken = 'pk.eyJ1IjoicGFibG9iZXJpYWluIiwiYSI6ImNsbGdtaWYwNjEzNjEzZXFodnc5MDU3ODYifQ.45XStASb0dbFZMGU0yGTMw'

# This is the part to create plotly fig
########################################################
ods=od['NM_MUN'].str.title().tolist()
# Convert 'Year' to string as it will be used as text for the x-axis labels
#od['Year'] = od['Year'].astype(str)

pl_deep=[[0.0, 'rgb(253, 253, 204)'],
         [0.1, 'rgb(201, 235, 177)'],
         [0.2, 'rgb(145, 216, 163)'],
         [0.3, 'rgb(102, 194, 163)'],
         [0.4, 'rgb(81, 168, 162)'],
         [0.5, 'rgb(72, 141, 157)'],
         [0.6, 'rgb(64, 117, 152)'],
         [0.7, 'rgb(61, 90, 146)'],
         [0.8, 'rgb(65, 64, 123)'],
         [0.9, 'rgb(55, 44, 80)'],
         [1.0, 'rgb(39, 26, 44)']]

Types = ['Mortality_mean','DAP Person_mean','Amount of employed people_mean','% basic education_mean']    

trace1 = []    
    
# Municipalities order should be the same as "id" passed to location
for q in Types:
    trace1.append(go.Choroplethmapbox(
        geojson = mun.__geo_interface__,
        locations = od.CD_MUN,
        z = od[q].tolist(),
        colorscale = pl_deep,
        text = ods, 
        colorbar = dict(thickness=20, ticklen=3),
        marker_line_width=0, marker_opacity=0.7,
        visible=False,
        subplot='mapbox1',
        hovertemplate = "<b>%{text}</b><br><br>" +
                        "Value: %{z}<br>" +
                        "<extra></extra>")) # "<extra></extra>" means we don't display the info in the secondary box, such as trace id.
    
trace1[0]['visible'] = True

trace2 = []    
    
# Suburbs order should be the same as "id" passed to location
for q in Types:
    trace2.append(go.Bar(
        x=od[q],  # Using the data directly without sorting
        y=od['NM_MUN'].str.title().tolist(),
        xaxis='x2',
        yaxis='y2',
        marker=dict(
            color='rgba(91, 207, 135, 0.3)',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.5),
        ),
        visible=False,
        name='Top 10 suburbs with the highest {} median price'.format(q),
        orientation='h',
    ))
 
trace2[0]['visible'] = True


# Sydney latitude and longitude values
latitude = -7
longitude = -35

layout = go.Layout(
    title = {'text': 'Socio-economical indicators',
    		 'font': {'size':28, 
    		 		  'family':'Arial'}},
    autosize = True,
    
    mapbox1 = dict(
        domain = {'x': [0.3, 1],'y': [0, 1]},
        center = dict(lat=latitude, lon=longitude),
        accesstoken = mapbox_accesstoken, 
        zoom = 8),

    xaxis2={
        'zeroline': False,
        "showline": False,
        "showticklabels":True,
        'showgrid':True,
        'domain': [0, 0.25],
        'side': 'left',
        'anchor': 'x2',
    },
    yaxis2={
        'domain': [0.4, 0.9],
        'anchor': 'y2',
        'autorange': 'reversed',
    },
    margin=dict(l=20, r=20, t=70, b=70),
    width=1000,
    height=800,
    paper_bgcolor='rgb(204, 204, 204)',
    plot_bgcolor='rgb(204, 204, 204)',
)
layout.update(updatemenus=list([
    dict(x=0,
         y=1,
         xanchor='left',
         yanchor='middle',
         buttons=list([
             dict(
                 args=['visible', [True, False, False, False]],
                 label='Mortality',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, True, False, False]],
                 label='DAP - Pessoa Física',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, False, True, False]],
                 label='Amount of employed people',
                 method='restyle'
                 ),
             dict(
                 args=['visible', [False, False, False, True]],
                 label='% basic education',
                 method='restyle'
                )
            ]),
        )]))

fig=go.Figure(data=trace2 + trace1, layout=layout)
#####################################################################
# This is the part to initiate Dash app

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children=''),

    dcc.Graph(
        id='example-graph-1',
        figure=fig
    ),

    html.Div(children='''
        Data source from https://www.realestate.com.au/neighbourhoods @Dec 2019
    ''')
])
             

if __name__ == '__main__':
    app.run_server(debug=True)
