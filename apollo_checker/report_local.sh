#!/bin/bash

set -u # stop if a variable is not initialized
set -e # stop in case of error

wa_ext_url=${1%/} # Url of the Apollo server (trim trailing slash)
genome=$2 # Path to the genome fasta file
output_dir=$3 # Directory where generated fils should be placed

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Automatic config
tmp_dir=`mktemp -d`
raw_apollo_gff="/data/raw_apollo.gff"
cur_date=`date +%F_%X`

cd "$tmp_dir"

OPTS=""
if [[ $ANNOTATION_GROUPS == "1" ]]
then
    OPTS="-g /data/annotation_groups.tsv"
fi

if [[ $SPLIT_USERS == "1" ]]
then
    OPTS="$OPTS --split-users"
fi

# Launch the script to check gene models
python $SCRIPT_DIR/apollo_checker.py \
    -a "$wa_ext_url" \
    -o "$output_dir/valid.gff" \
    -i "$output_dir/invalid.gff" \
    --report_admin_json "$output_dir/full_report.json" \
    $OPTS \
    "$raw_apollo_gff" \
    "$genome"

gffread "$output_dir/valid.gff" -F -g "$genome" \
    -w "$output_dir/valid_transcripts.fa" \
    -x "$output_dir/valid_cds.fa" \
    -y "$output_dir/valid_proteins.fa"

# Remove temp files
rm -rf $tmp_dir
