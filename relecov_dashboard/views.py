# Generic imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Local imports
import relecov_core.core_config
import relecov_core.utils.handling_lineage
import relecov_core.utils.handling_variant
import relecov_dashboard.dashboard_config
import relecov_dashboard.utils.generic.graphics.plotly
import relecov_dashboard.utils.methodology.graphics.met_bioinfo
import relecov_dashboard.utils.methodology.graphics.met_host_info
import relecov_dashboard.utils.methodology.graphics.met_index
import relecov_dashboard.utils.methodology.graphics.met_sample_preprocessing
import relecov_dashboard.utils.methodology.graphics.met_sequencing
import relecov_dashboard.utils.variants.graphics.var_heatmap_mutation_graph_by_lineage
import relecov_dashboard.utils.variants.graphics.var_lineage_variation_over_time_graph
import relecov_dashboard.utils.variants.graphics.var_lineages_in_time
import relecov_dashboard.utils.variants.graphics.var_molecule3D_bn_graph
import relecov_dashboard.utils.variants.graphics.var_needle_mutation_graph_by_lineage
import relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie


# dashboard/variants
@login_required
def variants_index(request):
    return render(request, "relecov_dashboard/variantsIndex.html")


@login_required
def mutations_in_lineage(request):
    # mutations in lineages by lineage
    def_chrom = relecov_core.utils.handling_variant.get_default_chromosome()
    lineages_list = relecov_core.utils.handling_lineage.get_lineages_list()
    mdata, lineage = (
        relecov_dashboard.utils.variants.graphics.var_needle_mutation_graph_by_lineage.get_variant_data_from_lineages(
            graphic_name="variations_per_lineage", lineage=None, chromosome=def_chrom
        )
    )

    if not mdata:
        return render(
            request,
            "relecov_dashboard/variantMutationsInLineage.html",
            {
                "ERROR": relecov_dashboard.dashboard_config.ERROR_NO_LINEAGES_ARE_DEFINED_YET
            },
        )
    relecov_dashboard.utils.variants.graphics.var_needle_mutation_graph_by_lineage.create_needle_plot_graph_mutation_by_lineage(
        lineages_list, lineage, mdata
    )
    return render(
        request,
        "relecov_dashboard/variantMutationsInLineage.html",
    )


# FIXME: template html has bad ref in plotly_app. App name shoudl be replaced by 'model3D_bn'
# FIXME: Couldn't find in variants dashboard a button or ref to acces this url
@login_required
def spike_mutations_3d(request):
    relecov_dashboard.utils.variants.graphics.var_molecule3D_bn_graph.create_model3D_bn()
    return render(request, "relecov_dashboard/variantSpikeMutations3D.html")


def lineages_voc(request):
    # Draw lineage based on time
    draw_lineages = {}
    draw_lineages["lineage_on_time"] = (
        relecov_dashboard.utils.variants.graphics.var_lineage_variation_over_time_graph.create_lineages_variations_graphic()
    )
    return render(
        request,
        "relecov_dashboard/variantLineageVoc.html",
        {"draw_lineages": draw_lineages},
    )


# FIXME: isn't called from urls.py and html template is not available.
@login_required
def samples_received_over_time_graph(request):
    df = (
        relecov_dashboard.utils.variants.graphics.var_lineages_in_time.create_dataframe_from_json()
    )
    relecov_dashboard.utils.variants.graphics.var_lineages_in_time.create_samples_over_time_graph(
        df
    )

    return render(request, "relecov_dashboard/samplesReceivedOverTimeGraph.html")


# FIXME: isn't called from urls.py and html template is not available.
@login_required
def samples_received_over_time_pie(request):
    data = (
        relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie.parse_json_file()
    )
    relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie.create_samples_received_over_time_per_ccaa_pieChart(
        data
    )
    relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie.create_samples_received_over_time_per_laboratory_pieChart(
        data
    )

    return render(request, "relecov_dashboard/samplesReceivedOverTimePie.html")


# FIXME: isn't called from urls.py and html template is not available.
@login_required
def samples_received_over_time_pie_laboratory(request):
    data = (
        relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie.parse_json_file()
    )
    relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie.create_samples_received_over_time_per_ccaa_pieChart(
        data
    )
    relecov_dashboard.utils.variants.graphics.var_samples_received_over_time_pie.create_samples_received_over_time_per_laboratory_pieChart(
        data
    )

    return render(
        request, "relecov_dashboard/samplesReceivedOverTimePieLaboratory.html"
    )


# FIXME: isn't called from urls.py and html template is not available.
@login_required
def variants_mutations_in_lineages_heatmap(request):
    chromesome_objs = relecov_core.utils.handling_variant.get_all_chromosome_objs()
    if chromesome_objs is None:
        return render(
            request,
            "relecov_dashboard/variantsMutationsInLineagesHeatmap.html",
            {
                "ERROR": relecov_core.core_config.ERROR_CHROMOSOME_NOT_DEFINED_IN_DATABASE
            },
        )
    if len(chromesome_objs) > 1:
        chromesome_list = []
        for chromesome_obj in chromesome_objs:
            chromesome_list.append(
                [
                    chromesome_objs.get_chromesome_id(),
                    chromesome_objs.get_chromesome_name(),
                ]
            )
        return render(
            request,
            "relecov_dashboard/variantsMutationsInLineagesHeatmap.html",
            {"ORGANISM": chromesome_list},
        )
    gene_list = relecov_core.utils.handling_variant.get_gene_list(chromesome_objs[0])
    if len(gene_list) == 0:
        return render(
            request,
            "relecov_dashboard/variantsMutationsInLineagesHeatmap.html",
            {"ERROR": relecov_core.core_config.ERROR_GENE_NOT_DEFINED_IN_DATABASE},
        )
    sample_list = relecov_core.utils.handling_variant.get_sample_in_variant_list(
        chromesome_objs[0]
    )
    if len(sample_list) == 0:
        return render(
            request,
            "relecov_dashboard/variantsMutationsInLineagesHeatmap.html",
            {"ERROR": relecov_core.core_config.ERROR_VARIANT_IN_SAMPLE_NOT_DEFINED},
        )
    relecov_dashboard.utils.variants.graphics.var_heatmap_mutation_graph_by_lineage.create_heatmap(
        sample_list, gene_list
    )
    return render(request, "relecov_dashboard/variantsMutationsInLineagesHeatmap.html")


# dashboard/methodology
@login_required
def methodology_index(request):
    graphics = relecov_dashboard.utils.methodology.graphics.met_index.index_dash_fields()
    return render(
        request, "relecov_dashboard/methodologyIndex.html", {"graphics": graphics}
    )


@login_required
def methodology_host_info(request):
    host_info = (
        relecov_dashboard.utils.methodology.graphics.met_host_info.host_info_graphics()
    )
    if "ERROR" in host_info:
        return render(
            request, "relecov_dashboard/methodologyHostInfo.html", {"ERROR": host_info}
        )
    return render(
        request, "relecov_dashboard/methodologyHostInfo.html", {"host_info": host_info}
    )


@login_required
def methodology_sequencing(request):
    sequencing = (
        relecov_dashboard.utils.methodology.graphics.met_sequencing.sequencing_graphics()
    )
    if "ERROR" in sequencing:
        return render(
            request,
            "relecov_dashboard/methodologySequencing.html",
            {"ERROR": sequencing},
        )
    return render(
        request,
        "relecov_dashboard/methodologySequencing.html",
        {"sequencing": sequencing},
    )


@login_required
def methodology_sample_processing(request):
    sample_processing = (
        relecov_dashboard.utils.methodology.graphics.met_sample_preprocessing.sample_processing_graphics()
    )
    if "ERROR" in sample_processing:
        return render(
            request,
            "relecov_dashboard/methodologySampleProcessing.html",
            {"ERROR": sample_processing},
        )
    return render(
        request,
        "relecov_dashboard/methodologySampleProcessing.html",
        {"sample_processing": sample_processing},
    )


@login_required
def methodology_bioinfo(request):
    bioinfo = relecov_dashboard.utils.methodology.graphics.met_bioinfo.bioinfo_graphics()
    return render(
        request, "relecov_dashboard/methodologyBioinfo.html", {"bioinfo": bioinfo}
    )
