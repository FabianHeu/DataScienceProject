import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly import graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime


# Initialize app -------------------------------------------------------------
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], )
app.title = "Covid 19 vaccination data"
server = app.server

# ######################## Load my own data ###################################################################
# data from 'our world in Data'
dataframeGlobal = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
columnsList = dataframeGlobal.columns
dataframeFiltered = dataframeGlobal[dataframeGlobal.date.eq('2021-12-16')]
dfNZ = dataframeGlobal[dataframeGlobal['location'] == 'New Zealand']

# #############################################################################################################

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src=app.get_asset_url("oth-logo.png"),
                            ),
                            href="https://www.oth-regensburg.de",
                        ),
                        html.H2("Covid -19 Dashboard"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=datetime(2020, 1, 1),
                                    max_date_allowed=datetime(2021, 9, 30),
                                    initial_visible_month=datetime(2020, 1, 1),
                                    date=datetime(2020, 1, 1).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[{'label': i, 'value': i} for i in dataframeGlobal['location'].unique()],
                                            placeholder="Select a location",
                                            value='Germany'

                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="data-dropdown",
                                            options=[{'label': i, 'value': i} for i in columnsList],
                                            multi=False,
                                            placeholder="Select data",
                                            value='total_cases_per_million'
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
                        dcc.Markdown(
                            """
                            Source: [Github](https://github.com/FabianHeu/DataScienceProject)
                            """
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="worldmap"),
                        dcc.Graph(id="graph"),
                    ],
                ),
            ],
        )
    ]
)

@app.callback(
    Output(component_id="worldmap", component_property="figure"),
    Input(component_id="location-dropdown", component_property="value")
)
def update_worldmap(selected):
    worldmap = px.choropleth(
        locations=dataframeFiltered['iso_code'],
        z=np.log(dataframeFiltered['male_smokers']),
        text=dataframeFiltered['location'],
        hoverinfo="text",
        marker_line_color='white',
        autocolorscale=False,
        reversescale=True,
        colorscale="Viridis",
        marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
        colorbar={"thickness": 10, "len": 0.3, "x": 0.9, "y": 0.7,
                  'title': {"text": 'persons', "side": "bottom"}, 'tickvals': [2, 10],
                  'ticktext': ['100', '100,000']})
    return {
        "data": [worldmap],
        "layout": go.Layout(
            autosize=False,
            geo={'showframe': False,
                 'showcoastlines': True,
                 'projection': {'type': "miller"},
                 'bgcolor': 'rgba(0,0,0,0)',
                 # 'center': {"lat": 37.0902, "lon": -95.7129}
                 },
            paper_bgcolor='rgba(0,0,0,0)',
            width=400,
            margin=dict(l=0, r=0, t=0, b=0),
        )
    }


@app.callback(
    Output(component_id="graph", component_property="figure"),
    Input(component_id="data-dropdown", component_property="value"),
    Input(component_id="location-dropdown", component_property="value")
)
def update_selection(data, country):
    graph = px.area(
        data_frame=dataframeGlobal[dataframeGlobal['location'] == country],
        x='date',
        y=data,
    )
    graph.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, l=0, b=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showline=False,
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
        ),
    )
    return graph


if __name__ == "__main__":
    app.run_server(debug=True)
