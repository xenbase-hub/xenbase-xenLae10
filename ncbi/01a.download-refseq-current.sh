#!/bin/bash

DATE=$(date +"%Y-%m-%d")
echo $DATE

DOWNLOAD_FILENAME_V10="XENLA_xenLae10.refseq"$DATE".zip"

curl --output-dir ./raw -OJX GET "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/GCF_017654675.1/download?include_annotation_type=GENOME_GFF,RNA_FASTA,CDS_FASTA,PROT_FASTA,SEQUENCE_REPORT&filename=$DOWNLOAD_FILENAME_V10" -H "Accept: application/zip"

unzip ./raw/$DOWNLOAD_FILENAME_V10
DIR_UNZIP_V10="ncbi_dataset/data/GCF_017654675.1/"
FILENAME_OUT_V10="XENLA_xenLae10.refseq"$DATE

mv $DIR_UNZIP_V10/cds_from_genomic.fna ./raw/$FILENAME_OUT_V10"_cds_from_genomic.fna"
mv $DIR_UNZIP_V10/genomic.gff ./raw/$FILENAME_OUT_V10"_genomic.gff"
mv $DIR_UNZIP_V10/protein.faa ./raw/$FILENAME_OUT_V10"_protein.faa"
mv $DIR_UNZIP_V10/rna.fna  ./raw/$FILENAME_OUT_V10"_rna.fna"

rm -rf ncbi_dataset
