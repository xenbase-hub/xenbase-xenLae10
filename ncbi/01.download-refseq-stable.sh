#!/bin/bash

URL_NCBI_GENOME="https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_other/Xenopus_laevis/all_assembly_versions"
URL_NCBI_v10=$URL_NCBI_GENOME"/GCF_017654675.1_Xenopus_laevis_v10.1/"
URL_NCBI_v2=$URL_NCBI_GENOME"/suppressed/GCF_001663975.1_Xenopus_laevis_v2/"

for FILENAME in $(cat FILES.xenLae10_refseq101)
do
  FILENAME_OUT="./raw/"$FILENAME
  if [ -e $FILENAME_OUT ]; then
    echo "$FILENAME_OUT exists. Skip."
  else
    FILENAME_URL=$URL_NCBI_v10"/"$FILENAME
    echo "Download $FILENAME_URL"
    curl --output-dir ./raw -O $FILENAME_URL
  fi
done

for FILENAME in $(cat FILES.xenLae2_refseq100)
do
  FILENAME_OUT="./raw/"$FILENAME
  if [ -e $FILENAME_OUT ]; then
    echo "$FILENAME_OUT exists. Skip."
  else
    FILENAME_URL=$URL_NCBI_v2"/"$FILENAME
    echo "Download $FILENAME_URL"
    curl --output-dir ./raw -O $FILENAME_URL
  fi
done
