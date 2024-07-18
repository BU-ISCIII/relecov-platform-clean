from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

import relecov_core.utils.samples
import relecov_core.utils.schema_handling
import relecov_core.utils.bioinfo_analysis
import relecov_core.utils.labs
import relecov_core.utils.public_db
import relecov_core.utils.variants
import relecov_core.utils.generic_functions
import relecov_core.utils.annotation
import relecov_core.utils.lineage

# Imports for received samples graphic at intranet
import relecov_core.utils.samples_graphics
import relecov_core.utils.samples_map

#  End of imports  received samples

from relecov_core.core_config import (
    ERROR_USER_IS_NOT_ASSIGNED_TO_LAB,
    ERROR_INVALID_DEFINED_SAMPLE_FORMAT,
    ERROR_NOT_MATCHED_ITEMS_IN_SEARCH,
    HEADING_FOR_SAMPLE_LIST,
)


def index(request):
    number_of_samples = relecov_core.utils.samples.count_handled_samples()
    nextstrain_url = relecov_core.utils.generic_functions.get_configuration_value(
        "NEXTSTRAIN_URL"
    )
    return render(
        request,
        "relecov_core/index.html",
        {"number_of_samples": number_of_samples, "nextstrain_url": nextstrain_url},
    )


@login_required
def assign_samples_to_user(request):
    if request.user.username != "admin":
        return redirect("/")
    if request.method == "POST" and request.POST["action"] == "assignSamples":
        assign = relecov_core.utils.samples.assign_samples_to_new_user(request.POST)
        return render(request, "relecov_core/assignSamplesToUser.html", assign)

    lab_data = {}
    lab_data["labs"] = relecov_core.utils.labs.get_all_defined_labs()
    lab_data["users"] = relecov_core.utils.generic_functions.get_defined_users()
    return render(
        request,
        "relecov_core/assignSamplesToUser.html",
        {"lab_data": lab_data},
    )


@login_required
def sample_display(request, sample_id):
    sample_data = relecov_core.utils.samples.get_sample_display_data(
        sample_id, request.user
    )
    if "ERROR" in sample_data:
        return render(
            request, "relecov_core/sampleDisplay.html", {"ERROR": sample_data["ERROR"]}
        )
    sample_data["gisaid"] = (
        relecov_core.utils.public_db.get_public_information_from_sample(
            "gisaid", sample_id
        )
    )
    sample_data["ena"] = (
        relecov_core.utils.public_db.get_public_information_from_sample(
            "ena", sample_id
        )
    )
    sample_data["bioinfo"] = (
        relecov_core.utils.bioinfo_analysis.get_bioinfo_analysis_data_from_sample(
            sample_id
        )
    )
    sample_data["lineage"] = relecov_core.utils.lineage.get_lineage_data_from_sample(
        sample_id
    )
    sample_data["variant"] = relecov_core.utils.variants.get_variant_data_from_sample(
        sample_id
    )
    # Display graphic only if variant data are for the sample
    if "heading" in sample_data["variant"]:
        sample_data["graphic"] = (
            relecov_core.utils.variants.get_variant_graphic_from_sample(sample_id)
        )
    return render(
        request, "relecov_core/sampleDisplay.html", {"sample_data": sample_data}
    )


@login_required
def schema_handling(request):
    if request.user.username != "admin":
        return redirect("/")
    if request.method == "POST" and request.POST["action"] == "uploadSchema":
        if "schemaDefault" in request.POST:
            schemaDefault = "on"
        else:
            schemaDefault = "off"
        schema_data = relecov_core.utils.schema_handling.process_schema_file(
            request.FILES["schemaFile"],
            schemaDefault,
            request.user,
            __package__,
        )
        if "ERROR" in schema_data:
            return render(
                request,
                "relecov_core/schemaHandling.html",
                {"ERROR": schema_data["ERROR"]},
            )
        schemas = relecov_core.utils.schema_handling.get_schemas_loaded(__package__)
        return render(
            request,
            "relecov_core/schemaHandling.html",
            {"SUCCESS": schema_data["SUCCESS"], "schemas": schemas},
        )
    schemas = relecov_core.utils.schema_handling.get_schemas_loaded(__package__)
    return render(request, "relecov_core/schemaHandling.html", {"schemas": schemas})


@login_required
def schema_display(request, schema_id):
    if request.user.username != "admin":
        return redirect("/")
    schema_data = relecov_core.utils.schema_handling.get_schema_display_data(schema_id)
    return render(
        request, "relecov_core/schemaDisplay.html", {"schema_data": schema_data}
    )


@login_required
def search_sample(request):
    """Search sample using the filter in the form"""
    search_data = relecov_core.utils.samples.get_search_data(request.user)
    if request.method == "POST" and request.POST["action"] == "searchSample":
        sample_name = request.POST["sampleName"]
        s_date = request.POST["sDate"]
        lab_name = request.POST["lab"]
        sample_state = request.POST["sampleState"]
        # check that some values are in the request if not return the form
        if lab_name == "" and s_date == "" and sample_name == "" and sample_state == "":
            return render(
                request, "relecov_core/searchSample.html", {"search_data": search_data}
            )
        # check the right format of s_date
        if (
            s_date != ""
            and not relecov_core.utils.generic_functions.check_valid_date_format(s_date)
        ):
            return render(
                request,
                "relecov_core/searchSample.html",
                {
                    "search_data": search_data,
                    "warning": ERROR_INVALID_DEFINED_SAMPLE_FORMAT,
                },
            )
        sample_list = relecov_core.utils.samples.search_samples(
            sample_name, lab_name, sample_state, s_date, request.user
        )
        if len(sample_list) == 0:
            return render(
                request,
                "relecov_core/searchSample.html",
                {
                    "search_data": search_data,
                    "warning": ERROR_NOT_MATCHED_ITEMS_IN_SEARCH,
                },
            )
        if len(sample_list) == 1:
            return redirect("sample_display", sample_id=sample_list[0])
        else:
            sample = {"s_data": sample_list, "heading": HEADING_FOR_SAMPLE_LIST}
            return render(
                request, "relecov_core/searchSample.html", {"list_display": sample}
            )
    if "ERROR" in search_data:
        return render(
            request, "relecov_core/searchSample.html", {"ERROR": search_data["ERROR"]}
        )
    return render(
        request, "relecov_core/searchSample.html", {"search_data": search_data}
    )


@login_required
def metadata_visualization(request):
    if request.user.username != "admin":
        return redirect("/")
    if request.method == "POST" and request.POST["action"] == "selectFields":
        selected_fields = (
            relecov_core.utils.schema_handling.store_fields_metadata_visualization(
                request.POST
            )
        )
        if "ERROR" in selected_fields:
            m_visualization = relecov_core.utils.schema_handling.get_fields_from_schema(
                relecov_core.utils.schema_handling.get_schema_obj_from_id(
                    request.POST["schemaID"]
                )
            )
            return render(
                request,
                "relecov_core/metadataVisualization.html",
                {"ERROR": selected_fields, "m_visualization": m_visualization},
            )
        return render(
            request,
            "relecov_core/metadataVisualization.html",
            {"SUCCESS": selected_fields},
        )
    if request.method == "POST" and request.POST["action"] == "deleteFields":
        relecov_core.utils.schema_handling.del_metadata_visualization()
        return render(
            request, "relecov_core/metadataVisualization.html", {"DELETE": "DELETE"}
        )
    metadata_obj = relecov_core.utils.schema_handling.get_latest_schema(
        "Relecov", __package__
    )
    if isinstance(metadata_obj, dict):
        return render(
            request,
            "relecov_core/metadataVisualization.html",
            {"ERROR": metadata_obj["ERROR"]},
        )
    data_visualization = (
        relecov_core.utils.schema_handling.fetch_info_meta_visualization(metadata_obj)
    )
    if isinstance(data_visualization, dict):
        return render(
            request,
            "relecov_core/metadataVisualization.html",
            {"data_visualization": data_visualization},
        )
    m_visualization = relecov_core.utils.schema_handling.get_fields_from_schema(
        metadata_obj
    )
    return render(
        request,
        "relecov_core/metadataVisualization.html",
        {"m_visualization": m_visualization},
    )


@login_required
def intranet(request):
    relecov_group = Group.objects.filter(name="RelecovManager").last()
    if relecov_group not in request.user.groups.all():
        intra_data = {}
        lab_name = relecov_core.utils.labs.get_lab_name_from_user(request.user)
        date_lab_samples = relecov_core.utils.samples.get_sample_per_date_per_lab(
            lab_name
        )
        if len(date_lab_samples) > 0:
            sample_lab_objs = relecov_core.utils.samples.get_sample_objs_per_lab(
                lab_name
            )
            analysis_percent = relecov_core.utils.labs.get_bio_analysis_stats_from_lab(
                lab_name
            )
            cust_data = {
                "col_names": ["Sequencing Date", "Number of samples"],
                "options": {},
            }
            cust_data["options"]["title"] = "Samples Received"
            cust_data["options"]["width"] = 600
            intra_data["sample_bar_graph"] = (
                relecov_core.utils.samples.create_date_sample_bar(
                    date_lab_samples, cust_data
                )
            )
            intra_data["sample_gauge_graph"] = (
                relecov_core.utils.samples.perc_gauge_graphic(analysis_percent)
            )
            intra_data["actions"] = relecov_core.utils.samples.get_lab_last_actions(
                lab_name
            )
            gisaid_acc = (
                relecov_core.utils.public_db.get_public_accession_from_sample_lab(
                    "gisaid_accession_id", sample_lab_objs
                )
            )
            if len(gisaid_acc) > 0:
                intra_data["gisaid_accession"] = gisaid_acc
            intra_data["gisaid_graph"] = (
                relecov_core.utils.public_db.percentage_graphic(
                    len(sample_lab_objs), len(gisaid_acc), ""
                )
            )
            ena_acc = relecov_core.utils.public_db.get_public_accession_from_sample_lab(
                "ena_sample_accession", sample_lab_objs
            )
            if len(ena_acc) > 0:
                intra_data["ena_accession"] = ena_acc
                intra_data["ena_graph"] = (
                    relecov_core.utils.public_db.percentage_graphic(
                        len(sample_lab_objs), len(ena_acc), ""
                    )
                )
        return render(request, "relecov_core/intranet.html", {"intra_data": intra_data})
    else:
        # loged user belongs to Relecov Manager group
        manager_intra_data = {}
        all_sample_per_date = (
            relecov_core.utils.samples.get_sample_per_date_per_all_lab()
        )
        num_of_samples = relecov_core.utils.samples.count_handled_samples()
        if len(all_sample_per_date) > 0:
            cust_data = {
                "col_names": ["Sequencing Date", "Number of samples"],
                "options": {},
            }
            cust_data["options"]["title"] = "Samples Received for all laboratories"
            cust_data["options"]["width"] = 590
            manager_intra_data["sample_bar_graph"] = (
                relecov_core.utils.samples.create_date_sample_bar(
                    all_sample_per_date, cust_data
                )
            )
            # graph for percentage analysis
            analysis_percent = relecov_core.utils.labs.get_bio_analysis_stats_from_lab()
            manager_intra_data["sample_gauge_graph"] = (
                relecov_core.utils.samples.perc_gauge_graphic(analysis_percent)
            )
            # dash graph for samples per lab
            relecov_core.utils.samples.create_dash_bar_for_each_lab()
            # Get the latest action from each lab
            manager_intra_data["actions"] = (
                relecov_core.utils.samples.get_lab_last_actions()
            )
            # Collect GISAID information
            gisaid_acc = (
                relecov_core.utils.public_db.get_public_accession_from_sample_lab(
                    "gisaid_accession_id", None
                )
            )
            if len(gisaid_acc) > 0:
                manager_intra_data["gisaid_accession"] = gisaid_acc
                manager_intra_data["gisaid_graph"] = (
                    relecov_core.utils.public_db.percentage_graphic(
                        num_of_samples["Defined"], len(gisaid_acc), ""
                    )
                )
            # Collect Ena information
            ena_acc = relecov_core.utils.public_db.get_public_accession_from_sample_lab(
                "ena_sample_accession", None
            )
            if len(ena_acc) > 0:
                manager_intra_data["ena_accession"] = ena_acc
                manager_intra_data["ena_graph"] = (
                    relecov_core.utils.public_db.percentage_graphic(
                        num_of_samples["Defined"], len(ena_acc), ""
                    )
                )
        # import pdb; pdb.set_trace()
        return render(
            request,
            "relecov_core/intranet.html",
            {"manager_intra_data": manager_intra_data},
        )


def variants(request):
    return render(request, "relecov_core/relecov_core.utils.variants.html", {})


@login_required()
def metadata_form(request):
    schema_obj = relecov_core.utils.schema_handling.get_latest_schema(
        "relecov", __package__
    )
    if request.method == "POST" and request.POST["action"] == "uploadMetadataFile":
        if "metadataFile" in request.FILES:
            relecov_core.utils.samples.save_excel_form_in_samba_folder(
                request.FILES["metadataFile"], request.user.username
            )
            return render(
                request,
                "relecov_core/metadataForm.html",
                {"sample_recorded": {"ok": "OK"}},
            )
    if request.method == "POST" and request.POST["action"] == "defineSamples":
        res_analyze = relecov_core.utils.samples.analyze_input_samples(request)
        # empty form
        if len(res_analyze) == 0:
            m_form = relecov_core.utils.samples.create_metadata_form(
                schema_obj, request.user
            )
            return render(request, "relecov_core/metadataForm.html", {"m_form": m_form})
        if "save_samples" in res_analyze:
            s_saved = relecov_core.utils.samples.save_temp_sample_data(
                res_analyze["save_samples"], request.user
            )
        if "s_incomplete" in res_analyze or "s_already_record" in res_analyze:
            if "s_incomplete" not in res_analyze:
                m_form = None
            else:
                m_form = relecov_core.utils.samples.create_metadata_form(
                    schema_obj, request.user
                )
            return render(
                request,
                "relecov_core/metadataForm.html",
                {"sample_issues": res_analyze, "m_form": m_form},
            )
        m_batch_form = relecov_core.utils.samples.create_form_for_batch(
            schema_obj, request.user
        )
        sample_saved = relecov_core.utils.samples.get_sample_pre_recorded(request.user)
        return render(
            request,
            "relecov_core/metadataForm.html",
            {"m_batch_form": m_batch_form, "sample_saved": s_saved},
        )
    if request.method == "POST" and request.POST["action"] == "defineBatch":
        if not relecov_core.utils.samples.check_if_empty_data(request.POST):
            sample_saved = relecov_core.utils.samples.get_sample_pre_recorded(
                request.user
            )
            m_batch_form = relecov_core.utils.samples.create_form_for_batch(
                schema_obj, request.user
            )
            return render(
                request,
                "relecov_core/metadataForm.html",
                {"m_batch_form": m_batch_form, "sample_saved": sample_saved},
            )
        meta_data = relecov_core.utils.samples.join_sample_and_batch(
            request.POST, request.user, schema_obj
        )
        # write date to excel using relecov tools
        relecov_core.utils.samples.write_form_data_to_excel(meta_data, request.user)
        relecov_core.utils.samples.delete_temporary_sample_table(request.user)
        # Display page to indicate that process is starting
        return render(
            request, "relecov_core/metadataForm.html", {"sample_recorded": {"ok": "OK"}}
        )
    else:
        if relecov_core.utils.samples.pending_samples_in_metadata_form(request.user):
            sample_saved = relecov_core.utils.samples.get_sample_pre_recorded(
                request.user
            )
            m_batch_form = relecov_core.utils.samples.create_form_for_batch(
                schema_obj, request.user
            )
            return render(
                request,
                "relecov_core/metadataForm.html",
                {"m_batch_form": m_batch_form, "sample_saved": sample_saved},
            )
        m_form = relecov_core.utils.samples.create_metadata_form(
            schema_obj, request.user
        )
        if "ERROR" in m_form:
            return render(
                request, "relecov_core/metadataForm.html", {"ERROR": m_form["ERROR"]}
            )
        if m_form["lab_name"] == "":
            return render(
                request,
                "relecov_core/metadataForm.html",
                {"ERROR": ERROR_USER_IS_NOT_ASSIGNED_TO_LAB},
            )
        return render(request, "relecov_core/metadataForm.html", {"m_form": m_form})


@login_required()
def annotation_display(request, annot_id):
    """Display the full information about the organism annotation stored in
    database
    """
    if request.user.username != "admin":
        return redirect("/")
    if not relecov_core.utils.annotation.check_if_annotation_exists(annot_id):
        return render(request, "relecov_core/error_404.html")
    annot_data = relecov_core.utils.annotation.get_annotation_data(annot_id)
    return render(
        request, "relecov_core/annotationDisplay.html", {"annotation_data": annot_data}
    )


@login_required()
def organism_annotation(request):
    """Store the organism annotation gff file"""
    if request.user.username != "admin":
        return redirect("/")
    annotations = relecov_core.utils.annotation.get_annotations()
    if request.method == "POST" and request.POST["action"] == "uploadAnnotation":
        gff_parsed = relecov_core.utils.annotation.read_gff_file(
            request.FILES["gffFile"]
        )
        if "ERROR" in gff_parsed:
            return render(
                request,
                "relecov_core/organismAnnotation.html",
                {"ERROR": gff_parsed["ERROR"], "annotations": annotations},
            )
        relecov_core.utils.annotation.store_gff(gff_parsed, request.user)
        annotations = relecov_core.utils.annotation.get_annotations()
        return render(
            request,
            "relecov_core/organismAnnotation.html",
            {"SUCCESS": "Success", "annotations": annotations},
        )
    return render(
        request, "relecov_core/organismAnnotation.html", {"annotations": annotations}
    )


@login_required()
def laboratory_contact(request):
    lab_data = relecov_core.utils.labs.get_lab_contact_details(request.user)
    if "ERROR" in lab_data:
        return render(
            request, "relecov_core/laboratoryContact.html", {"ERROR": lab_data["ERROR"]}
        )
    if request.method == "POST" and request.POST["action"] == "updateLabData":
        result = relecov_core.utils.labs.update_contact_lab(lab_data, request.POST)
        if isinstance(result, dict):
            return render(
                request,
                "relecov_core/laboratoryContact.html",
                {"ERROR": result["ERROR"]},
            )
        return render(
            request, "relecov_core/laboratoryContact.html", {"Success": "Success"}
        )
    return render(
        request, "relecov_core/laboratoryContact.html", {"lab_data": lab_data}
    )


@login_required
def received_samples(request):
    sample_data = {}
    # samples receive over time map
    sample_data["map"] = relecov_core.utils.samples_map.create_samples_received_map()
    # samples receive over time graph
    # df = create_dataframe_from_json()
    # create_samples_over_time_graph(df)

    # # collecting now data from database
    sample_data["received_samples_graph"] = (
        relecov_core.utils.samples_graphics.display_received_samples_graph()
    )
    # Pie charts
    # data = parse_json_file()
    # create_samples_received_over_time_per_ccaa_pieChart(data)
    sample_data["samples_per_ccaa"] = (
        relecov_core.utils.samples_graphics.display_received_per_ccaa()
    )
    # create_samples_received_over_time_per_laboratory_pieChart(data)
    sample_data["samples_per_lab"] = (
        relecov_core.utils.samples_graphics.display_received_per_lab()
    )
    return render(
        request,
        "relecov_core/receivedSamples.html",
        {"sample_data": sample_data},
    )


def contact(request):
    return render(request, "relecov_core/contact.html", {})
