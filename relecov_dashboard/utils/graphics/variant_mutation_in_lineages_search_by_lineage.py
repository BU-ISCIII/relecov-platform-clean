# Generic imports
import dash_bio as dashbio
from dash import dcc, html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash

# Local imports
import relecov_core.models
import relecov_dashboard.utils.generic_functions
import relecov_dashboard.utils.pre_processing_data


def get_variant_data_from_lineages(graphic_name=None, lineage=None, chromosome=None):
    json_data = relecov_dashboard.utils.generic_functions.get_graphic_json_data(
        graphic_name
    )

    if json_data is None:
        # Execute the pre-processed task to get the data
        result = (
            relecov_dashboard.utils.pre_processing_data.pre_proc_variations_per_lineage(
                chromosome
            )
        )
        if "ERROR" in result:
            return result

    json_data = relecov_dashboard.utils.generic_functions.get_graphic_json_data(
        graphic_name
    )
    # Return None to indicate that there is no data stored yet
    if not json_data:
        return None, None
    #    if not LineageValues.objects.filter(
    #        lineage_fieldID__property_name__iexact="lineage_name"
    #    ).exists():
    #        return None

    if lineage is None:
        lineage = (
            relecov_core.models.LineageValues.objects.filter(
                lineage_fieldID__property_name__iexact="lineage_name"
            )
            .values_list("value", flat=True)
            .first()
        )

    mdata = json_data[lineage]

    return mdata, lineage


def create_needle_plot_graph_mutation_by_lineage(lineage_list, lineage, mdata):
    options = []
    for lin in lineage_list:
        options.append({"label": lin, "value": lin})

    app = DjangoDash("needlePlotMutationByLineage")

    app.layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            "Show or hide range slider",
                            dcc.Dropdown(
                                id="needleplot-rangeslider",
                                options=[
                                    {"label": "Show", "value": 1},
                                    {"label": "Hide", "value": 0},
                                ],
                                clearable=False,
                                multi=False,
                                value=1,
                                style={"width": "150px", "margin-right": "30px"},
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            "Select a Lineage",
                            dcc.Dropdown(
                                id="needleplot-select-lineage",
                                options=options,
                                clearable=False,
                                multi=False,
                                value=lineage,
                                style={"width": "150px"},
                            ),
                        ]
                    ),
                ],
                style={
                    "display": "flex",
                    "justify-content": "start",
                    "align-items": "flex-start",
                },
            ),
            html.Div(
                children=dashbio.NeedlePlot(
                    width="auto",
                    id="dashbio-needleplot",
                    mutationData=mdata,
                    rangeSlider=True,
                    xlabel="Genome Position",
                    ylabel="Population Allele Frequency ",
                    domainStyle={
                        # "textangle": "45",
                        "displayMinorDomains": False,
                    },
                ),
            ),
        ]
    )

    @app.callback(
        Output("dashbio-needleplot", "mutationData"),
        Output("dashbio-needleplot", "lineage"),
        Input("needleplot-select-lineage", "value"),
    )
    def update_sample(selected_lineage):
        mdata, lineage = get_variant_data_from_lineages(
            graphic_name="variations_per_lineage",
            lineage=selected_lineage,
            chromosome=None,
        )
        return mdata, lineage

    @app.callback(
        Output("dashbio-needleplot", "rangeSlider"),
        Input("needleplot-rangeslider", "value"),
    )
    def update_range_slider(range_slider_value):
        return True if range_slider_value else False
