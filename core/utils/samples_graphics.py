# Local imports
import core.utils.plotly_graphics
import core.utils.rest_api
import core.utils.samples


def received_per_ccaa():
    """Fetch the data from LIMS and show them in a graphic bar"""
    raw_data = core.utils.rest_api.get_summarize_data("")
    if "ERROR" in raw_data:
        return raw_data

    data = {"x": [], "y": []}
    for key, value in raw_data["region"].items():
        data["x"].append(key)
        data["y"].append(value)

    return core.utils.plotly_graphics.bar_graphic(
        data=data,
        col_names=["x", "y"],
        legend=[""],
        yaxis={"title": "Number of samples"},
        options={"title": "", "height": 400},
    )


def received_per_lab():
    """Fetch the data from LIMS and show them in a graphic bar"""
    raw_data = core.utils.rest_api.get_summarize_data("")
    if "ERROR" in raw_data:
        return raw_data

    data = {"x": [], "y": []}
    for key, value in raw_data["laboratory"].items():
        data["x"].append(key)
        data["y"].append(value)

    return core.utils.plotly_graphics.bar_graphic(
        data=data,
        col_names=["x", "y"],
        legend=[""],
        yaxis={"title": "Number of samples"},
        options={"title": "", "height": 400, "colors": "#1aff8c"},
    )


def received_samples_graph():
    """Fetch the number of samples received in the plaftorm and show them"""
    r_data = core.utils.samples.get_all_recieved_samples_with_dates(accumulated=True)
    data = {"x": [], "y": []}
    for r_dat in r_data:
        for key, value in r_dat.items():
            data["x"].append(key)
            data["y"].append(value)
    options = {
        "height": 450,
        "width": 400,
        "lines": "Samples",
        "x_axis": "Dates",
        "y_axis": "Number of samples",
        "x_title": "Date",
        "y_title": "Number of samples",
        "title": "",
        "xaxis": {"type":"date", "range": [data["x"][0], data["x"][-1]]}
    }
    return core.utils.plotly_graphics.line_graphic(data["x"], data["y"], options)
