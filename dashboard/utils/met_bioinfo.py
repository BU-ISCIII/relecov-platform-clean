# Generic imports
from collections import OrderedDict
from statistics import mean

# Local imports
import core.models
import dashboard.dashboard_config
import dashboard.utils.generic_graphic_data
import dashboard.utils.plotly
import dashboard.utils.generic_process_data


def bioinfo_graphics():
    def get_pre_proc_data(graphic_name):
        json_data = dashboard.utils.generic_graphic_data.get_graphic_json_data(
            graphic_name
        )
        if json_data is None:
            # Execute the pre-processed task to get the data
            if graphic_name == "depth_variant_consensus":
                result = dashboard.utils.generic_process_data.pre_proc_depth_variants()
            elif graphic_name == "depth_samples_in_run":
                result = (
                    dashboard.utils.generic_process_data.pre_proc_depth_sample_run()
                )
            else:
                return {"ERROR": "pre-processing not defined"}
            if "ERROR" in result:
                return result
            json_data = dashboard.utils.generic_graphic_data.get_graphic_json_data(
                graphic_name
            )
        tmp_json_float = {}
        for key, values in json_data.items():
            tmp_json_float[float(key)] = values
        json_data_sorted = OrderedDict(sorted(tmp_json_float.items()))
        data = {}
        data = {"depth": [], "variant": []}
        for key, values in json_data_sorted.items():
            data["depth"].append(float(key))
            data["variant"].append(mean(values))
        return data

    def get_percentage_data():
        per_data = []
        graph_list = ["per_Ns", "per_reads_host", "per_reads_virus", "per_unmapped"]
        for graph in graph_list:
            if core.models.BioinfoAnalysisValue.objects.filter(
                bioinfo_analysis_fieldID__property_name__exact=graph
            ).exists():
                str_data = list(
                    core.models.BioinfoAnalysisValue.objects.filter(
                        bioinfo_analysis_fieldID__property_name__exact=graph
                    ).values_list("value", flat=True)
                )
                try:
                    per_data.append({graph: list(map(float, str_data))})
                except ValueError:
                    filter_list = []
                    for value in str_data:
                        try:
                            filter_list.append(float(value))
                        except ValueError:
                            continue
                    per_data.append({graph: filter_list})

        return per_data

    bioinfo = {}
    percentage_data = get_percentage_data()
    if "ERROR" not in percentage_data:
        bioinfo["boxplot_comparation"] = dashboard.utils.plotly.box_plot_graphic(
            percentage_data,
            {"title": "Boxplot Percentage", "height": 400, "width": 420},
        )
    depth_variants_data = get_pre_proc_data("depth_variant_consensus")
    if "ERROR" not in depth_variants_data:
        bioinfo["depth_variants"] = dashboard.utils.plotly.line_graphic(
            depth_variants_data["depth"],
            depth_variants_data["variant"],
            {
                "title": "Depth / variant consensus",
                "height": 350,
                "width": 420,
                "x_title": "Depth",
                "y_title": "number of variants",
            },
        )
    depth_sample_run_data = get_pre_proc_data("depth_samples_in_run")
    if "ERROR" not in depth_sample_run_data:
        bioinfo["depth_sample_run"] = dashboard.utils.plotly.line_graphic(
            depth_sample_run_data["depth"],
            depth_sample_run_data["variant"],
            {
                "title": "Depth / number of samples in run",
                "height": 350,
                "width": 420,
                "x_title": "Depth",
                "y_title": "Samples in run",
            },
        )
    if not bioinfo:
        bioinfo["ERROR"] = dashboard.dashboard_config.ERROR_NOT_DATA_LOADED_YET
    return bioinfo
