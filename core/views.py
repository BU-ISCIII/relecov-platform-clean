# Generic imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Local imports
import core.utils.samples
import core.utils.schema
import core.utils.bioinfo_analysis
import core.utils.labs
import core.utils.public_db
import core.utils.variants
import core.utils.generic_functions
import core.utils.annotation
import core.utils.lineage
import core.config

# Imports for received samples graphic at intranet
import core.utils.samples_graphics
import core.utils.samples_map

#  End of imports  received samples


def index(request):
    number_of_samples = core.utils.samples.count_handled_samples()
    nextstrain_url = core.utils.generic_functions.get_configuration_value(
        "NEXTSTRAIN_URL"
    )
    return render(
        request,
        "core/index.html",
        {"number_of_samples": number_of_samples, "nextstrain_url": nextstrain_url},
    )


@login_required
def assign_samples_to_user(request):
    if request.user.username != "admin":
        return redirect("/")
    if request.method == "POST" and request.POST["action"] == "assignSamples":
        assign = core.utils.samples.assign_samples_to_new_user(request.POST)
        return render(request, "core/assignSamplesToUser.html", assign)

    lab_data = {}
    lab_data["labs"] = core.utils.labs.get_all_defined_labs()
    lab_data["users"] = core.utils.generic_functions.get_defined_users()
    return render(
        request,
        "core/assignSamplesToUser.html",
        {"lab_data": lab_data},
    )


@login_required
def sample_display(request, sample_id):
    sample_data = core.utils.samples.get_sample_display_data(sample_id, request.user)
    if "ERROR" in sample_data:
        return render(
            request, "core/sampleDisplay.html", {"ERROR": sample_data["ERROR"]}
        )
    sample_data["gisaid"] = core.utils.public_db.get_public_information_from_sample(
        "gisaid", sample_id
    )
    sample_data["ena"] = core.utils.public_db.get_public_information_from_sample(
        "ena", sample_id
    )
    sample_data["bioinfo"] = (
        core.utils.bioinfo_analysis.get_bioinfo_analysis_data_from_sample(sample_id)
    )
    sample_data["lineage"] = core.utils.lineage.get_lineage_data_from_sample(sample_id)
    sample_data["variant"] = core.utils.variants.get_variant_data_from_sample(sample_id)
    # Display graphic only if variant data are for the sample
    if "heading" in sample_data["variant"]:
        sample_data["graphic"] = core.utils.variants.get_variant_graphic_from_sample(
            sample_id
        )
    return render(request, "core/sampleDisplay.html", {"sample_data": sample_data})


@login_required
def schema_handling(request):
    if request.user.username != "admin":
        return redirect("/")
    if request.method == "POST" and request.POST["action"] == "uploadSchema":
        if "schemaDefault" in request.POST:
            schemaDefault = "on"
        else:
            schemaDefault = "off"
        schema_data = core.utils.schema.process_schema_file(
            request.FILES["schemaFile"],
            schemaDefault,
            request.user,
            __package__,
        )
        if "ERROR" in schema_data:
            return render(
                request,
                "core/schemaHandling.html",
                {"ERROR": schema_data["ERROR"]},
            )
        schemas = core.utils.schema.get_schemas_loaded(__package__)
        return render(
            request,
            "core/schemaHandling.html",
            {"SUCCESS": schema_data["SUCCESS"], "schemas": schemas},
        )
    schemas = core.utils.schema.get_schemas_loaded(__package__)
    return render(request, "core/schemaHandling.html", {"schemas": schemas})


@login_required
def schema_display(request, schema_id):
    if request.user.username != "admin":
        return redirect("/")
    schema_data = core.utils.schema.get_schema_display_data(schema_id)
    return render(request, "core/schemaDisplay.html", {"schema_data": schema_data})


@login_required
def search_sample(request):
    """Search sample using the filter in the form"""
    search_data = core.utils.samples.get_search_data(request.user)
    if request.method == "POST" and request.POST["action"] == "searchSample":
        sample_name = request.POST["sampleName"]
        s_date = request.POST["sDate"]
        lab_name = request.POST["lab"]
        sample_state = request.POST["sampleState"]
        # check that some values are in the request if not return the form
        if lab_name == "" and s_date == "" and sample_name == "" and sample_state == "":
            return render(
                request, "core/searchSample.html", {"search_data": search_data}
            )
        # check the right format of s_date
        if s_date != "" and not core.utils.generic_functions.check_valid_date_format(
            s_date
        ):
            return render(
                request,
                "core/searchSample.html",
                {
                    "search_data": search_data,
                    "warning": core.config.ERROR_INVALID_DEFINED_SAMPLE_FORMAT,
                },
            )
        sample_list = core.utils.samples.search_samples(
            sample_name, lab_name, sample_state, s_date, request.user
        )
        if len(sample_list) == 0:
            return render(
                request,
                "core/searchSample.html",
                {
                    "search_data": search_data,
                    "warning": core.config.ERROR_NOT_MATCHED_ITEMS_IN_SEARCH,
                },
            )
        if len(sample_list) == 1:
            return redirect("sample_display", sample_id=sample_list[0])
        else:
            sample = {
                "s_data": sample_list,
                "heading": core.config.HEADING_FOR_SAMPLE_LIST,
            }
            return render(request, "core/searchSample.html", {"list_display": sample})
    if "ERROR" in search_data:
        return render(
            request, "core/searchSample.html", {"ERROR": search_data["ERROR"]}
        )
    return render(request, "core/searchSample.html", {"search_data": search_data})


@login_required
def metadata_visualization(request):
    if request.user.username != "admin":
        return redirect("/")
    if request.method == "POST" and request.POST["action"] == "selectFields":
        selected_fields = core.utils.schema.store_fields_metadata_visualization(
            request.POST
        )
        if "ERROR" in selected_fields:
            m_visualization = core.utils.schema.get_fields_from_schema(
                core.utils.schema.get_schema_obj_from_id(request.POST["schemaID"])
            )
            return render(
                request,
                "core/metadataVisualization.html",
                {"ERROR": selected_fields, "m_visualization": m_visualization},
            )
        return render(
            request,
            "core/metadataVisualization.html",
            {"SUCCESS": selected_fields},
        )
    if request.method == "POST" and request.POST["action"] == "deleteFields":
        core.utils.schema.del_metadata_visualization()
        return render(request, "core/metadataVisualization.html", {"DELETE": "DELETE"})
    metadata_obj = core.utils.schema.get_latest_schema("Relecov", __package__)
    if isinstance(metadata_obj, dict):
        return render(
            request,
            "core/metadataVisualization.html",
            {"ERROR": metadata_obj["ERROR"]},
        )
    data_visualization = core.utils.schema.fetch_info_meta_visualization(metadata_obj)
    if isinstance(data_visualization, dict):
        return render(
            request,
            "core/metadataVisualization.html",
            {"data_visualization": data_visualization},
        )
    m_visualization = core.utils.schema.get_fields_from_schema(metadata_obj)
    return render(
        request,
        "core/metadataVisualization.html",
        {"m_visualization": m_visualization},
    )


@login_required
def intranet(request):
    relecov_group = Group.objects.filter(name="RelecovManager").last()
    if relecov_group not in request.user.groups.all():
        intra_data = {}
        lab_name = core.utils.labs.get_lab_name_from_user(request.user)
        date_lab_samples = core.utils.samples.get_sample_per_date_per_lab(lab_name)
        if len(date_lab_samples) > 0:
            sample_lab_objs = core.utils.samples.get_sample_objs_per_lab(lab_name)
            analysis_percent = (
                core.utils.bioinfo_analysis.get_bio_analysis_stats_from_lab(lab_name)
            )
            cust_data = {
                "col_names": ["Sequencing Date", "Number of samples"],
                "options": {},
            }
            cust_data["options"]["title"] = "Samples Received"
            cust_data["options"]["width"] = 600
            intra_data["sample_bar_graph"] = core.utils.samples.create_date_sample_bar(
                date_lab_samples, cust_data
            )
            intra_data["sample_gauge_graph"] = core.utils.samples.perc_gauge_graphic(
                analysis_percent
            )
            intra_data["actions"] = core.utils.samples.get_lab_last_actions(lab_name)
            gisaid_acc = core.utils.public_db.get_public_accession_from_sample_lab(
                "gisaid_accession_id", sample_lab_objs
            )
            if len(gisaid_acc) > 0:
                intra_data["gisaid_accession"] = gisaid_acc
            intra_data["gisaid_graph"] = core.utils.public_db.percentage_graphic(
                len(sample_lab_objs), len(gisaid_acc), ""
            )
            ena_acc = core.utils.public_db.get_public_accession_from_sample_lab(
                "ena_sample_accession", sample_lab_objs
            )
            if len(ena_acc) > 0:
                intra_data["ena_accession"] = ena_acc
                intra_data["ena_graph"] = core.utils.public_db.percentage_graphic(
                    len(sample_lab_objs), len(ena_acc), ""
                )
        else:
            intra_data = f"No samples found for selected laboratory: {lab_name}"
        return render(request, "core/intranet.html", {"intra_data": intra_data})
    else:
        # loged user belongs to Relecov Manager group
        manager_intra_data = {}
        all_sample_per_date = core.utils.samples.get_sample_per_date_per_all_lab()
        num_of_samples = core.utils.samples.count_handled_samples()
        if len(all_sample_per_date) > 0:
            cust_data = {
                "col_names": ["Sequencing Date", "Number of samples"],
                "options": {},
            }
            cust_data["options"]["title"] = "Samples Received for all laboratories"
            cust_data["options"]["width"] = 590
            manager_intra_data["sample_bar_graph"] = (
                core.utils.samples.create_date_sample_bar(
                    all_sample_per_date, cust_data
                )
            )
            # graph for percentage analysis
            analysis_percent = (
                core.utils.bioinfo_analysis.get_bio_analysis_stats_from_lab()
            )
            manager_intra_data["sample_gauge_graph"] = (
                core.utils.samples.perc_gauge_graphic(analysis_percent)
            )
            # dash graph for samples per lab
            core.utils.samples.create_dash_bar_for_each_lab()
            # Get the latest action from each lab
            manager_intra_data["actions"] = core.utils.samples.get_lab_last_actions()
            # Collect GISAID information
            gisaid_acc = core.utils.public_db.get_public_accession_from_sample_lab(
                "gisaid_accession_id", None
            )
            if len(gisaid_acc) > 0:
                manager_intra_data["gisaid_accession"] = gisaid_acc
                manager_intra_data["gisaid_graph"] = (
                    core.utils.public_db.percentage_graphic(
                        num_of_samples["Defined"], len(gisaid_acc), ""
                    )
                )
            # Collect Ena information
            ena_acc = core.utils.public_db.get_public_accession_from_sample_lab(
                "ena_sample_accession", None
            )
            if len(ena_acc) > 0:
                manager_intra_data["ena_accession"] = ena_acc
                manager_intra_data["ena_graph"] = (
                    core.utils.public_db.percentage_graphic(
                        num_of_samples["Defined"], len(ena_acc), ""
                    )
                )
        return render(
            request,
            "core/intranet.html",
            {"manager_intra_data": manager_intra_data},
        )


def variants(request):
    return render(request, "core/variants.html", {})


@login_required()
def metadata_form(request):
    schema_obj = core.utils.schema.get_latest_schema("relecov", __package__)
    if request.method == "POST" and request.POST["action"] == "uploadMetadataFile":
        if "metadataFile" in request.FILES:
            core.utils.samples.save_excel_form_in_samba_folder(
                request.FILES["metadataFile"], request.user.username
            )
            return render(
                request,
                "core/metadataForm.html",
                {"sample_recorded": {"ok": "OK"}},
            )
    if request.method == "POST" and request.POST["action"] == "defineSamples":
        res_analyze = core.utils.samples.analyze_input_samples(request)
        # empty form
        if len(res_analyze) == 0:
            m_form = core.utils.samples.create_metadata_form(schema_obj, request.user)
            return render(request, "core/metadataForm.html", {"m_form": m_form})
        if "save_samples" in res_analyze:
            s_saved = core.utils.samples.save_temp_sample_data(
                res_analyze["save_samples"], request.user
            )
        if "s_incomplete" in res_analyze or "s_already_record" in res_analyze:
            if "s_incomplete" not in res_analyze:
                m_form = None
            else:
                m_form = core.utils.samples.create_metadata_form(
                    schema_obj, request.user
                )
            return render(
                request,
                "core/metadataForm.html",
                {"sample_issues": res_analyze, "m_form": m_form},
            )
        m_batch_form = core.utils.samples.create_form_for_batch(
            schema_obj, request.user
        )
        sample_saved = core.utils.samples.get_sample_pre_recorded(request.user)
        return render(
            request,
            "core/metadataForm.html",
            {"m_batch_form": m_batch_form, "sample_saved": s_saved},
        )
    if request.method == "POST" and request.POST["action"] == "defineBatch":
        if not core.utils.samples.check_if_empty_data(request.POST):
            sample_saved = core.utils.samples.get_sample_pre_recorded(request.user)
            m_batch_form = core.utils.samples.create_form_for_batch(
                schema_obj, request.user
            )
            return render(
                request,
                "core/metadataForm.html",
                {"m_batch_form": m_batch_form, "sample_saved": sample_saved},
            )
        meta_data = core.utils.samples.join_sample_and_batch(
            request.POST, request.user, schema_obj
        )
        # write date to excel using relecov tools
        core.utils.samples.write_form_data_to_excel(meta_data, request.user)
        core.utils.samples.delete_temporary_sample_table(request.user)
        # Display page to indicate that process is starting
        return render(
            request, "core/metadataForm.html", {"sample_recorded": {"ok": "OK"}}
        )
    else:
        if core.utils.samples.pending_samples_in_metadata_form(request.user):
            sample_saved = core.utils.samples.get_sample_pre_recorded(request.user)
            m_batch_form = core.utils.samples.create_form_for_batch(
                schema_obj, request.user
            )
            return render(
                request,
                "core/metadataForm.html",
                {"m_batch_form": m_batch_form, "sample_saved": sample_saved},
            )
        m_form = core.utils.samples.create_metadata_form(schema_obj, request.user)
        if "ERROR" in m_form:
            return render(request, "core/metadataForm.html", {"ERROR": m_form["ERROR"]})
        if m_form["lab_name"] == "":
            return render(
                request,
                "core/metadataForm.html",
                {"ERROR": core.config.ERROR_USER_IS_NOT_ASSIGNED_TO_LAB},
            )
        return render(request, "core/metadataForm.html", {"m_form": m_form})


@login_required()
def annotation_display(request, annot_id):
    """Display the full information about the organism annotation stored in
    database
    """
    if request.user.username != "admin":
        return redirect("/")
    if not core.utils.annotation.check_if_annotation_exists(annot_id):
        return render(request, "core/error_404.html")
    annot_data = core.utils.annotation.get_annotation_data(annot_id)
    return render(
        request, "core/annotationDisplay.html", {"annotation_data": annot_data}
    )


@login_required()
def organism_annotation(request):
    """Store the organism annotation gff file"""
    if request.user.username != "admin":
        return redirect("/")
    annotations = core.utils.annotation.get_annotations()
    if request.method == "POST" and request.POST["action"] == "uploadAnnotation":
        gff_parsed = core.utils.annotation.read_gff_file(request.FILES["gffFile"])
        if "ERROR" in gff_parsed:
            return render(
                request,
                "core/organismAnnotation.html",
                {"ERROR": gff_parsed["ERROR"], "annotations": annotations},
            )
        core.utils.annotation.store_gff(gff_parsed, request.user)
        annotations = core.utils.annotation.get_annotations()
        return render(
            request,
            "core/organismAnnotation.html",
            {"SUCCESS": "Success", "annotations": annotations},
        )
    return render(request, "core/organismAnnotation.html", {"annotations": annotations})


@login_required()
def laboratory_contact(request):
    lab_data = core.utils.labs.get_lab_contact_details(request.user)
    if "ERROR" in lab_data:
        return render(
            request, "core/laboratoryContact.html", {"ERROR": lab_data["ERROR"]}
        )
    if request.method == "POST" and request.POST["action"] == "updateLabData":
        result = core.utils.labs.update_contact_lab(lab_data, request.POST)
        if isinstance(result, dict):
            return render(
                request,
                "core/laboratoryContact.html",
                {"ERROR": result["ERROR"]},
            )
        return render(request, "core/laboratoryContact.html", {"Success": "Success"})
    return render(request, "core/laboratoryContact.html", {"lab_data": lab_data})


@login_required
def received_samples(request):
    sample_data = {}
    # samples receive over time map
    sample_data["map"] = core.utils.samples_map.create_samples_received_map()
    # samples receive over time graph
    # df = create_dataframe_from_json()
    # create_samples_over_time_graph(df)

    # # collecting now data from database
    sample_data["received_samples_graph"] = (
        core.utils.samples_graphics.received_samples_graph()
    )
    # Pie charts
    # data = parse_json_file()
    # create_samples_received_over_time_per_ccaa_pieChart(data)
    sample_data["samples_per_ccaa"] = core.utils.samples_graphics.received_per_ccaa()
    # create_samples_received_over_time_per_laboratory_pieChart(data)
    sample_data["samples_per_lab"] = core.utils.samples_graphics.received_per_lab()
    return render(
        request,
        "core/receivedSamples.html",
        {"sample_data": sample_data},
    )


def contact(request):
    return render(request, "core/contact.html", {})
