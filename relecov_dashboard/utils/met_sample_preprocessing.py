# Generc imports
import pandas

# Local imports
import relecov_core.utils.rest_api_handling
import relecov_dashboard.utils.generic_graphic_data
import relecov_dashboard.utils.plotly
import relecov_dashboard.utils.generic_process_data


def sample_processing_graphics():
    def get_pre_proc_data(graphic_name):
        """Get the pre-processed data for the graphic name.
        If there is no data stored for the graphic, it will query to store
        them before calling for the second time
        """
        json_data = relecov_dashboard.utils.generic.generic_graphic_data.get_graphic_json_data(
            graphic_name
        )
        if json_data is None:
            # Execute the pre-processed task to get the data
            if graphic_name == "specimen_source_pcr_1":
                result = (
                    relecov_dashboard.utils.generic.generic_process_data.pre_proc_specimen_source_pcr_1()
                )
            elif graphic_name == "extraction_protocol_pcr_1":
                result = (
                    relecov_dashboard.utils.generic.generic_process_data.pre_proc_extraction_protocol_pcr_1()
                )
            elif graphic_name == "calculation_date":
                result = (
                    relecov_dashboard.utils.generic.generic_process_data.pre_proc_calculation_date()
                )
            else:
                return {"ERROR": "pre-processing not defined"}
            if "ERROR" in result:
                return result
            json_data = (
                relecov_dashboard.utils.generic.generic_graphic_data.get_graphic_json_data(
                    graphic_name
                )
            )
        # Convert string to float values
        if graphic_name == "calculation_date":
            return [json_data]
        data = []

        for key, values in json_data.items():
            tmp_data = []
            for str_val, numbers in values.items():
                try:
                    float_val = float(str_val)
                except ValueError:
                    continue
                tmp_data += [float_val] * numbers
            data.append({key: tmp_data})
        return data

    def fetch_data(project_field, columns):
        # get stats utilization fields from LIMS about nucleic acid extraction protocol
        lims_data = relecov_core.utils.rest_api_handling.get_stats_data(
            {
                "sample_project_name": "Relecov",
                "project_field": project_field,
            }
        )
        if "ERROR" in lims_data:
            return lims_data
        if "," in project_field:
            data = []
            for key, values in lims_data.items():
                tmp_data = []
                for str_val, numbers in values.items():
                    try:
                        float_val = float(str_val)
                    except ValueError:
                        continue
                    tmp_data += [float_val] * numbers
                data.append({key: tmp_data})
            return data
        else:
            return pandas.DataFrame(lims_data.items(), columns=columns)

    sample_processing = {}

    # extraction protocol graphics
    extraction_protocol_df = fetch_data(
        project_field="nucleic_acid_extraction_protocol", columns=["protocol", "number"]
    )
    if "ERROR" in extraction_protocol_df:
        return extraction_protocol_df
    sample_processing["nucleic_protocol"] = (
        relecov_dashboard.utils.generic.graphics.plotly.bar_graphic(
            data=extraction_protocol_df,
            col_names=["protocol", "number"],
            legend=[""],
            yaxis={"title": "Number of samples"},
            options={
                "title": "Nucleic acid extraction protocol",
                "height": 400,
                "width": 320,
            },
        )
    )

    cts_extraction_data = get_pre_proc_data("extraction_protocol_pcr_1")

    sample_processing["cts_extraction"] = (
        relecov_dashboard.utils.generic.graphics.plotly.box_plot_graphic(
            cts_extraction_data,
            {"title": "Boxplot Cts / Extraction protocol", "height": 400, "width": 520},
        )
    )
    # specimen source graphics
    cts_specimen_data = get_pre_proc_data("specimen_source_pcr_1")

    sample_processing["cts_specimen"] = (
        relecov_dashboard.utils.generic.graphics.plotly.box_plot_graphic(
            cts_specimen_data,
            {"title": "Boxplot Cts / specimen source", "height": 400, "width": 600},
        )
    )
    # calculate the number of days spent in each state before moved on to the next step
    calculation_date_data = get_pre_proc_data("calculation_date")
    sample_processing["calculation_date"] = (
        relecov_dashboard.utils.generic.graphics.plotly.box_plot_graphic(
            calculation_date_data,
            {"title": "Time between sample step actions", "height": 400, "width": 420},
        )
    )
    return sample_processing
