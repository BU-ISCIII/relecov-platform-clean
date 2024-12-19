# Generic imports
import os
import json
import pandas as pd
import plotly.express as px
from dash import dcc, html
from django_plotly_dash import DjangoDash

# Local imports
from relecov_platform import settings as relecov_platform_settings
import core.utils.rest_api
import dashboard.models

def create_samples_received_map():
    geojson_file = os.path.join(
        relecov_platform_settings.STATIC_ROOT,
        "dashboard",
        "custom",
        "map",
        "spain-communities.geojson",
    )
    with open(geojson_file, encoding="utf-8") as geo_json:
        counties = json.load(geo_json)
    json_data = dashboard.utils.generic_graphic_data.get_graphic_json_data(
        "received_samples_map"
    )
    if json_data is None:
        # Execute the pre-processed task to get the data
        result = dashboard.utils.generic_process_data.pre_proc_samples_received_map()
        if "ERROR" in result:
            return result
        json_data = dashboard.utils.generic_graphic_data.get_graphic_json_data(
            "received_samples_map"
        )

    ldata = pd.DataFrame(json_data)

    fig = px.choropleth_mapbox(
        ldata,
        geojson=counties,
        locations=ldata.ccaa_id,
        color=ldata.samples,
        color_continuous_scale="Viridis",
        range_color=ldata.ccaa_name,
        mapbox_style="carto-positron",
        zoom=3.8,
        center={"lat": 35.9, "lon": -5.3},
        opacity=0.5,
        labels={
            "ccaa_name": "CCAA",
            "samples": "SAMPLES",
        },
        custom_data=[
            "samples",
        ],
        hover_name="ccaa_name",
        hover_data={"ccaa_id": False},
    )
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    # Don't show legend in plotly.express
    fig.update_traces(showlegend=False)
    app = DjangoDash("samplesReceivedOverTimeMap")
    app.layout = html.Div(
        children=[
            dcc.Graph(className="card", id="geomap-per-lineage", figure=fig),
        ],
    )
