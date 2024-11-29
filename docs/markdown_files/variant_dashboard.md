# Variants Dashboard

Variants Dashboard gathers different kinds of interactive graphs, both
related to the results of the variants detected in the samples through 
bioinformatics analysis.

## Mutations in Lineages

This interactive needle plot shows the different mutations that are found
in the samples for each lineage registered in the database, where the height
of the needle is related to the population allele frequency, and the color
with the kind of mutation. The x axis represents the length of SARS-CoV-2
genome, so each needle is shown under the corresponding genome location where
it's found.

You can choose between all the lineages registered in the database, and
zoom in any section of the genome of your interest.

![v_dashboard_var_in_lineage](img/v_dashboard_var_in_lineage.png)

There's a tutorial in the upper part which shows information about each
element of the graph.

## Lineages VOC

Lineages VOC (Variants Of Concern) graph shows the evolution of the variants
in the database over time. As there are a lot of lineages in the database, the
data shown in this graph corresponds to variants, representing a higher level of
classification. Multiple lineages may correspond to the same variant.
Each color represents a different variant, and the occupied area shows the
relative abundancy of each one. The dates shown by default are the first
and last collection dates found in the database.

![v_dashboard_voc](img/v_dashboard_voc.png)