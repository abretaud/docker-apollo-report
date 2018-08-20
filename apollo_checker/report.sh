#!/bin/bash

set -u # stop if a variable is not initialized
set -e # stop in case of error

wa_url="0.0.0.0:8080" # Url of the Apollo server (trim trailing slash)
wa_ext_url="0.0.0.0:8080" # Url of the Apollo server (trim trailing slash)
genome="/root/script_python/Citrus_sinensis-scaffold00001.fasta" # Path to the genome fasta file
output_dir="/root/script_python/tmp" # Directory where generated fils should be placed
ANNOTATION_GROUPS="1"
SPLIT_USERS="1"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APOLLO_USER="admin_temp@bipaa"
APOLLO_PASS="admin"

# Automatic config
tmp_dir=`mktemp -d`
raw_apollo_gff="raw_apollo.gff"
raw_apollo_gff_gz="$raw_apollo_gff.gz"
cur_date=`date +%F_%X`

OPTS=""
if [[ $ANNOTATION_GROUPS == "0" ]]
then
    OPTS="-g /data/annotation_groups.tsv"
fi

if [[ $SPLIT_USERS == "1" ]]
then
    OPTS="$OPTS --split-users"
fi

# Get organisms

res=`curl --header "Content-Type:application/json" -d"{'username': '$APOLLO_USER', 'password': '$APOLLO_PASS'}" "http://0.0.0.0:8080/organism/findAllOrganisms"`
touch "$output_dir/report.json"

echo "$res" | jq -c '.[]' | while read i; do
    tmp_dir=`mktemp -d`
    cd "$tmp_dir"
    orga=`echo $i | jq ".commonName"`
    res=`curl --header "Content-Type:application/json" -d "{'username': '$APOLLO_USER', 'password': '$APOLLO_PASS', 'type':'GFF3', 'exportAllSequences':'true', 'chadoExportType':'', 'seqType':'genomic', 'exportGff3Fasta':'false', 'output':'file', 'format':'gzip', 'sequences':[]}" "$wa_url/IOService/write"`
    orga=`sed -e 's/^"//' -e 's/"$//' <<<"${orga// /_}"`
    uuid=`echo $res | sed "s/.*uuid\"\:\"\([-a-z0-9]\+\)\".*/\1/"`
    orga_output_dir="$output_dir/$orga"
    mkdir -p "$orga_output_dir"

# Download the gz file
    curl --data-urlencode data="{'username': '$APOLLO_USER', 'password': '$APOLLO_PASS'}" -o "$raw_apollo_gff_gz" "$wa_url/IOService/download?uuid=$uuid&format=gzip&seqType=genomic&exportType=GFF3"

# Unzip the annotation file

    gunzip "$raw_apollo_gff_gz"

# Launch the script to check gene models
    python $SCRIPT_DIR/apollo_checker.py \
        -a "$wa_ext_url" \
        -o "$orga_output_dir/valid.gff" \
        -i "$orga_output_dir/invalid.gff" \
        -d "$orga_output_dir/deleted.tsv" \
        --report_admin_json "$orga_output_dir/report.json" \
        $OPTS \
        "$raw_apollo_gff" \
        "$genome"

    gffread "$orga_output_dir/valid.gff" -F -g "$genome" \
        -w "$orga_output_dir/valid_transcripts.fa" \
        -x "$orga_output_dir/valid_cds.fa" \
        -y "$orga_output_dir/valid_proteins.fa"

    echo -n "\"$orga\""":" >> "$output_dir/report.json"
    cat "$orga_output_dir/report.json" >> "$output_dir/report.json"
    echo "" >> "$output_dir/report.json"
    cp "$raw_apollo_gff" "$orga_output_dir/$raw_apollo_gff"

    # Remove temp files
    rm -rf $tmp_dir
done

sed -i '1s/^/{/;$!s/$/,/;$s/$/}/' "$output_dir/report.json"
