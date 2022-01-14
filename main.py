import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import date, timedelta


# Initialize app -------------------------------------------------------------
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], )
app.title = "Covid 19 data"
server = app.server

# ######################## Load  data ##########################################################################
# data from 'our world in Data'
dataframeGlobal = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')

# select data which wants to be shown
columnsList = ['total_cases_per_million', 'new_cases_smoothed_per_million',
              'total_deaths_per_million', 'total_vaccinations_per_hundred',
              'people_fully_vaccinated_per_hundred','icu_patients_per_million',
              ]

# Indroduction for User in web app
explanation = "Select a location with the dropdown. More than one country can be selected and the data can be compared.\n" \
              "The data can be selected with the data dropdown. Here only one selection can be made. The data will always be shown until" \
              " yesterday which is the most up to date data. "

# get the actual date
today = str(date.today() - timedelta(1))

# Layout of Dash App the css files are placed in ../assets
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns user-controls",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src=app.get_asset_url("oth-logo.png"),
                            ),
                            href="https://www.oth-regensburg.de",
                        ),
                        html.H2("Covid - 19 Dashboard"),
                        html.P(
                            explanation
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
                                            value=['Germany'],
                                            multi=True,
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
                        dcc.Markdown(
                            """
                            Source: [Github](https://github.com/FabianHeu/DataScienceProject)
                            """
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns worldmap and graph",
                    children=[
                        dcc.Graph(id="worldmap"),
                        dcc.Graph(id="graph"),
                    ],
                ),
            ],
        )
    ]
)

# call back to update the worldmap
@app.callback(
    Output(component_id="worldmap", component_property="figure"),
    Input(component_id="location-dropdown", component_property="value"),
    Input(component_id="data-dropdown", component_property="value"),

)
def update_worldmap(location, data):
    dataframeFiltered = dataframeGlobal[dataframeGlobal.date.eq(today)]
    worldmap = px.choropleth(
        data_frame=dataframeFiltered,
        locations='iso_code',
        hover_name='location',
        color=data,
        color_continuous_scale=px.colors.sequential.Viridis,

    )
    worldmap.update_layout(
        showlegend=False,
        margin=dict(t=0, l=0, b=0, r=0),
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        dragmode=False,
    )
    worldmap.update_geos(
        showlakes=False,
        visible=False,
    )

    return worldmap


# call back to update the graph
@app.callback(
    Output(component_id="graph", component_property="figure"),
    Input(component_id="data-dropdown", component_property="value"),
    Input(component_id="location-dropdown", component_property="value")
)
def update_graph(dataSelection, country):
    graph = px.line(
        data_frame=dataframeGlobal.loc[dataframeGlobal['location'].isin(list(country))],
        x='date',
        y=dataSelection,
        color="location",
        line_group='location',
    )
    graph.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, l=0, b=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showline=False,
            zeroline=False,
            showgrid=False,
            title='',
            tickfont=dict(size=15, family='verdana', color='rgba(0,162,137,100)'),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            titlefont=dict(size=15, family='verdana', color='rgba(0,162,137,100)'),
            tickfont=dict(size=15, family='verdana', color='rgba(0,162,137,100)'),
        ),
    )
    return graph


if __name__ == "__main__":
    app.run_server(debug=True)
