from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    api_view,
    # action,
    #    parser_classes,
)
from rest_framework import status
from rest_framework.response import Response
from django.http import QueryDict
from relecov_core.api.serializers import (
    CrateAnalysisForSampleSerilizer,
    CreateDateAfterChangeStateSerializer,
    CreateSampleSerializer,
    CreateAuthorSerializer,
    CreateGisaidSerializer,
    CreateEnaSerializer,
    UpdateSampleSerializer,
)

from relecov_core.api.utils.long_table_handling import fetch_long_table_data
from relecov_core.api.utils.sample_handling import (
    check_if_sample_exists,
    split_sample_data,
)
from relecov_core.api.utils.bioinfo_metadata_handling import (
    split_bioinfo_data,
    store_bioinfo_data,
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from relecov_core.models import Sample, SampleState, Error, EnaInfo

from relecov_core.api.utils.accession_to_ENA import (
    date_converter,
    extract_number_of_sample,
)  # parse_xml,

from relecov_core.api.utils.common_functions import (
    get_schema_version_if_exists,
    get_sample_obj_if_exists,
    get_analysis_type_id,
)

from relecov_core.core_config import (
    ERROR_SAMPLE_NAME_NOT_INCLUDED,
    ERROR_SAMPLE_NOT_DEFINED,
)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "analysis_authors": openapi.Schema(
                type=openapi.TYPE_STRING, description="Author of the analysis"
            ),
            "author_submitter": openapi.Schema(
                type=openapi.TYPE_STRING, description="Submitter author to GISAID"
            ),
            "authors": openapi.Schema(
                type=openapi.TYPE_STRING, description="Authors involved in the analysis"
            ),
            "experiment_alias": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Experiment alias used for uploading to ENA",
            ),
            "experiment_title": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Experiment title for uploading to ENA",
            ),
            "fastq_r1_md5": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="MD5 for fastq R1 file",
            ),
            "fastq_r2_md5": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="MD5 for fastq R2 file",
            ),
            "gisaid_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Id given by GISAID",
            ),
            "microbiology_lab_sample_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Sample name ID given by the microbiology lab ",
            ),
            "r1_fastq_filepath": openapi.Schema(
                type=openapi.TYPE_STRING, description="Path where fastq R1 is stored"
            ),
            "r2_fastq_filepath": openapi.Schema(
                type=openapi.TYPE_STRING, description="Path where fastq R2 is stored"
            ),
            "sequence_file_R1_fastq": openapi.Schema(
                type=openapi.TYPE_STRING, description="File name of fastq R1"
            ),
            "sequence_file_R2_fastq": openapi.Schema(
                type=openapi.TYPE_STRING, description="File name of fastq R2"
            ),
            "sequencing_sample_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Project name"
            ),
            "study_alias": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Study alias used for uplading to ENA",
            ),
            "study_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Study ID for uploading to ENA"
            ),
            "study_title": openapi.Schema(
                type=openapi.TYPE_STRING, description="Study title for uploading to ENA"
            ),
            "study_type": openapi.Schema(
                type=openapi.TYPE_STRING, description="Study type for uploading to ENA"
            ),
            "submitting_lab_sample_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="sample name id given by the submitted lab",
            ),
        },
    ),
    responses={
        201: "Successful create information",
        400: "Bad Request",
        500: "Internal Server Error",
    },
)
@authentication_classes([SessionAuthentication, BasicAuthentication])
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_sample_data(request):
    if request.method == "POST":
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        schema_obj = get_schema_version_if_exists(data)
        if schema_obj is None:
            error = {"ERROR": "schema name and version is not defined"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        # check if sample is alrady defined
        if "sequencing_sample_id" not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if check_if_sample_exists(data["sequencing_sample_id"]):
            error = {"ERROR": "sample already defined"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        data["user"] = request.user.pk
        split_data = split_sample_data(data)
        if "ERROR" in split_data:
            return Response(split_data, status=status.HTTP_400_BAD_REQUEST)
        if split_data["author"]["authors"] != "":
            author_serializer = CreateAuthorSerializer(data=split_data["author"])
            if not author_serializer.is_valid():
                return Response(
                    author_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            author_serializer = None
        if "EPI_" in split_data["gisaid"]["gisaid_id"]:
            gisaid_serializer = CreateGisaidSerializer(data=split_data["gisaid"])
            if not gisaid_serializer.is_valid():
                return Response(
                    gisaid_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            gisaid_serializer = None
        if split_data["ena"]["biosample_accession_ENA"] != "":
            ena_serializer = CreateEnaSerializer(data=split_data["ena"])
            if not ena_serializer.is_valid():
                return Response(
                    ena_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            ena_serializer = None
        # Store authors, gisaid, ena in ddbb to get the references
        if author_serializer:
            split_data["sample"][
                "authors_obj"
            ] = author_serializer.save().get_author_obj()
        else:
            split_data["sample"]["authors_obj"] = None
        if gisaid_serializer:
            split_data["sample"][
                "gisaid_obj"
            ] = gisaid_serializer.save().get_gisaid_obj()
        else:
            split_data["sample"]["gisaid_obj"] = None
        if ena_serializer:
            split_data["sample"]["ena_obj"] = ena_serializer.save().get_ena_obj()
        else:
            split_data["sample"]["ena_obj"] = None
        split_data["sample"]["schema_obj"] = schema_obj.get_schema_id()
        sample_serializer = CreateSampleSerializer(data=split_data["sample"])
        if not sample_serializer.is_valid():
            return Response(
                sample_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        sample_obj = sample_serializer.save()
        # update sample state date
        data = {
            "sampleID": sample_obj.get_sample_id(),
            "stateID": split_data["sample"]["state"],
        }
        date_serilizer = CreateDateAfterChangeStateSerializer(data=data)
        if date_serilizer.is_valid():
            date_serilizer.save()
        return Response("Successful upload information", status=status.HTTP_201_CREATED)


y_param = openapi.Parameter("y", "query", openapi.IN_FORM, type=openapi.TYPE_STRING)


@api_view(["POST"])
def create_bioinfo_metadata(request):
    if request.method == "POST":
        data = request.data

    if isinstance(data, QueryDict):
        data = data.dict()
    # check schema (name and version)
    schema_obj = get_schema_version_if_exists(data)
    if schema_obj is None:
        error = {"ERROR": "schema name and version is not defined"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    if "sample_name" not in data:
        return Response(
            {"ERROR": ERROR_SAMPLE_NAME_NOT_INCLUDED},
            status=status.HTTP_400_BAD_REQUEST,
        )
    sample_obj = get_sample_obj_if_exists(data)
    if sample_obj is None:
        return Response(
            {"ERROR": ERROR_SAMPLE_NOT_DEFINED}, status=status.HTTP_400_BAD_REQUEST
        )
    split_data = split_bioinfo_data(data, schema_obj)
    if "ERROR" in split_data:
        return Response(split_data, status=status.HTTP_400_BAD_REQUEST)

    stored_data = store_bioinfo_data(split_data, schema_obj)
    if "ERROR" in stored_data:
        return Response(stored_data, status=status.HTTP_400_BAD_REQUEST)
    state_id = SampleState.objects.filter(state__exact="Bioinfo").last().get_state_id()
    data_date = {"sampleID": sample_obj.get_sample_id(), "stateID": state_id}

    # update sample state
    sample_obj.update_state("Bioinfo")
    # Include date and state in DateState table
    date_serializer = CreateDateAfterChangeStateSerializer(data=data_date)
    if date_serializer.is_valid():
        date_serializer.save()

    analysis_data = {
        "sampleID": sample_obj.get_sample_id(),
        "typeID": get_analysis_type_id("bioinfo_analysis"),
    }
    analysis_serializer = CrateAnalysisForSampleSerilizer(data=analysis_data)

    if analysis_serializer.is_valid():
        analysis_serializer.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(["POST"])
def create_variant_data(request):
    if request.method == "POST":
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()

        # sample_obj = get_sample(data)
        sample_obj = get_sample_obj_if_exists(data)
        if sample_obj is None:
            return Response(
                {"ERROR": ERROR_SAMPLE_NOT_DEFINED}, status=status.HTTP_400_BAD_REQUEST
            )

        stored_data = fetch_long_table_data(data, sample_obj)

        if "ERROR" in stored_data:
            return Response(stored_data, status=status.HTTP_400_BAD_REQUEST)

        analysis_data = {
            "sampleID": sample_obj.get_sample_id(),
            "typeID": get_analysis_type_id("variant_analysis"),
        }
        analysis_serializer = CrateAnalysisForSampleSerilizer(data=analysis_data)

        if analysis_serializer.is_valid():
            analysis_serializer.save()

        return Response(status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="put",
    operation_description="The PUT method is used to update existing records in the database.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "sample": openapi.Schema(
                type=openapi.TYPE_STRING, description="Number of Sample"
            ),
            "state": openapi.Schema(
                type=openapi.TYPE_STRING, description="Sample Status"
            ),
            "error_type": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="(Optional) If the status of the sample is ERROR, error_type tells us what type of error it is.",
            ),
        },
    ),
    responses={
        201: "Successful create information",
        400: "Bad Request",
        500: "Internal Server Error",
    },
)
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_state(request):
    data_date = {}

    if request.method == "PUT":
        data = request.data

        if isinstance(data, QueryDict):
            data = data.dict()

        data["user"] = request.user.pk

        # if state exists,
        if SampleState.objects.filter(state=data["state"]).exists():
            data["state"] = SampleState.objects.filter(state=data["state"]).last().pk
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data["sequencing_sample_id"] = data["sample"]

        if "error_type" in data:
            data["error_type"] = (
                Error.objects.filter(error_name=data["error_type"]).last().pk
            )

        # if sample exists, create an instance of existing sample.
        if Sample.objects.filter(
            sequencing_sample_id=data["sample"], user=request.user
        ).exists():
            sample_instance = Sample.objects.filter(
                sequencing_sample_id=data["sample"]
            ).last()

            sample_serializer = UpdateSampleSerializer(sample_instance, data=data)
        # if sample does not exist, create a new sample register.
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not sample_serializer.is_valid():
            return Response(
                sample_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        sample_serializer.save()

        data_date["stateID"] = SampleState.objects.filter(
            pk__exact=data["state"]
        ).last()
        data_date["sampleID"] = Sample.objects.filter(
            sequencing_sample_id=sample_instance
        )

        CreateDateAfterChangeStateSerializer(data_date)

        return Response("Successful upload information", status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="post",
    operation_description="The POST method is used to create new records in the database.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "SRA_accession": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Code provided by ENA after uploading samples",
            ),
            "ena_process_date": openapi.Schema(
                type=openapi.TYPE_STRING, description="Upload date to ENA"
            ),
            "GenBank_ENA_DDBJ_accession": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="",
            ),
            "study_alias": openapi.Schema(type=openapi.TYPE_STRING, description=""),
            "study_id": openapi.Schema(type=openapi.TYPE_STRING, description=""),
            "study_title": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="",
            ),
            "study_type": openapi.Schema(type=openapi.TYPE_STRING, description=""),
            "experiment_alias": openapi.Schema(
                type=openapi.TYPE_STRING, description=""
            ),
            "experiment_title": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="",
            ),
        },
    ),
    responses={
        201: "Successful create information",
        400: "Bad Request",
        500: "Internal Server Error",
    },
)
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def accession_ena(request):
    if request.method == "POST":
        data = request.data

        if isinstance(data, QueryDict):
            data = data.dict()

        number_of_sample = extract_number_of_sample(data["GenBank_ENA_DDBJ_accession"])

        data["user"] = request.user.pk
        process_date = date_converter(data["ena_process_date"])

        if EnaInfo.objects.filter(SRA_accession=data["SRA_accession"]).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            ena_obj = EnaInfo.objects.create(
                ena_process_date=process_date,
                SRA_accession=data["SRA_accession"],
                GenBank_ENA_DDBJ_accession=data["GenBank_ENA_DDBJ_accession"],
            )
            sample_obj = Sample.objects.filter(
                sequencing_sample_id=number_of_sample
            ).last()

            ena_obj = EnaInfo.objects.filter(SRA_accession=data["SRA_accession"]).last()
            sample_obj.ena_obj = ena_obj

            sample_obj.save()

    return Response("Successful upload information", status=status.HTTP_201_CREATED)
