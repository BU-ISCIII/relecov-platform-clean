from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from relecov_core.core_config import (
    SCHEMAS_UPLOAD_FOLDER,
    METADATA_UPLOAD_FOLDER,
    BIOINFO_METADATA_UPLOAD_FOLDER,
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    laboratory = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        db_table = "Profile"

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Document(models.Model):
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=200)
    uploadedFile = models.FileField(upload_to=METADATA_UPLOAD_FOLDER)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "Document"

    def __str__(self):
        return "%s" % (self.title)


class BioinfoMetadataFile(models.Model):
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=200)
    uploadedFile = models.FileField(upload_to=BIOINFO_METADATA_UPLOAD_FOLDER)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "BioinfoMetadataFile"

    def __str__(self):
        return "%s" % (self.title)

    def get_title(self):
        return "%s" % (self.title)

    def get_file_path(self):
        return "%s" % (self.file_path)

    def get_uploaded_file(self):
        return "%s" % (self.uploadedFile)


class SchemaManager(models.Manager):
    def create_new_schema(self, data):
        new_schema = self.create(
            file_name=data["file_name"],
            user_name=data["user_name"],
            schema_name=data["schema_name"],
            schema_version=data["schema_version"],
            schema_default=data["schema_default"],
            schema_in_use=True,
            schema_apps_name=data["schema_app_name"],
        )
        return new_schema


class Schema(models.Model):
    file_name = models.FileField(upload_to=SCHEMAS_UPLOAD_FOLDER)
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    schema_name = models.CharField(max_length=40)
    schema_version = models.CharField(max_length=10)
    schema_in_use = models.BooleanField(default=True)
    schema_default = models.BooleanField(default=True)
    schema_apps_name = models.CharField(max_length=40, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "Schema"

    def __str__(self):
        return "%s_%s" % (self.schema_name, self.schema_version)

    def get_schema_and_version(self):
        return "%s_%s" % (self.schema_name, self.schema_version)

    def get_schema_name(self):
        return "%s" % (self.schema_name)

    def get_schema_id(self):
        return "%s" % (self.pk)

    def get_schema_info(self):
        data = []
        data.append(self.pk)
        data.append(self.schema_name)
        data.append(self.schema_version)
        data.append(self.schema_default)
        data.append(str(self.schema_in_use))
        data.append(self.file_name)
        return data

    def update_default(self, default):
        self.schema_default = default
        self.save()

    objects = SchemaManager()


class ClassificationManager(models.Manager):
    def create_new_classification(self, classification_name):
        new_class_obj = self.create(classification_name=classification_name)
        return new_class_obj


class Classification(models.Model):
    classification_name = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "Classification"

    def __str__(self):
        return "%s" % (self.classification_name)

    def get_classification_id(self):
        return "%s" % (self.pk)

    def get_classification_name(self):
        return "%s" % (self.classification_name)

    objects = ClassificationManager()


class SchemaPropertiesManager(models.Manager):
    def create_new_property(self, data):
        required = True if "required" in data else False
        options = True if "options" in data else False
        format = data["format"] if "format" in data else None
        if Classification.objects.filter(
            classification_name__iexact=data["classification"]
        ).exists():
            classification_id = Classification.objects.filter(
                classification_name=data["classification"]
            ).last()
        else:
            classification_id = Classification.objects.create_new_classification(
                data["classification"]
            )

        new_property_obj = self.create(
            schemaID=data["schemaID"],
            property=data["property"],
            examples=data["examples"],
            ontology=data["ontology"],
            type=data["type"],
            description=data["description"],
            label=data["label"],
            classificationID=classification_id,
            fill_mode=data["fill_mode"],
            required=required,
            options=options,
            format=format,
        )
        return new_property_obj


class SchemaProperties(models.Model):
    schemaID = models.ForeignKey(Schema, on_delete=models.CASCADE)
    classificationID = models.ForeignKey(
        Classification, on_delete=models.CASCADE, null=True, blank=True
    )
    property = models.CharField(max_length=50)
    examples = models.CharField(max_length=200, null=True, blank=True)
    ontology = models.CharField(max_length=40, null=True, blank=True)
    type = models.CharField(max_length=20)
    format = models.CharField(max_length=20, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    required = models.BooleanField(default=False)
    options = models.BooleanField(default=False)
    fill_mode = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "SchemaProperties"

    def __str__(self):
        return "%s" % (self.property)

    def get_property_name(self):
        return "%s" % (self.property)

    def get_property_id(self):
        return "%s" % (self.pk)

    def get_property_info(self):
        if self.classificationID:
            classification = self.classificationID.get_classification_name()
        else:
            classification = ""
        data = []
        data.append(self.property)
        data.append(self.label)
        data.append(self.required)
        data.append(classification)
        data.append(self.description)
        return data

    def has_options(self):
        return self.options

    def get_label(self):
        return "%s" % (self.label)

    def get_format(self):
        return "%s" % (self.format)

    def get_ontology(self):
        return "%s" % (self.ontology)

    def get_fill_mode(self):
        return "%s" % (self.fill_mode)

    objects = SchemaPropertiesManager()


class PropertyOptionsManager(models.Manager):
    def create_property_options(self, data):
        new_property_option_obj = self.create(
            propertyID=data["propertyID"],
            enums=data["enums"],
            ontology=data["ontology"],
        )
        return new_property_option_obj


class PropertyOptions(models.Model):
    propertyID = models.ForeignKey(SchemaProperties, on_delete=models.CASCADE)
    enums = models.CharField(max_length=80, null=True, blank=True)
    ontology = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        db_table = "PropertyOptions"

    def __str__(self):
        return "%s" % (self.enums)

    def get_enum(self):
        return "%s" % (self.enums)

    objects = PropertyOptionsManager()


# Metadata_json
class MetadataVisualizationManager(models.Manager):
    def create_metadata_visualization(self, data):
        new_met_visual = self.create(
            schemaID=data["schema_id"],
            property_name=data["property_name"],
            label_name=data["label_name"],
            order=data["order"],
            in_use=data["in_use"],
            fill_mode=data["fill_mode"],
        )
        return new_met_visual


class MetadataVisualization(models.Model):
    schemaID = models.ForeignKey(Schema, on_delete=models.CASCADE)
    property_name = models.CharField(max_length=60)
    label_name = models.CharField(max_length=80)
    order = models.IntegerField()
    in_use = models.BooleanField(default=True)
    fill_mode = models.CharField(max_length=40)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "MetadataVisualization"

    def __str__(self):
        return "%s" % (self.label_name)

    def get_label(self):
        return "%s" % (self.label_name)

    def get_property(self):
        return "%s" % (self.property_name)

    def get_order(self):
        return "%s" % (self.order)

    def get_schema_obj(self):
        return self.schemaID

    objects = MetadataVisualizationManager()


class BioinfoAnalysisFieldManager(models.Manager):
    def create_new_field(self, data):
        new_field = self.create(
            classificationID=data["classificationID"],
            property_name=data["property_name"],
            label_name=data["label_name"],
        )
        return new_field


class BioinfoAnalysisField(models.Model):
    schemaID = models.ManyToManyField(Schema)
    classificationID = models.ForeignKey(Classification, on_delete=models.CASCADE)
    property_name = models.CharField(max_length=60)
    label_name = models.CharField(max_length=80)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "BioinfoAnalysisField"

    def __str__(self):
        return "%s" % (self.property_name)

    def get_id(self):
        return "%s" % (self.pk)

    def get_property(self):
        return "%s" % (self.property_name)

    def get_label(self):
        return "%s" % (self.label_name)

    def get_classification_name(self):
        if self.classificationID is not None:
            return self.classificationID.get_classification()
        return None

    objects = BioinfoAnalysisFieldManager()


class BioInfoAnalysisValueManager(models.Manager):
    def create_new_value(self, data):
        new_value = self.create(
            value=data["value"],
            bioinfo_analysis_fieldID=data["bioinfo_analysis_fieldID"],
            sampleID_id=data["sampleID_id"],
        )
        return new_value


class BioInfoAnalysisValue(models.Model):
    value = models.CharField(max_length=240)
    bioinfo_analysis_fieldID = models.ForeignKey(
        BioinfoAnalysisField, on_delete=models.CASCADE
    )
    # sampleID_id = models.ForeignKey(Sample, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "BioInfoAnalysisValue"

    def __str__(self):
        return "%s" % (self.value)

    def get_value(self):
        return "%s" % (self.value)

    def get_id(self):
        return "%s" % (self.pk)

    def get_b_process_field_id(self):
        return "%s" % (self.bioinfo_analysis_fieldID)


class LineageInfo(models.Model):
    lineage_name = models.CharField(max_length=100)
    pango_lineages = models.CharField(max_length=100)
    variant_name = models.CharField(max_length=100)
    nextclade = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "LineageInfo"

    def __str__(self):
        return "%s" % (self.lineage_name)

    def get_lineage_name(self):
        return "%s" % (self.lineage_name)

    def get_lineage_id(self):
        return "%s" % (self.pk)


class LineageFieldsManager(models.Manager):
    def create_new_field(self, data):
        new_field = self.create(
            classificationID=data["classificationID"],
            property_name=data["property_name"],
            label_name=data["label_name"],
        )
        return new_field


class LineageFields(models.Model):
    schemaID = models.ManyToManyField(Schema)
    classificationID = models.ForeignKey(Classification, on_delete=models.CASCADE)
    property_name = models.CharField(max_length=60)
    label_name = models.CharField(max_length=80)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "LineageFields"

    def __str__(self):
        return "%s" % (self.property_name)

    def get_lineage_property_name(self):
        return "%s" % (self.property_name)

    def get_lineage_field_id(self):
        return "%s" % (self.pk)

    objects = LineageFieldsManager()


class LineageValues(models.Model):
    # sampleID_id = models.ForeignKey(Sample, on_delete=models.CASCADE)
    lineage_fieldID = models.ForeignKey(LineageFields, on_delete=models.CASCADE)
    value = models.CharField(max_length=240)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "LinageValue"

    def __str__(self):
        return "%s" % (self.value)

    def get_value(self):
        return "%s" % (self.value)

    def get_id(self):
        return "%s" % (self.pk)

    def get_lineage_field(self):
        return "%s" % (self.lineage_fieldID)


class OrganismAnnotationManger(models.Manager):
    def create_new_annotation(self, data):
        new_annotation = self.create(
            user=data["user"],
            gff_version=data["gff_version"],
            gff_spec_version=data["gff_spec_version"],
            sequence_region=data["sequence_region"],
            organism_code=data["organism_code"],
            organism_code_version=data["organism_code_version"],
        )
        return new_annotation


class OrganismAnnotation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    gff_version = models.CharField(max_length=5)
    gff_spec_version = models.CharField(max_length=10)
    sequence_region = models.CharField(max_length=30)
    organism_code = models.CharField(max_length=20)
    organism_code_version = models.CharField(max_length=10)

    class Meta:
        db_table = "OrganismAnnotation"

    def __str__(self):
        return "%s" % (self.organism_code)

    def get_organism_code(self):
        return "%s" % (self.organism_code)

    def get_organism_code_version(self):
        return "%s" % (self.organism_code_version)

    def get_full_information(self):
        data = []
        data.append(self.pk)
        data.append(self.organism_code)
        data.append(self.organism_code_version)
        data.append(self.gff_spec_version)
        data.append(self.sequence_region)
        return data

    objects = OrganismAnnotationManger()


"""
# Caller Table
class CallerManager(models.Manager):
    def create_new_caller(self, data):
        new_caller = self.create(name=data["name"], version=data["version"])
        return new_caller


class Caller(models.Model):
    name = models.CharField(max_length=60)
    version = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "Caller"

    def __str__(self):
        return "%s" % (self.name)

    def get_version(self):
        return "%s" % (self.version)

    objects = CallerManager()
"""


# Filter Table
class FilterManager(models.Manager):
    def create_new_filter(self, data):
        new_filter = self.create(filter=data)
        return new_filter


class Filter(models.Model):
    filter = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "Filter"

    def __str__(self):
        return "%s" % (self.filter)

    def get_filter(self):
        return "%s" % (self.filter)

    def get_filter_id(self):
        return "%s" % (self.pk)

    objects = FilterManager()


# Effect Table
class EffectManager(models.Manager):
    def create_new_effect(self, data):
        new_effect = self.create(
            effect=data[11],
        )
        return new_effect


class Effect(models.Model):
    effect = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "Effect"

    def __str__(self):
        return "%s" % (self.effect)

    def get_effect_id(self):
        return "%s" % (self.pk)

    def get_effect(self):
        return "%s" % (self.effect)

    objects = EffectManager()


# Gene Table
class GeneManager(models.Manager):
    def create_new_gene(self, data):
        new_gene = self.create(
            gene_name=data["gene_name"],
            gene_start=data["gene_start"],
            gene_end=data["gene_end"],
            user=data["user"],
            org_annotationID=data["org_annotationID"],
        )
        return new_gene


class Gene(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    org_annotationID = models.ForeignKey(
        OrganismAnnotation, on_delete=models.CASCADE, null=True, blank=True
    )
    gene_name = models.CharField(max_length=50)
    gene_start = models.IntegerField()
    gene_end = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Gene"

    def __str__(self):
        return "%s" % (self.gene_name)

    def get_gene_name(self):
        return "%s" % (self.gene_name)

    def get_gene_id(self):
        return "%s" % (self.pk)

    def get_gene_positions(self):
        return [str(self.gene_start), str(self.gene_end)]

    objects = GeneManager()


# Chromosome Table
class ChromosomeManager(models.Manager):
    def create_new_chromosome(self, data):
        new_chromosome = self.create(chromosome=data)
        return new_chromosome


class Chromosome(models.Model):
    chromosome = models.CharField(max_length=110)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "Chromosome"

    def __str__(self):
        return "%s" % (self.chromosome)

    def get_chromosome_name(self):
        return "%s" % (self.chromosome)

    def get_chromosome_id(self):
        return "%s" % (self.pk)

    objects = ChromosomeManager()


# Sample states table
class SampleState(models.Model):
    state = models.CharField(max_length=80)
    display_string = models.CharField(max_length=80, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "SampleState"

    def __str__(self):
        return "%s" % (self.state)

    def get_state(self):
        return "%s" % (self.state)

    def get_state_id(self):
        return "%s" % (self.pk)

    def get_state_display_string(self):
        return "%s" % (self.display_string)


# table Authors
class AuthorsManager(models.Manager):
    def create_new_authors(self, data):
        analysis_authors = ""
        author_submitter = ""
        new_authors = self.create(
            analysis_authors=analysis_authors,
            author_submitter=author_submitter,
            # analysis_authors=data["analysis_authors"],
            # author_submitter=data["author_submitter"],
            authors=data["authors"],
        )
        return new_authors


class Authors(models.Model):
    analysis_authors = models.CharField(max_length=100, null=True, blank=True)
    author_submitter = models.CharField(max_length=100, null=True, blank=True)
    authors = models.CharField(max_length=600, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "Authors"

    def __str__(self):
        return "%s" % (self.author_submitter)

    def get_analysis_author(self):
        return "%s" % (self.analysis_authors)

    def get_author_submitter(self):
        return "%s" % (self.author_submitter)

    def get_authors(self):
        return "%s" % (self.authors)

    def get_author_obj(self):
        return "%s" % (self.pk)

    objects = AuthorsManager()


class EnaInfo(models.Model):
    bioproject_accession_ENA = models.CharField(max_length=80, null=True, blank=True)
    bioproject_umbrella_accession_ENA = models.CharField(
        max_length=80, null=True, blank=True
    )
    biosample_accession_ENA = models.CharField(max_length=80, null=True, blank=True)
    GenBank_ENA_DDBJ_accession = models.CharField(max_length=80, null=True, blank=True)
    SRA_accession = models.CharField(max_length=80, null=True, blank=True)
    study_alias = models.CharField(max_length=80, null=True, blank=True)
    study_id = models.CharField(max_length=80, null=True, blank=True)
    study_title = models.CharField(max_length=100, null=True, blank=True)
    study_type = models.CharField(max_length=80, null=True, blank=True)
    experiment_alias = models.CharField(max_length=80, null=True, blank=True)
    experiment_title = models.CharField(max_length=80, null=True, blank=True)
    ena_process_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "EnaInfo"

    def __str__(self):
        return "%s" % (self.GenBank_ENA_DDBJ_accession)

    def get_genbank(self):
        return "%s" % (self.GenBank_ENA_DDBJ_accession)

    def get_ena_info(self):
        data = []
        return data

    def get_ena_obj(self):
        return "%s" % (self.pk)


class VirusName(models.Model):
    virus_name = models.CharField(max_length=80, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "VirusName"

    def __str__(self):
        return "%s" % (self.virus_name)

    def get_virus_name(self):
        return "%s" % (self.virus_name)


class GisaidInfo(models.Model):
    virus_id = models.ForeignKey(
        VirusName, on_delete=models.CASCADE, null=True, blank=True
    )
    # GISAID_accession = models.CharField(max_length=80, null=True, blank=True)
    gisaid_id = models.CharField(max_length=80, null=True, blank=True)
    submission_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    length = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "GisaidInfo"

    def __str__(self):
        return "%s" % (self.gisaid_id)

    def get_gisaid_id(self):
        return "%s" % (self.gisaid_id)

    def get_gisaid_data(self):
        if self.virus_id is not None:
            v_name = self.virus_id.get_virus_name()
        else:
            v_name = None
        if self.submission_date is None:
            date = "Not Provided"
        else:
            date = self.submission_date.strftime("%d , %B , %Y")
        data = []
        data.append(self.gisaid_id)
        data.append(date)
        data.append(self.length)
        data.append(v_name)
        return data

    def get_gisaid_obj(self):
        return "%s" % (self.pk)


class Error(models.Model):
    error_name = models.CharField(max_length=100)
    display_string = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "Error"

    def __str__(self):
        return "%s" % (self.error_name)

    def get_error_name(self):
        return "%s" % (self.error_name)

    def get_id(self):
        return "%s" % (self.pk)

    def get_display_string(self):
        return "%s" % (self.display_string)

    def get_description(self):
        return "%s" % (self.description)


# Sample Table
class SampleManager(models.Manager):
    def create_new_sample(self, data):
        state = SampleState.objects.filter(state__exact=data["state"]).last()
        new_sample = self.create(
            sample_unique_id=data["sample_unique_id"],
            sequencing_sample_id=data["sequencing_sample_id"],
            sequencing_date=data["sequencing_date"],
            metadata_file=data["metadata_file"],
            state=state,
            user=data["user"],
        )
        return new_sample


class Sample(models.Model):
    state = models.ForeignKey(SampleState, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    error_type = models.ForeignKey(
        Error, on_delete=models.CASCADE, null=True, blank=True
    )
    metadata_file = models.ForeignKey(
        Document, on_delete=models.CASCADE, null=True, blank=True
    )
    authors_obj = models.ForeignKey(
        Authors, on_delete=models.CASCADE, null=True, blank=True
    )
    gisaid_obj = models.ForeignKey(
        GisaidInfo, on_delete=models.CASCADE, null=True, blank=True
    )
    ena_obj = models.ForeignKey(
        EnaInfo, on_delete=models.CASCADE, null=True, blank=True
    )
    schema_obj = models.ForeignKey(
        Schema, on_delete=models.CASCADE, null=True, blank=True
    )
    linage_values = models.ManyToManyField(LineageValues)
    linage_info = models.ManyToManyField(LineageInfo)
    bio_analysis_values = models.ManyToManyField(BioInfoAnalysisValue)

    sample_unique_id = models.CharField(max_length=12)
    microbiology_lab_sample_id = models.CharField(max_length=80, null=True, blank=True)
    collecting_lab_sample_id = models.CharField(max_length=80, null=True, blank=True)
    sequencing_sample_id = models.CharField(max_length=80, null=True, blank=True)
    submitting_lab_sample_id = models.CharField(max_length=80, null=True, blank=True)
    sequence_file_R1_fastq = models.CharField(max_length=80, null=True, blank=True)
    sequence_file_R2_fastq = models.CharField(max_length=80, null=True, blank=True)
    fastq_r1_md5 = models.CharField(max_length=80, null=True, blank=True)
    fastq_r2_md5 = models.CharField(max_length=80, null=True, blank=True)
    r1_fastq_filepath = models.CharField(max_length=120, null=True, blank=True)
    r2_fastq_filepath = models.CharField(max_length=120, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Sample"

    def __str__(self):
        return "%s" % (self.sequencing_sample_id)

    def get_sample_id(self):
        return "%s" % (self.pk)

    def get_sequencing_sample_id(self):
        return "%s" % (self.sequencing_sample_id)

    def get_collecting_lab_sample_id(self):
        return "%s" % (self.collecting_lab_sample_id)

    def get_unique_id(self):
        return "%s" % (self.sample_unique_id)

    def get_virus_obj(self):
        if self.virus_obj:
            return "%s" % (self.virus_obj)
        return None

    def get_gisaid_obj(self):
        if self.gisaid_obj:
            return "%s" % (self.gisaid_obj)
        return None

    def get_gisaid_info(self):
        if self.gisaid_obj is None:
            return ""
        return self.gisaid_obj.get_gisaid_data()

    def get_ena_obj(self):
        if self.ena_obj:
            return "%s" % (self.ena_obj)
        return None

    def get_schema_obj(self):
        if self.schema_obj:
            return self.schema_obj
        return None

    def get_ena_info(self):
        if self.ena_obj is None:
            return ""
        return self.ena_obj.get_ena_data()

    def get_state(self):
        if self.state:
            return "%s" % (self.state.get_state())
        return None

    def get_user(self):
        return "%s" % (self.user)

    def get_metadata_file(self):
        return "%s" % (self.metadata_file)

    def get_info_for_searching(self):
        recorded_date = self.created_at.strftime("%d , %B , %Y")
        data = []
        data.append(self.pk)
        data.append(self.sequencing_sample_id)
        data.append(self.get_state())
        data.append(recorded_date)
        return data

    def get_sample_basic_data(self):
        recorded_date = self.created_at.strftime("%d , %B , %Y")
        data = []
        data.append(self.sequencing_sample_id)
        data.append(self.microbiology_lab_sample_id)
        data.append(self.submitting_lab_sample_id)
        data.append(self.get_state())
        data.append(recorded_date)
        return data

    def get_fastq_data(self):
        data = []
        data.append(self.sequence_file_R1_fastq)
        data.append(self.sequence_file_R2_fastq)
        data.append(self.r1_fastq_filepath)
        data.append(self.r2_fastq_filepath)
        data.append(self.fastq_r1_md5)
        data.append(self.fastq_r2_md5)
        return data

    def update_state(self, state):
        if not SampleState.objects.filter(state__exact=state).exists():
            return False
        self.state = SampleState.objects.filter(state__exact=state).last()
        self.save()
        return self

    objects = SampleManager()


class DateUpdateState(models.Model):
    stateID = models.ForeignKey(SampleState, on_delete=models.CASCADE)
    sampleID = models.ForeignKey(Sample, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DateUpdateState"

    def __str__(self):
        return "%s_%s" % (self.stateID, self.sampleID)

    def get_state_name(self):
        if self.stateID is not None:
            return "%s" % (self.stateID.get_state_display_string())

    def get_date(self):
        return self.date.strftime("%B %d, %Y")


class AnalysisType(models.Model):
    type_name = models.CharField(max_length=20)
    display_string = models.CharField(max_length=50)

    class Meta:
        db_table = "AnalysisType"

    def __str__(self):
        return "%s" % (self.type_name)

    def get_type_name(self):
        return "%s" % (self.type_name)

    def get_id(self):
        return "%s" % (self.pk)

    def get_display_string(self):
        return "%s" % (self.display_string)


class AnalysisPerformed(models.Model):
    typeID = models.ForeignKey(AnalysisType, on_delete=models.CASCADE)
    sampleID = models.ForeignKey(Sample, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "AnalysisPerformed"

    def __str__(self):
        return "%s_%s" % (
            self.sampleID.get_sequencing_sample_id(),
            self.typeID.get_type_name(),
        )

    def get_analysis_type(self):
        return "%s" % (self.typeID.get_type_name())


# Variant Table
class VariantManager(models.Manager):
    def create_new_variant(self, data, data_ids):
        new_variant = self.create(
            # ref=data,
            chrom=data["chrom"],
            pos=data["pos"],
            ref=data["ref"],
            alt=data["alt"],
            chromosomeID_id=data_ids["chromosomeID_id"],
            callerID_id=data_ids["callerID_id"],
            filterID_id=data_ids["filterID_id"],
            variant_in_sampleID_id=data_ids["variant_in_sampleID_id"],
        )
        return new_variant


# CHROM	POS	REF	ALT
class Variant(models.Model):
    chromosomeID_id = models.ForeignKey(
        Chromosome, on_delete=models.CASCADE, null=True, blank=True
    )
    filterID_id = models.ForeignKey(
        Filter, on_delete=models.CASCADE, null=True, blank=True
    )
    ref = models.CharField(max_length=60, null=True, blank=True)
    pos = models.CharField(max_length=60, null=True, blank=True)
    alt = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "Variant"

    def __str__(self):
        return "%s_%s" % (self.pos, self.alt)

    def get_variant_id(self):
        return "%s" % (self.pk)

    def get_ref(self):
        return "%s" % (self.ref)

    def get_pos(self):
        return "%s" % (self.pos)

    def get_chrom(self):
        return "%s" % (self.chrom)

    def get_alt(self):
        return "%s" % (self.alt)

    objects = VariantManager()


class VariantInSampleManager(models.Manager):
    """
    fields => SAMPLE(0), CHROM(1), POS(2), REF(3), ALT(4),
    FILTER(5), DP(6),  REF_DP(7), ALT_DP(8), AF(9), GENE(10),
    EFFECT(11), HGVS_C(12), HGVS_P(13), HGVS_P1LETTER(14),
    CALLER(15), LINEAGE(16)
    """

    def create_new_variant_in_sample(self, data):
        new_variant_in_sample = self.create(
            dp=data["dp"],
            ref_dp=data["ref_dp"],
            alt_dp=data["alt_dp"],
            af=data["af"],
        )
        return new_variant_in_sample


# FILTER	DP	REF_DP	ALT_DP	AF
class VariantInSample(models.Model):  # include Foreign Keys
    sampleID_id = models.ForeignKey(
        Sample, on_delete=models.CASCADE, null=True, blank=True
    )
    variantID_id = models.ForeignKey(
        Variant, on_delete=models.CASCADE, null=True, blank=True
    )
    dp = models.CharField(max_length=10, null=True, blank=True)
    ref_dp = models.CharField(max_length=10, null=True, blank=True)
    alt_dp = models.CharField(max_length=5, null=True, blank=True)
    af = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("created at"))

    class Meta:
        db_table = "VariantInSample"

    def __str__(self):
        return "%s" % (self.dp)

    def get_variant_in_sample_id(self):
        return "%s" % (self.pk)
    
    def get_variantID_id(self):
        return "%s" % (self.variantID_id.get_variant_id())

    def get_dp(self):
        return "%s" % (self.dp)

    def get_ref_dp(self):
        return "%s" % (self.ref_dp)

    def get_alt_dp(self):
        return "%s" % (self.alt_dp)

    def get_af(self):
        return "%s" % (self.af)
    
    def get_variant_pos(self):
        return self.variantID_id.get_pos()
    
    def get_variant_in_sample_data(self):
        data = []
        data.append(self.dp)
        data.append(self.ref_dp)
        data.append(self.alt_dp)
        data.append(self.af)
        return data

    objects = VariantInSampleManager()


class VariantAnnotationManager(models.Manager):
    def create_new_variant_annotation(self, data, data_ids):
        new_variant_annotation = self.create(
            hgvs_c=data["hgvs_c"],
            hgvs_p=data["hgvs_p"],
            hgvs_p_1letter=data["hgvs_p_1_letter"],
            effectID_id=data_ids["effectID_id"],
            geneID_id=data_ids["geneID_id"],
        )
        return new_variant_annotation


# variant annotation GENE	EFFECT??	HGVS_C	HGVS_P	HGVS_P_1LETTER
class VariantAnnotation(models.Model):
    geneID_id = models.ForeignKey(Gene, on_delete=models.CASCADE)
    effectID_id = models.ForeignKey(
        Effect, on_delete=models.CASCADE, null=True, blank=True
    )
    variantID_id = models.ForeignKey(
        Variant, on_delete=models.CASCADE, null=True, blank=True
    )
    hgvs_c = models.CharField(max_length=60)
    hgvs_p = models.CharField(max_length=60)
    hgvs_p_1letter = models.CharField(max_length=100)

    class Meta:
        db_table = "VariantAnnotation"

    def __str__(self):
        return "%s" % (self.variantID_id)

    def get_variant_annotation_id(self):
        return "%s" % (self.pk)

    def get_geneID_id(self):
        return "%s" % (self.geneID_id)

    def get_effectID_id(self):
        return "%s" % (self.effectID_id)
    
    def get_hgvs_c(self):
        return "%s" % (self.hgvs_c)

    def get_hgvs_p(self):
        return "%s" % (self.hgvs_p)

    def get_hgvs_p_1letter(self):
        return "%s" % (self.hgvs_p_1letter)

    def get_variant_in_sample_data(self):
        data = []
        data.append(self.hgvs_c)
        data.append(self.hgvs_p)
        data.append(self.hgvs_p_1letter)
        return data

    objects = VariantAnnotationManager()


class TemporalSampleStorageManager(models.Manager):
    def save_temp_data(self, data):
        new_t_data = self.create(
            sample_idx=data["sample_idx"], field=data["field"], value=data["value"]
        )
        return new_t_data


class TemporalSampleStorage(models.Model):
    sample_idx = models.IntegerField()
    field = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    sent = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "TemporalSampleStorage"

    def __str__(self):
        return "%s,%s" % (self.sample, self.field)

    def get_temp_values(self):
        return {self.field: self.value}

    def update_sent_status(self, value):
        self.sent = value
        self.save()
        return

    objects = TemporalSampleStorageManager()


class ConfigSettingManager(models.Manager):
    def create_config_setting(self, configuration_name, configuration_value):
        new_config_settings = self.create(
            configurationName=configuration_name, configurationValue=configuration_value
        )
        return new_config_settings


class ConfigSetting(models.Model):
    configuration_name = models.CharField(max_length=80)
    configuration_value = models.CharField(max_length=255, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ConfigSetting"

    def __str__(self):
        return "%s" % (self.configuration_name)

    def get_configuration_value(self):
        return "%s" % (self.configuration_value)

    def set_configuration_value(self, new_value):
        self.configuration_value = new_value
        self.save()
        return self

    objects = ConfigSettingManager()
