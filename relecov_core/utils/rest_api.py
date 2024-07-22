# Generic imports
import json
import relecov_tools.rest_api

# Local imports
import relecov_core.utils.generic_functions
import relecov_core.config


def create_get_api_instance(request_param, data):
    """Crate api request to iSkyLIMS"""
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    if isinstance(data, dict):
        request = request_param[0]
        param = data
    else:
        request, param = request_param
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    return r_api.get_request(request, param, data)


def fetch_samples_on_condition(request_param):
    """Send request to get the list of samples that for a specific parameter
    has a condition. If no filter condition is given it returns grouping the
    samples for each defined value of the parameter
    """
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request, param = relecov_core.config.ISKLIMS_FETCH_SAMPLES_ON_CONDITION
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    data = r_api.get_request(request, param, request_param)
    if "ERROR" in data:
        return {"ERROR": data}
    return data


def get_laboratory_data(lab_name):
    """Send api request to iSkyLIMS to fetch laboratory data"""

    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request, param = relecov_core.config.ISKLIMS_GET_LABORATORY_PARAMETERS
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    data = r_api.get_request(request, param, lab_name)
    if "ERROR" in data:
        return {"ERROR": data}
    return data


def get_user_credentials():
    """Fetch the user and password taht are stored in database"""
    credentials = {}
    credentials["user"] = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_USER"
    )
    credentials["pass"] = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_PASSWORD"
    )
    return credentials


def set_laboratory_data(lab_data):
    """Send api request to iSkyLIMS to update laboratory data"""

    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API

    request = relecov_core.config.ISKLIMS_PUT_LABORATORY_PARAMETER
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    credentials = get_user_credentials()
    data = r_api.put_request(lab_data, credentials, request)
    if "ERROR" in data:
        return {"ERROR": data}
    return data


def get_sample_fields_data():
    """Send API request to iSkyLIMs to get the sample_fields and their options"""
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request = relecov_core.config.ISKLIMS_GET_SAMPLE_FIELDS
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    data = r_api.get_request(request, "", "")
    if "ERROR" in data:
        return data
    return data["DATA"]


def get_sample_information(sample_name):
    """Send APY request to iSkyLIMS to get sample and sample project information"""
    """
    iskylims_server = get_configuration_value("ISKYLIMS_SERVER")
    iskylims_url = ISKLIMS_REST_API
    request = ISKLIMS_GET_SAMPLE_INFORMATION
    r_api = RestApi(iskylims_server, iskylims_url)
    """
    data = create_get_api_instance(
        relecov_core.config.ISKLIMS_GET_SAMPLE_INFORMATION, sample_name
    )
    # data = r_api.get_request(request, sample_name)
    if "ERROR" in data:
        return {"ERROR": data}
    return data["DATA"]


def get_sample_parameter_data(param_data):
    if isinstance(param_data, dict):
        data = create_get_api_instance(
            relecov_core.config.ISKLIMS_GET_SAMPLE_PROJECT_PARAMETER_INFORMATION,
            param_data,
        )
    else:
        data = create_get_api_instance(
            relecov_core.config.ISKLIMS_GET_SAMPLE_PARAMETER_INFORMATION, param_data
        )
    # data = r_api.get_request(request, sample_name)
    if "ERROR" in data:
        return {"ERROR": data}
    return data["DATA"]


def get_sample_project_fields_data(project):
    """Send API request to iSkyLIMS to get the sample project fields and their
    options
    """
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request, param = relecov_core.config.ISKLIMS_GET_SAMPLE_PROJECT_FIELDS
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    data = r_api.get_request(request, param, project)
    if "ERROR" in data:
        return {"ERROR": data}
    return data["DATA"]


def get_summarize_data(param_data):
    """Send API request to iSkyLIMS to get the summarize data options"""
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request = relecov_core.config.ISKLIMS_GET_SUMMARIZE_DATA
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    data = r_api.get_request(request, param_data)
    if "ERROR" in data:
        return data
    return data["DATA"]


def get_stats_data(param_data):
    """Send API request to iSkyLIMS to get the stats data"""
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request = relecov_core.config.ISKLIMS_GET_STATS_DATA
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)
    data = r_api.get_request(request, param_data)
    if "ERROR" in data:
        return data
    return data["DATA"]


def save_sample_form_data(post_data, credencials):
    """Send POST API request to iSkyLIMS to save sample data"""
    iskylims_server = relecov_core.utils.generic_functions.get_configuration_value(
        "ISKYLIMS_SERVER"
    )
    iskylims_url = relecov_core.config.ISKLIMS_REST_API
    request = relecov_core.config.ISKLIMS_POST_SAMPLE_DATA
    r_api = relecov_tools.rest_api.RestApi(iskylims_server, iskylims_url)

    data = r_api.post_request(json.dumps(post_data), credencials, request)
    if "ERROR" in data:
        return data
    return data["DATA"]
