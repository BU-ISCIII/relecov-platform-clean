from django.shortcuts import render
from relecov_dashboard.utils.graphics.lineages_in_time_graph import (
    create_lineage_in_time_graph,
)

from relecov_dashboard.utils.graphics.molecule3D_graph import (
    create_molecule3D_zoom_specific_residues,
)
from relecov_dashboard.utils.graphics.needle_plot_graph import create_needle_plot_graph
from relecov_dashboard.utils.graphics.mutations_3D_molecule import create_graph
from relecov_dashboard.utils.graphics.mutation_table import create_mutation_table

# from relecov_dashboard.utils.graphics.lineage_by_CCAA_geomap_graph import plot_geomap
from relecov_dashboard.utils.graphics.mutation_heatmap import create_hot_map

from relecov_dashboard.utils.graphics.geo_json import create_json


def variant_dashboard(request):
    return render(request, "relecov_dashboard/variant_dashboard.html")


def methodology_dashboard(request):
    return render(request, "relecov_dashboard/methodology_dashboard.html")


def lineages_voc(request):
    create_lineage_in_time_graph()
    create_needle_plot_graph(sample=None)
    create_molecule3D_zoom_specific_residues()
    create_mutation_table(214821)
    create_hot_map()
    return render(request, "relecov_dashboard/dashboard_templates/lineages_voc.html")


def hackaton_graphs(request):
    create_graph()
    create_json("BA.1.1.1")
    return render(request, "relecov_dashboard/dashboard_templates/hackaton_graphs.html")
