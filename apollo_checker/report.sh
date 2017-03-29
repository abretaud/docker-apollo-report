#!/bin/bash

set -u # stop if a variable is not initialized
set -e # stop in case of error

wa_url=${1%/} # Url of the Apollo server (trim trailing slash)
wa_ext_url=${2%/} # Url of the Apollo server (trim trailing slash)
genome=$3 # Path to the genome fasta file
output_dir=$4 # Directory where generated fils should be placed

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Automatic config
tmp_dir=`mktemp -d`
raw_apollo_gff="raw_apollo.gff"
raw_apollo_gff_gz="$raw_apollo_gff.gz"
cur_date=`date +%F_%X`

cd "$tmp_dir"

# Create the gz file on the server
res=`curl --data-urlencode data="{'username': '$APOLLO_USER', 'password': '$APOLLO_PASS', 'type':'GFF3', 'exportAllSequences':'true', 'chadoExportType':'', 'seqType':'genomic', 'exportGff3Fasta':'false', 'output':'file', 'format':'gzip', 'sequences':[]}" "$wa_url/IOService/write"`

uuid=`echo $res | sed "s/.*uuid\"\:\"\([-a-z0-9]\+\)\".*/\1/"`

# Download the gz file
curl --data-urlencode data="{'username': '$APOLLO_USER', 'password': '$APOLLO_PASS'}" -o "$raw_apollo_gff_gz" "$wa_url/IOService/download?uuid=$uuid&format=gzip&seqType=genomic&exportType=GFF3"

# Unzip the annotation file
gunzip "$raw_apollo_gff_gz"

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
    -a "$wa_url" \
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

cp "$raw_apollo_gff" "$output_dir/$raw_apollo_gff"

# Remove temp files
rm -rf $tmp_dir
