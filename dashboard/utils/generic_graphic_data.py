# Local imports
import dashboard.models


"""
def get_graphic_in_data_frame(graphic_name):
    Collect the pre-processed data from database and return in panda's
    dataFrame
    if GraphicName.objects.filter(graphic_name__iexact=graphic_name).exists():
        graphic_name_obj = GraphicName.objects.filter(
            graphic_name__iexact=graphic_name
        ).last()
        fields = GraphicField.objects.filter(graphic=graphic_name_obj).values_list(
            "field_1", "field_2", "field_3"
        )[0]
        values = list(
            GraphicValue.objects.filter(graphic=graphic_name_obj).values_list(
                "value_1", "value_2", "value_3"
            )
        )
        return pd.DataFrame(values, columns=fields)

    return None
"""


def get_graphic_json_data(graphic_name):
    """ """
    if dashboard.models.GraphicJsonFile.objects.filter(
        graphic_name__exact=graphic_name
    ).exists():
        json_data = (
            dashboard.models.GraphicJsonFile.objects.filter(
                graphic_name__exact=graphic_name
            )
            .last()
            .get_json_data()
        )
        if not json_data:
            return None
        else:
            return json_data
    return None
