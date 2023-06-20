#!/bin/bash

DATE=$(date +"%Y-%m-%d")

GPI_OUT="Xenbase_GPI."$DATE".raw.tsv"

if [ ! -e $GPI_OUT ]; then
  echo "Download $GPI_OUT"
  curl --output-dir ./raw -o $GPI_OUT https://xenbase-bio1.ucalgary.ca/cgi-bin/reports/gpi_v2.cgi
  gzip ./raw/$GPI_OUT
else
  echo "$GPI_OUT is available. Skip."
fi
