from django.contrib import admin
from .models import *


class CallerAdmin(admin.ModelAdmin):
    list_display = ["name", "version"]


class FilterAdmin(admin.ModelAdmin):
    list_display = ["filter"]


class EffectAdmin(admin.ModelAdmin):
    list_display = ["effect", "hgvs_c", "hgvs_p", "hgvs_p_1_letter"]


class LineageAdmin(admin.ModelAdmin):
    list_display = [
        "lineage_identification_date",
        "lineage_name",
        "lineage_analysis_software_name",
        "if_lineage_identification_other",
        "lineage_analysis_software_version",
    ]


class GeneAdmin(admin.ModelAdmin):
    list_display = ["gene"]


class ChromosomeAdmin(admin.ModelAdmin):
    list_display = ["chromosome"]


class SampleAdmin(admin.ModelAdmin):
    list_display = [
        "collecting_lab_sample_id",
        "sequencing_sample_id",
        "biosample_accession_ENA",
        "virus_name",
        "gisaid_id",
        "sequencing_date",
    ]


class SampleStateAdmin(admin.ModelAdmin):
    list_display = ["state", "description"]


class VariantAdmin(admin.ModelAdmin):
    list_display = ["pos", "ref", "alt", "dp", "alt_dp", "ref_dp", "af"]


class AnalysisAdmin(admin.ModelAdmin):
    list_display = [
        "raw_sequence_data_processing_method",
        "dehosting_method",
        "assembly",
        "if_assembly_other",
        "assembly_params",
        "variant_calling",
        "if_variant_calling_other",
        "variant_calling_params",
        "consensus_sequence_name",
        "consensus_sequence_name_md5",
        "consensus_sequence_filepath",
        "consensus_sequence_software_name",
        "if_consensus_other",
        "consensus_sequence_software_version",
        "consensus_criteria",
        "reference_genome_accession",
        "bioinformatics_protocol",
        "if_bioinformatic_protocol_is_other_specify",
        "bioinformatic_protocol_version",
        "analysis_date",
        "commercial_open_source_both",
        "preprocessing",
        "if_preprocessing_other",
        "preprocessing_params",
        "mapping",
        "if_mapping_other",
        "mapping_params",
        "reference_genome_accession",
    ]


class QcStatsAdmin(admin.ModelAdmin):
    list_display = [
        "quality_control_metrics",
        "breadth_of_coverage_value",
        "depth_of_coverage_value",
        "depth_of_coverage_threshold",
        "number_of_base_pairs_sequenced",
        "consensus_genome_length",
        "ns_per_100_kbp",
        "per_qc_filtered",
        "per_reads_host",
        "per_reads_virus",
        "per_unmapped",
        "per_genome_greater_10x",
        "mean_depth_of_coverage_value",
        "per_Ns",
        "number_of_variants_AF_greater_75percent",
        "number_of_variants_with_effect",
    ]


class AuthorsAdmin(admin.ModelAdmin):
    list_display = ["analysis_authors", "author_submitter", "authors"]


class PublicDatabaseAdmin(admin.ModelAdmin):
    list_display = ["databaseName"]


class PublicDatabaseFieldAdmin(admin.ModelAdmin):
    list_display = ["publicDatabaseID", "fieldName", "fieldDescription", "fieldInUse"]


class SchemaAdmin(admin.ModelAdmin):
    list_display = ["schemaName", "schemaVersion", "schemaInUse", "schemaAppsName"]


# Register models
admin.site.register(Caller, CallerAdmin)
admin.site.register(Filter, FilterAdmin)
admin.site.register(Effect, EffectAdmin)
admin.site.register(Lineage, LineageAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Chromosome, ChromosomeAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Analysis, AnalysisAdmin)
admin.site.register(QcStats, QcStatsAdmin)
admin.site.register(Authors, AuthorsAdmin)
admin.site.register(PublicDatabase, PublicDatabaseAdmin)
admin.site.register(PublicDatabaseField, PublicDatabaseFieldAdmin)
admin.site.register(Schema, SchemaAdmin)
