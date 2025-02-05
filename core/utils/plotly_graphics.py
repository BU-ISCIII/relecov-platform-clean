# Generic imports
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from dash_bio import NeedlePlot
from dash import dcc, html
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output


def bar_graphic(data, col_names, legend, yaxis, options):
    """Options fields are: title, height"""
    if "colors" in options:
        colors = options["colors"]
    else:
        colors = ["#0099ff", "#1aff8c", "#ffad33", "#ff7733", "#66b3ff", "#66ffcc"]
    fig = go.Figure()
    for idx in range(1, len(col_names)):
        fig.add_trace(
            go.Bar(
                x=data[col_names[0]],
                y=data[col_names[idx]],
                name=legend[idx - 1],
                marker_color=colors if "colors" in options else colors[idx - 1],
            )
        )

    # Customize aspect
    fig.update_traces(
        marker_line_color="rgb(8,48,107)",
        marker_line_width=1.5,
        opacity=0.6,
    )
    fig.update_layout(
        title=options["title"],
        title_font_color="green",
        title_font_size=20,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45,
        yaxis=yaxis,
        margin=dict(l=0, r=0, t=30, b=0),
        height=options["height"],
    )
    if "xaxis_tics" in options:
        fig.update_layout(xaxis=options["xaxis"])

    plot_div = plot(fig, output_type="div", config={"displaylogo": False})

    return plot_div


def line_graphic(x_data, y_data, options):
    # Create line
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode="lines", name="lines"))

    fig.update_layout(
        height=options["height"],
        width=options["width"],
        xaxis_title=options["x_title"],
        yaxis_title=options["y_title"],
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=options["title"],
        title_font_color="green",
        title_font_size=20,
    )
    if "xaxis" in options:
        fig.update_layout(xaxis=options["xaxis"])
    plot_div = plot(fig, output_type="div", config={"displaylogo": False})
    return plot_div


def histogram_graphic(data, col_names, options):
    graph = px.bar(
        data, y=col_names[1], x=col_names[0], text_auto=True, width=options["width"]
    )
    # Customize aspect
    graph.update_traces(
        marker_color="rgb(158,202,225)",
        marker_line_color="rgb(8,48,107)",
        marker_line_width=1.5,
        opacity=0.6,
    )
    graph.update_layout(
        title=options["title"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45,
        margin=dict(l=20, r=40, t=30, b=20),
    )

    plot_div = plot(graph, output_type="div", config={"displaylogo": False})
    return plot_div


def gauge_graphic(data):
    graph = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=data["value"],
            number={"suffix": "%"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Samples Analized in percentage"},
            gauge={"axis": {"range": [None, 100]}},
        )
    )
    graph.update_layout(margin=dict(t=20, b=10, l=20, r=30))
    plot_div = plot(graph, output_type="div", config={"displaylogo": False})
    return plot_div


# FIXME: This function es never called within the platform
def bullet_graphic(value, title):
    point = str(value)
    top_value = int(value)
    data = [
        {
            "label": "Upload %",
            "range": [40, 70, 100],
            "performance": [40, top_value],
            "point": [point],
        }
    ]

    measure_colors = ["rgb(68, 107, 162)", "rgb(0, 153, 0)"]
    fig = ff.create_bullet(
        data,
        titles="label",
        title=title,
        markers="point",
        measures="performance",
        ranges="range",
        orientation="v",
        measure_colors=measure_colors,
        margin=dict(
            t=25,
            r=0,
            b=0,
            l=0,
        ),
    )
    fig.update_layout(height=450, width=330)
    plot_div = plot(fig, output_type="div")
    return plot_div


def pie_graphic(data, names, title, show_legend=False):
    colors = [
        "cyan",
        "red",
        "gold",
        "darkblue",
        "darkred",
        "magenta",
        "darkorange",
        "turquoise",
    ]
    fig = go.Figure(
        data=go.Pie(
            labels=names,
            values=data,
        )
    )
    fig.update_traces(
        title=title,
        title_font=dict(size=15, family="Verdana", color="darkgreen"),
        marker=dict(colors=colors, line=dict(color="black", width=1)),
    )
    fig.update_layout(
        height=350, width=270, showlegend=show_legend, margin=dict(t=0, b=0, l=0, r=0)
    )
    plot_div = plot(fig, output_type="div", config={"displaylogo": False})
    return plot_div


def needle_plot(m_data):
    """Create needleplot using dash-bio.
    Facing an issue when displaying name of domains. Names are outside graphic.
    """
    app = DjangoDash("sampleVariantGraphic")

    app.layout = html.Div(
        [
            "Show or hide range slider",
            dcc.Dropdown(
                id="default-needleplot-rangeslider",
                options=[{"label": "Show", "value": 1}, {"label": "Hide", "value": 0}],
                clearable=False,
                multi=False,
                value=1,
                style={"width": "400px"},
            ),
            NeedlePlot(
                id="dashbio-default-needleplot",
                mutationData=m_data,
                height=950,
                width=900,
                margin={"t": 100, "l": 40, "r": 20, "b": 20},
                domainStyle={
                    "displayMinorDomains": True,
                    # 'domainColor': ['#FFDD00', '#00FFDD', '#0F0F0F', '#D3D3D3']
                },
                rangeSlider=True,
                xlabel="Sequence of the proteins",
                ylabel="Number of Mutations",
            ),
        ]
    )

    @app.callback(
        Output("dashbio-default-needleplot", "rangeSlider"),
        Input("default-needleplot-rangeslider", "value"),
    )
    def update_needleplot(show_rangeslider):
        return True if show_rangeslider else False
