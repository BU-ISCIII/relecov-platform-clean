import json
import os
from collections import OrderedDict
from datetime import datetime
import pandas as pd
from django.contrib.auth.models import Group, User
from django.conf import settings
from relecov_tools.utils import write_to_excel_file

# from django.db.models import Max

from relecov_core.core_config import (
    ALLOWED_EMPTY_FIELDS_IN_METADATA_SAMPLE_FORM,
    ERROR_FIELDS_FOR_METADATA_ARE_NOT_DEFINED,
    ERROR_ISKYLIMS_NOT_REACHEABLE,
    ERROR_NO_SAMPLES_ARE_ASSIGNED_TO_LAB,
    ERROR_NOT_ALLOWED_TO_SEE_THE_SAMPLE,
    ERROR_NOT_SAMPLES_HAVE_BEEN_DEFINED,
    ERROR_SAMPLE_DOES_NOT_EXIST,
    ERROR_SAMPLES_NOT_DEFINED_IN_FORM,
    ERROR_UNABLE_FETCH_SAMPLE_PROJECT_FIELDS,
    FIELD_FOR_GETTING_SAMPLE_ID,
    HEADING_FOR_BASIC_SAMPLE_DATA,
    HEADING_FOR_FASTQ_SAMPLE_DATA,
)


from relecov_core.models import (
    DateUpdateState,
    MetadataVisualization,
    Profile,
    PublicDatabaseFields,
    PublicDatabaseValues,
    SchemaProperties,
    Sample,
    SampleState,
    TemporalSampleStorage,
)

from relecov_core.utils.handling_lab import get_lab_name, get_all_defined_labs

from relecov_core.utils.plotly_graphics import histogram_graphic, gauge_graphic

from relecov_core.utils.rest_api_handling import (
    get_sample_fields_data,
    get_sample_project_fields_data,
    get_sample_information,
    # save_sample_form_data,
)

from relecov_core.utils.generic_functions import get_configuration_value


def analyze_input_samples(request):
    result = {}
    save_samples = []
    s_already_record = []
    s_incomplete = []
    s_json_data = json.loads(request.POST["table_data"])
    heading_in_form = request.POST["heading"].split(",")
    user_lab = Profile.objects.filter(user=request.user).last().get_lab_name()
    submmit_institution = get_configuration_value("SUBMITTING_INSTITUTION")
    # Select the sample field that will be used in Sample class
    idx_sample = heading_in_form.index(FIELD_FOR_GETTING_SAMPLE_ID)
    allowed_empty_index = []
    for item in ALLOWED_EMPTY_FIELDS_IN_METADATA_SAMPLE_FORM:
        allowed_empty_index.append(heading_in_form.index(item))
    for row in s_json_data:
        row_data = {}
        sample_name = row[idx_sample]
        if sample_name == "":
            continue
        if Sample.objects.filter(sequencing_sample_id__iexact=sample_name).exists():
            s_already_record.append(row)
            continue
        for idx in range(len(heading_in_form)):
            if row[idx] == "" and idx not in allowed_empty_index:
                s_incomplete.append(row)
                break
            row_data[heading_in_form[idx]] = row[idx]
        row_data["Originating Laboratory"] = user_lab
        row_data["Submitting Institution"] = submmit_institution
        save_samples.append(row_data)

    if len(save_samples) > 0:
        result["save_samples"] = save_samples
    if len(s_incomplete) > 0:
        result["s_incomplete"] = s_incomplete
    if len(s_already_record) > 0:
        result["s_already_record"] = s_already_record
    return result


def assign_samples_to_new_user(data):
    """Assign all samples from a laboratory to a new userID"""
    user_obj = User.objects.filter(pk__exact=data["userName"])
    if Sample.objects.filter(collecting_institution__iexact=data["lab"]).exists():
        Sample.objects.filter(collecting_institution__iexact=data["lab"]).update(
            user=user_obj[0]
        )
        return {"Success": "Success"}
    return {"ERROR": ERROR_NO_SAMPLES_ARE_ASSIGNED_TO_LAB + " " + data["lab"]}


def count_samples_in_all_tables():
    """Count the number of entries that are in Sample,"""
    data = {}
    data["received"] = Sample.objects.all().count()
    # data["ena"] = EnaInfo.objects.all().count()
    # data["gisaid"] = GisaidInfo.objects.all().count()
    # data["processed"] = AnalysisPerformed.objects.filter(
    #    typeID__type_name__iexact="bioinfo_analysis"
    # ).count()
    return data


def check_if_empty_data(data):
    """Check if user has not set any data in the form"""
    ignore_fields = ["csrfmiddlewaretoken", "action"]
    for key, value in data.items():
        if key in ignore_fields:
            continue
        if value != "":
            return True
    return False


def create_form_for_batch(schema_obj, user_obj):
    """Collect information for creating for batch from. This form is displayed
    only if previously was defined sample in sample form
    """
    schema_name = schema_obj.get_schema_name()
    try:
        iskylims_sample_raw = get_sample_fields_data()
    except AttributeError:
        return {"ERROR": ERROR_ISKYLIMS_NOT_REACHEABLE}
    if "ERROR" in iskylims_sample_raw:
        return iskylims_sample_raw
    # Remove the characters "schema" if exist in the name of the schema
    if "schema" in schema_name:
        schema_name = schema_name.replace("schema", "").strip()
    i_sam_proj_raw = get_sample_project_fields_data(schema_name)
    i_sam_proj_data = {}
    # Create the structure from the sample project fields get from iSkyLIMS
    for item in i_sam_proj_raw:
        key = item["sampleProjectFieldDescription"]
        i_sam_proj_data[key] = {}
        i_sam_proj_data[key]["format"] = item["sampleProjectFieldType"]
        if item["sampleProjectFieldType"] == "Options List":
            i_sam_proj_data[key]["options"] = []
            for opt in item["sampleProjectOptionList"]:
                i_sam_proj_data[key]["options"].append(opt["optionValue"])
    if not MetadataVisualization.objects.filter(fill_mode="sample").exists():
        return {"ERROR": ERROR_FIELDS_FOR_METADATA_ARE_NOT_DEFINED}
    m_batch_objs = MetadataVisualization.objects.filter(fill_mode="batch").order_by(
        "order"
    )

    m_batch_form = {}
    field_data = {}
    for m_batch_obj in m_batch_objs:
        label = m_batch_obj.get_label()
        field_data[label] = {}

        if label in i_sam_proj_data:
            field_data[label]["format"] = i_sam_proj_data[label]["format"]
            if "options" in i_sam_proj_data[label]:
                field_data[label]["options"] = i_sam_proj_data[label]["options"]
        else:
            print("The field not be recorded in iSkyLIMS", label)

    m_batch_form["fields"] = field_data
    m_batch_form["username"] = user_obj.username
    m_batch_form["lab_name"] = get_lab_name(user_obj)

    sample_objs = TemporalSampleStorage.objects.filter(user=user_obj)
    for sample_obj in sample_objs:
        pass

    return m_batch_form


def create_form_for_sample(schema_obj):
    """Collect information from iSkyLIMS and from metadata table to
    create the metadata form for filling sample data
    """
    # schema_name = schema_obj.get_schema_name()
    m_form = OrderedDict()
    f_data = {}
    l_iskylims = []  # variable name in iSkyLIMS
    l_metadata = []  # label in the form
    if not MetadataVisualization.objects.filter(fill_mode="sample").exists():
        return {"ERROR": ERROR_FIELDS_FOR_METADATA_ARE_NOT_DEFINED}
    m_sam_objs = MetadataVisualization.objects.filter(fill_mode="sample").order_by(
        "order"
    )
    # schema_obj = m_sam_objs[0].get_schema_obj()
    schema_name = schema_obj.get_schema_name()
    # Get the properties in schema for mapping
    s_prop_objs = SchemaProperties.objects.filter(schemaID=schema_obj)
    s_prop_dict = {}
    for s_prop_obj in s_prop_objs:
        if s_prop_obj.get_ontology() == "0":
            continue
        s_prop_dict[s_prop_obj.get_ontology()] = {
            "label": s_prop_obj.get_label(),
            "format": s_prop_obj.get_format(),
        }

    # get the sample fields and sample project fields from iSkyLIMS
    try:
        iskylims_sample_raw = get_sample_fields_data()
    except AttributeError:
        return {"ERROR": ERROR_ISKYLIMS_NOT_REACHEABLE}
    if "ERROR" in iskylims_sample_raw:
        return iskylims_sample_raw

    # Remove the characters "schema" if exist in the name of the schema
    if "schema" in schema_name:
        schema_name = schema_name.replace("schema", "").strip()
    i_sam_proj_raw = get_sample_project_fields_data(schema_name)
    if "ERROR" in i_sam_proj_raw:
        return {
            "ERROR": ERROR_UNABLE_FETCH_SAMPLE_PROJECT_FIELDS + "for " + schema_name
        }
    i_sam_proj_data = {}
    # Format the information from sample Project to have label as key
    # format of the field and the option list in aa list
    for item in i_sam_proj_raw:
        key = item["sampleProjectFieldDescription"]
        i_sam_proj_data[key] = {}
        i_sam_proj_data[key]["format"] = item["sampleProjectFieldType"]
        if item["sampleProjectFieldType"] == "Options List":
            i_sam_proj_data[key]["options"] = []
            for opt in item["sampleProjectOptionList"]:
                i_sam_proj_data[key]["options"].append(opt["optionValue"])
    # Map fields using ontology
    iskylims_sample_data = {}
    for key, values in iskylims_sample_raw.items():
        if "ontology" in values:
            try:
                label = s_prop_dict[values["ontology"]]["label"]
                iskylims_sample_data[label] = {}
                # Collect information to send back the values to iSkyLIMS
                l_iskylims.append(values["field_name"])
                l_metadata.append(label)
                if "options" in values:
                    iskylims_sample_data[label]["options"] = values["options"]
            except KeyError as e:
                print("Error in map ontology ", e)

    # Prepare for each label the information to show in form
    # Exclude the Originating Laboratory because value is fetched from user
    # profilc.
    # Exclude Submitting Institution becaue it is fixed to ISCIII
    exclude_fields = ["Originating Laboratory", "Submitting Institution"]
    for m_sam_obj in m_sam_objs:
        label = m_sam_obj.get_label()
        if label in exclude_fields:
            continue
        m_form[label] = {}

        if label in i_sam_proj_data:
            m_form[label]["format"] = i_sam_proj_data[label]["format"]
            if "options" in i_sam_proj_data[label]:
                m_form[label]["options"] = i_sam_proj_data[label]["options"]
        elif label in iskylims_sample_data:
            if "options" in iskylims_sample_data[label]:
                m_form[label]["options"] = iskylims_sample_data[label]["options"]
        else:
            print("The field not be recorded in iSkyLIMS", label)
        if "date" in label.lower():
            m_form[label]["format"] = "date"
        # check label belongs to iskylims to get t
    f_data["heading"] = ",".join(list(m_form.keys()))
    f_data["data"] = m_form
    f_data["l_iskylims"] = ",".join(l_iskylims)
    f_data["l_metadata"] = ",".join(l_metadata)
    return f_data


def create_metadata_form(schema_obj, user_obj):
    """Collect information from iSkyLIMS and from metadata table to
    create the user metadata fom
    """
    # Check if Fields for metadata Form are defiened
    if not MetadataVisualization.objects.all().exists():
        return {"ERROR": ERROR_FIELDS_FOR_METADATA_ARE_NOT_DEFINED}
    m_form = {}
    m_form["sample"] = create_form_for_sample(schema_obj)
    if "ERROR" in m_form["sample"]:
        return m_form["sample"]
    m_form["username"] = user_obj.username
    m_form["lab_name"] = get_lab_name(user_obj)
    return m_form


def create_date_sample_bar(lab_sample):
    """Create bar graph where X-axis are the dates and Y-axis the number of
    samples
    """

    # df = pd.DataFrame(lab_sample, index=[0])
    col_names = ["Sequencing Date", "Value"]
    df = pd.DataFrame(lab_sample.items(), columns=col_names)

    options = {
        "title": "Samples received",
        "xaxis_title": "Sequencing date",
        "yaxis_title": "Number of samples",
        "height": "300",
        "width": 700,
    }
    bar_graph = histogram_graphic(df, col_names, options)
    # import pdb; pdb.set_trace()
    return bar_graph


def create_percentage_gauge_graphic(values):
    data = {}
    x = values["analized"] / values["received"] * 100
    data["value"] = float("{:.2f}".format(x))

    gauge_graph = gauge_graphic(data)
    return gauge_graph


def get_lab_last_actions(user_obj):
    actions = {}
    lab_name = get_lab_name(user_obj)
    last_sample_obj = Sample.objects.filter(
        collecting_institution__iexact=lab_name
    ).last()
    action_objs = DateUpdateState.objects.filter(sampleID=last_sample_obj)
    action_list = ["Defined", "Analysis", "Gisaid", "Ena"]
    for action_obj in action_objs:
        s_state = action_obj.get_state_name()
        if s_state in action_list:
            actions[s_state] = action_obj.get_date()
    return actions


def get_gisaid_info(sample_obj, schema_obj):
    """Get the Gisaid information that is stored for the sample"""
    gisaid_info = []
    field_objs = get_public_database_fields(schema_obj, "gisaid")
    if field_objs is None:
        return gisaid_info
    for field_obj in field_objs:
        label = field_obj.get_label_name()
        value = ""
        if PublicDatabaseValues.objects.filter(
            public_database_fieldID=field_obj, sampleID=sample_obj
        ).exists():
            value = (
                PublicDatabaseValues.objects.filter(
                    public_database_fieldID=field_obj, sampleID=sample_obj
                )
                .last()
                .get_value()
            )
        gisaid_info.append([label, value])
    return gisaid_info


def get_public_database_fields(schema_obj, db_type):
    """Return the fields allocated for databse type"""
    if PublicDatabaseFields.objects.filter(
        schemaID=schema_obj, database_type__public_type_name__iexact=db_type
    ).exists():
        return PublicDatabaseFields.objects.filter(
            schemaID=schema_obj, database_type__public_type_name__iexact=db_type
        )
    return None


def get_sample_display_data(sample_id, user):
    """Check if user is allow to see the data and if true collect all info
    from sample to display
    """
    sample_obj = get_sample_obj_from_id(sample_id)
    if sample_obj is None:
        return {"ERROR": ERROR_SAMPLE_DOES_NOT_EXIST}
    schema_obj = sample_obj.get_schema_obj()
    # Allow to see information obut sample to relecovManager
    group = Group.objects.get(name="RelecovManager")
    if group not in user.groups.all():
        lab_name = sample_obj.get_collecting_institution()
        if not Profile.objects.filter(user=user, laboratory__iexact=lab_name).exists():
            return {"ERROR": ERROR_NOT_ALLOWED_TO_SEE_THE_SAMPLE}

    s_data = {}
    s_data["basic"] = list(
        zip(HEADING_FOR_BASIC_SAMPLE_DATA, sample_obj.get_sample_basic_data())
    )
    s_data["fastq"] = list(
        zip(HEADING_FOR_FASTQ_SAMPLE_DATA, sample_obj.get_fastq_data())
    )
    # Fetch actions done on the sample
    if DateUpdateState.objects.filter(sampleID=sample_obj).exists():
        actions = []
        actions_date_objs = DateUpdateState.objects.filter(
            sampleID=sample_obj
        ).order_by("-date")
        for action_date_obj in actions_date_objs:
            actions.append(
                [action_date_obj.get_state_display_name(), action_date_obj.get_date()]
            )
        s_data["actions"] = actions
    # Fetch gisaid and ena information

    s_data["gisaid_data"] = get_gisaid_info(sample_obj, schema_obj)
    s_data["ena_data"] = []

    lab_sample = sample_obj.get_collecting_lab_sample_id()
    # Fetch information from iSkyLIMS
    if lab_sample != "":
        iskylims_data = get_sample_information(lab_sample)
        if "ERROR" not in iskylims_data:
            s_data["iskylims_basic"] = list(
                zip(iskylims_data["heading"], iskylims_data["s_basic"])
            )
            s_data["iskylims_p_data"] = list(
                zip(
                    iskylims_data["sample_project_field_heading"],
                    iskylims_data["sample_project_field_value"],
                )
            )
            s_data["iskylims_project"] = iskylims_data["sample_project_name"]
    return s_data


def get_sample_obj_from_sample_name(sample_name):
    """Return the sample instance from its name"""
    if Sample.objects.filter(sequencing_sample_id__iexact=sample_name).exists():
        return Sample.objects.filter(sequencing_sample_id__iexact=sample_name).last()
    return None


def get_sample_obj_from_id(sample_id):
    """Return the sample instance from its id"""
    if Sample.objects.filter(pk__exact=sample_id).exists():
        return Sample.objects.filter(pk__exact=sample_id).last()
    return None


def get_samples_count_per_schema(schema_name):
    """Get the number of samples that are stored in the schema"""
    return Sample.objects.filter(schema_obj__schema_name__iexact=schema_name).count()


def get_sample_per_date_per_lab(user_obj):
    """Get the historic of submitted sample, creating a dictionary with dates
    and number of samples
    """
    samples_per_date = OrderedDict()
    lab_name = get_lab_name(user_obj)
    s_dates = (
        Sample.objects.filter(collecting_institution__iexact=lab_name)
        .values_list("sequencing_date", flat=True)
        .distinct()
        .order_by("-sequencing_date")
    )
    for s_date in s_dates:
        date = datetime.strftime(s_date, "%d-%B-%Y")
        samples_per_date[date] = Sample.objects.filter(
            collecting_institution__iexact=lab_name, sequencing_date=s_date
        ).count()
    return samples_per_date


def get_sample_objs_per_lab(user_obj):
    lab_name = get_lab_name(user_obj)
    return Sample.objects.filter(collecting_institution__iexact=lab_name)


def get_search_data(user_obj):
    """Fetch data to show in form"""
    s_data = {}
    if Sample.objects.count() == 0:
        return {"ERROR": ERROR_NOT_SAMPLES_HAVE_BEEN_DEFINED}
    s_data["s_state"] = SampleState.objects.all().values_list("pk", "display_string")
    # Allow to search information from any laboratoryr
    group = Group.objects.get(name="RelecovManager")
    if group in user_obj.groups.all():
        s_data["labs"] = get_all_defined_labs()
    else:
        s_data["labs"] = get_lab_name(user_obj)

    return s_data


def get_user_id_from_collecting_institution(lab):
    """Use the laboratory name defined in the Profile to find out the user.
    if no user is not defined with this lab it retruns None
    """
    if Profile.objects.filter(laboratory__iexact=lab).exists():
        return Profile.objects.filter(laboratory__iexact=lab).last().user.pk
    return None


def join_sample_and_batch(b_data, user_obj, schema_obj):
    """Get the sample information stored on temporary tables and join with the
    batch data.
    """
    join_data = []
    sample_dict = {}
    if not TemporalSampleStorage.objects.filter(user=user_obj).exists():
        return {"ERROR": ERROR_SAMPLES_NOT_DEFINED_IN_FORM}
    field_list = list(
        MetadataVisualization.objects.filter(schemaID=schema_obj)
        .order_by("order")
        .values_list("label_name", flat=True)
    )
    join_data.append(field_list)
    t_sample_objs = TemporalSampleStorage.objects.filter(user=user_obj)
    for t_sample_obj in t_sample_objs:
        s_name = t_sample_obj.get_sample_name()
        if s_name not in sample_dict:
            sample_dict[s_name] = {}
        sample_dict[s_name].update(t_sample_obj.get_temp_values())

    for key in sample_dict.keys():
        row_data = []
        for field_name in field_list:
            if field_name in b_data:
                row_data.append(b_data[field_name])
            elif field_name in sample_dict[key]:
                row_data.append(sample_dict[key][field_name])
            else:
                print("error not defined", field_name, " for sample ", key)
                row_data.append("")
                import pdb

                pdb.set_trace()
        join_data.append(row_data)

    return join_data


def increase_unique_value(old_unique_number):
    """The function increases in one number the unique value
    If number reaches the 9999 then the letter is stepped
    """
    split_value = old_unique_number.split("-")
    number = int(split_value[1]) + 1
    letter = split_value[0]

    if number > 9999:
        number = 1
        index_letter = list(split_value[0])
        if index_letter[2] == "Z":
            if index_letter[1] == "Z":
                index_letter[0] = chr(ord(index_letter[0]) + 1)
                index_letter[1] = "A"
                index_letter[2] = "A"
            else:
                index_letter[1] = chr(ord(index_letter[1]) + 1)
                index_letter[2] = "A"

            index_letter = "".join(index_letter)
        else:
            index_letter[2] = chr(ord(index_letter[2]) + 1)

        letter = "".join(index_letter)

    number_str = str(number)
    number_str = number_str.zfill(4)
    return str(letter + "-" + number_str)


def pending_samples_in_metadata_form(user_obj):
    """Check if there are samples waiting to be completed for the metadata form"""
    if TemporalSampleStorage.objects.filter(user=user_obj).exists():
        return True
    return False


def search_samples(sample_name, lab_name, sample_state, s_date, user):
    """Search the samples that match with the query conditions"""
    sample_list = []
    sample_objs = Sample.objects.all()
    if lab_name != "":
        sample_objs = sample_objs.filter(collecting_institution__iexact=lab_name)
    if sample_name != "":
        if sample_objs.filter(sequencing_sample_id__iexact=sample_name).exists():
            sample_objs = sample_objs.filter(sequencing_sample_id__iexact=sample_name)
            if len(sample_objs) == 1:
                sample_list.append(sample_objs[0].get_sample_id())
                return sample_list

        elif sample_objs.filter(sequencing_sample_id__icontains=sample_name).exists():
            sample_objs = sample_objs.filter(
                sequencing_sample_id__icontains=sample_name
            )
            if len(sample_objs) == 1:
                sample_list.append(sample_objs[0].get_sample_id())
                return sample_list
        else:
            return sample_list
    if sample_state != "":
        sample_objs = sample_objs.filter(state__pk__exact=sample_state)
    if s_date != "":
        sample_objs = sample_objs.filter(created_at__exact=s_date)
    if len(sample_objs) == 1:
        sample_list.append(sample_objs[0].get_sample_id())
        return sample_list
    for sample_obj in sample_objs:
        sample_list.append(sample_obj.get_info_for_searching())
    return sample_list


def save_temp_sample_data(samples, user_obj):
    """Store the valid sample into the temporary table"""
    sample_saved_list = []
    for sample in samples:
        for item, value in sample.items():
            data = {"sample_name": sample[FIELD_FOR_GETTING_SAMPLE_ID]}
            data["field"] = item
            data["value"] = value
            data["user"] = user_obj
            TemporalSampleStorage.objects.save_temp_data(data)
        # Include Originating Laboratory and Submitting Institution

        sample_saved_list.append(sample[FIELD_FOR_GETTING_SAMPLE_ID])
    return


def update_temporary_sample_table(user_obj):
    """Set for all samples in the temporary table for the user that are sent
    to folder to start the process for validatation
    """
    if TemporalSampleStorage.objects.filter(user=user_obj).exists():
        t_sample_objs = TemporalSampleStorage.objects.filter(user=user_obj)
        for t_sample_obj in t_sample_objs:
            t_sample_obj.update_sent_status()
    return True


def write_form_data_to_excel(data, user_obj):
    """Write data to excel using relecov-tools"""
    folder_tmp = os.path.join(settings.MEDIA_ROOT, "tmp")
    os.makedirs(folder_tmp, exist_ok=True)
    f_name = os.path.join(folder_tmp, "Metadata_lab_" + user_obj.username + ".xlsx")
    write_to_excel_file(data, f_name, "METADATA_LAB", True)
    return
