# Generic imports
import inspect
from collections import defaultdict


# Local imports
import core.models
import dashboard.models
import dashboard.utils.generic_process_data


def get_top_level_function_names(module):
    # Get a list of all functions in the module
    functions = inspect.getmembers(module, inspect.isfunction)
    # Extract only the top-level methods, excluding inner methods
    return [func[0] for func in functions if func[1].__module__ == dashboard.utils.generic_process_data.__name__]


def remove_older_graphic_jsons(graphic_name, date):
    """Remove graphic jsons with creation date strictly older than given (not equal to)

    Args:
        graphic_name (str): Name of the graphic json to delete
        date (datetime): Date from which graphic jsons will be deleted
    """
    dashboard.models.GraphicJsonFile.objects.filter(
        graphic_name__exact=graphic_name,
        creation_date__lt=date
    ).delete()
    return


def update_graphic_json_data():
    """The function is called from crontab to update graphic json data

    Args:
        days_to_check (int, optional): Graphic jsons older than this num will be 
        deleted, keeping the most recent ones. Defaults to 7.
    """
    names_and_dates = dashboard.models.GraphicJsonFile.objects.values("graphic_name", "creation_date")
    grouped_jsons = defaultdict(list)
    for item in names_and_dates:
        grouped_jsons[item["graphic_name"]].append(item["creation_date"])
    for graphic_name, dates in grouped_jsons.items():
        last_date = max(dates)
        # Keep only the last graphic json
        remove_older_graphic_jsons(graphic_name, last_date)
    
    # Start updating all graphic jsons
    print("Starting graphic jsons update...")
    print("Running pre_proc_calculation_date()")
    dashboard.utils.generic_process_data.pre_proc_calculation_date()
    print("Running pre_proc_variant_graphic()")
    dashboard.utils.generic_process_data.pre_proc_variant_graphic()
    print("Running pre_proc_specimen_source_pcr_1()")
    dashboard.utils.generic_process_data.pre_proc_specimen_source_pcr_1()
    print("Running pre_proc_library_kit_pcr_1()")
    dashboard.utils.generic_process_data.pre_proc_library_kit_pcr_1()
    print("Running pre_proc_based_pairs_sequenced()")
    dashboard.utils.generic_process_data.pre_proc_based_pairs_sequenced()
    print("Running pre_proc_depth_variants()")
    dashboard.utils.generic_process_data.pre_proc_depth_variants()
    print("Running pre_proc_depth_sample_run()")
    dashboard.utils.generic_process_data.pre_proc_depth_sample_run()
    uniq_chrom_id_list = [
        x["chromosomeID"] for x in core.models.Gene.objects.values("chromosomeID").distinct()
    ]
    print(f"List of extracted unique chromosomes: {uniq_chrom_id_list}")
    print("Running pre_proc_variations_per_lineage() for each chromosome")
    for chromosome in uniq_chrom_id_list:
        dashboard.utils.generic_process_data.pre_proc_variations_per_lineage(
            chromosome=chromosome
        )


