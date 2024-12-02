# Upload samples to GISAID

GISAID is an international initiative aimed at sharing data on influenza and other respiratory 
viruses, including SARS-CoV-2, to enhance global surveillance and response to viral outbreaks by
facilitating the sharing of genomic sequences and associated metadata. During the COVID-19 pandemic,
GISAID played a pivotal role in the global sharing of SARS-CoV-2 genomic data, and its still in
high demand for assets like an online [mutation analysis](https://gisaid.org/database-features/covsurver-mutations-app/) app. 

If you want to upload your sequences to GISAID database, you will need to register first. For any
programmatic submission you will also need an API token associated to your account.

GISAID also provides several alternatives for sequence submission to their database. You may find more
information in [their webpage](https://gisaid.org/database-features/submission-tool-cli4/)

Nonetheless, relecov-tools also implements a [module](https://github.com/BU-ISCIII/relecov-tools?tab=readme-ov-file#upload-to-gisaid) to update samples semi-automatically to ENA,
you will only need to install the package, and follow the instructions found in the repository.