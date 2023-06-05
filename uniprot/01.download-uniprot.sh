#!/bin/bash

DATE=$(date +"%Y-%m-%d")
echo "Today: "$DATE

## UniProt current_release
UNIPROT_URL="https://ftp.uniprot.org/pub/databases/uniprot/current_release"

curl --output-dir ./raw -O "$UNIPROT_URL/relnotes.txt"
RELNOTE_OUT="./raw/uniprot_relnotes.$DATE.txt"
mv ./raw/relnotes.txt $RELNOTE_OUT

UP_VERSION=$(head -n 1 $RELNOTE_OUT | awk '{print $3}')

UNIPROT_XT_URL=$UNIPROT_URL"/knowledgebase/reference_proteomes/Eukaryota/UP000186698/"

for FILENAME in UP000186698_8355.fasta.gz UP000186698_8355_additional.fasta.gz UP000186698_8355.idmapping.gz UP000186698_8355.gene2acc.gz
do
  FILENAME_OUT=$UP_VERSION"."$FILENAME
  if [ -e "./raw/$FILENAME_OUT" ]; then
    echo "$FILENAME_OUT exists. Skip."
  else
    echo "Download $FILENAME_OUT"
    curl --output-dir ./raw -o $FILENAME_OUT "$UNIPROT_XT_URL/$FILENAME"
  fi
done
