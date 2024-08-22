# Generic imports
import json
from django.db import DataError

# Local imports
import core.models
import core.utils.generic_functions
import core.config


def get_metadata_json_data(metadata_id):
    """Get the properties defined for the schema"""
    metadata_obj = get_metadata_obj_from_id(metadata_id)
    if metadata_obj is None:
        return {"ERROR": core.config.ERROR_SCHEMA_ID_NOT_DEFINED}
    metadata_data = {"s_data": []}
    if core.models.MetadataProperties.objects.filter(
        metadataID=metadata_obj
    ).exists():
        s_prop_objs = core.models.MetadataProperties.objects.filter(
            metadataID=metadata_obj
        ).order_by("property")
        metadata_data["heading"] = core.config.HEADING_SCHEMA_DISPLAY
        for s_prop_obj in s_prop_objs:
            metadata_data["s_data"].append(s_prop_obj.get_property_info())
    return metadata_data


def get_metadata_json_loaded(apps_name):
    """Return the defined metadata"""
    s_data = []
    if core.models.Metadata.objects.filter(
        metadata_apps_name__exact=apps_name
    ).exists():
        metadata_objs = core.models.Metadata.objects.filter(
            metadata_apps_name__exact=apps_name
        ).order_by("metadata_name")
        for metadata_obj in metadata_objs:
            s_data.append(metadata_obj.get_metadata_info())
    return s_data


def get_metadata_obj_from_id(metadata_id):
    """Get the metadata instance from id"""
    if core.models.Metadata.objects.filter(pk__exact=metadata_id).exists():
        return core.models.Metadata.objects.filter(pk__exact=metadata_id).last()
    return None


def load_metadata_json(json_file):
    """Store json file in the defined folder and store information in database"""
    data = {}
    try:
        data["full_metadata_json"] = json.load(json_file)
    except json.decoder.JSONDecodeError:
        return {"ERROR": core.config.ERROR_INVALID_JSON}
    data["file_name"] = core.utils.generic_functions.store_file(
        json_file, core.config.METADATA_JSON_UPLOAD_FOLDER
    )
    return data


def check_heading_valid_json(metadata_data, m_structure):
    """Check if json have at least the main structure"""
    for item in m_structure:
        try:
            metadata_data[item]
        except KeyError:
            return False
    return True


def store_metadata_properties(metadata_obj, s_properties):
    """Store the properties defined in the metadata"""
    for prop_key in s_properties.keys():
        data = dict(s_properties[prop_key])
        data["metadataID"] = metadata_obj
        data["property"] = prop_key
        try:
            core.models.MetadataProperties.objects.create_new_property(data)
        except (KeyError, DataError) as e:
            print(prop_key, " error ", e)
    return {"SUCCESS": ""}


def remove_existing_default_metadata(metadata_name, apps_name):
    """Remove the tag for default schema for the given schema name"""
    if core.models.Metadata.objects.filter(
        metadata_name__iexact=metadata_name,
        metadata_apps_name=apps_name,
        metadata_default=True,
    ).exists():
        metadata_obj = core.models.Metadata.objects.filter(
            metadata_name__iexact=metadata_name,
            metadata_apps_name=apps_name,
            metadata_default=True,
        ).last()
        metadata_obj.update_default(False)
    return


def process_metadata_json_file(json_file, version, default, user, apps_name):
    """Check json file and store in database"""
    metadata_data = load_metadata_json(json_file)

    if "ERROR" in metadata_data:
        return metadata_data

    # store root data of json schema

    structure = [
        "properties",
    ]
    if not check_heading_valid_json(metadata_data["full_metadata_json"], structure):
        return {"ERROR": core.config.ERROR_INVALID_SCHEMA}

    metadata_name = metadata_data["full_metadata_json"]["project"]

    if default == "on":
        remove_existing_default_metadata(metadata_name, apps_name)
        default = True
    else:
        default = False

    if core.models.Metadata.objects.filter(
        metadata_name__iexact=metadata_name,
        metadata_version__iexact=version,
        metadata_apps_name__exact=apps_name,
    ).exists():
        return {"ERROR": core.config.ERROR_SCHEMA_ALREADY_LOADED}

    data = {
        "file_name": metadata_data["file_name"],
        "user_name": user,
        "metadata_name": metadata_name,
        "metadata_version": version,
        "metadata_default": default,
        "metadata_app_name": apps_name,
        "user_name": user,
    }
    new_metadata = core.models.Metadata.objects.create_new_metadata(data)

    result = store_metadata_properties(
        new_metadata,
        metadata_data["full_metadata_json"]["properties"],
        # metadata_data["full_metadata_json"]["required"],
    )
    if "ERROR" in result:
        return result

    return {"SUCCESS": core.config.METADATA_JSON_SUCCESSFUL_LOAD}
