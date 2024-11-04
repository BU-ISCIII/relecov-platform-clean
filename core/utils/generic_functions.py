# Generic imports
import time
import os
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.conf import settings

# local imports
import core.models


def get_configuration_value(parameter_name):
    """
    Description:
        Function will get the parameter value defined in the configutration table
        if not exists return 'False'

    Input:
        parameter_name    #parameter name
    Return:
        parameter_value
    """

    parameter_value = "False"
    if core.models.ConfigSetting.objects.filter(
        configuration_name__exact=parameter_name
    ).exists():
        parameter_obj = core.models.ConfigSetting.objects.filter(
            configuration_name__exact=parameter_name
        ).last()
        parameter_value = parameter_obj.get_configuration_value()
    return parameter_value


def get_defined_users():
    """Get the id and the user names defined in relecov"""
    user_list = []
    user_objs = (
        User.objects.all().exclude(username__iexact="admin").order_by("username")
    )
    for user_obj in user_objs:
        user_list.append([user_obj.pk, user_obj.username])
    return user_list


def store_file(user_file, folder):
    """
    Description:
        The function save the user input file
    Input:
        user_file # contains the file
        folder      subfolder to store the file
    Return:
        file_name
    """
    filename, file_extension = os.path.splitext(user_file.name)
    file_name = filename + "_" + str(time.strftime("%Y%m%d-%H%M%S")) + file_extension
    store_filepath = os.path.join(folder, file_name)
    fs = FileSystemStorage()
    fs.save(store_filepath, user_file)
    return store_filepath


def check_valid_date_format(date):
    """check it date has a valid format"""
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
