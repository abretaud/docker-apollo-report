# Docker Image for Apollo annotation reports

[![Docker Repository on Quay](https://quay.io/repository/abretaud/apollo-report/status "Docker Repository on Quay")](https://quay.io/repository/abretaud/apollo-report)

This image contains everything needed to generate an Apollo per-user report each day, with rules defined at http://bipaa.genouest.org/.

## Using the Container

We highly recommend using a `docker-compose.yml` to run your containers.

```yaml
version: "2"
services:
  report:
    image: quay.io/abretaud/apollo-report:latest
    environment:
        APOLLO_URL: http://apollo:8080/ # Full URL to the Apollo server
        APOLLO_EXT_URL: http://example.org/somewhere/apollo/ # Full URL to the Apollo server, accessible from anywhere (default= APOLLO_URL)
        APOLLO_USER: admin@apollo # Admin account to connect to apollo
        APOLLO_PASS: password # Password to connect to apollo
        ADMIN_USERS: userx@apollo,usery@apollo # Set this to a list of users who will have access to all the data from all users.
    volumes:
        - ./my_genome.fa:/data/genomes/Genus_species.fa:ro # Always mount the genome fasta files to this location, named by organism common name
        - ./my_other_genome.fa:/data/genomes/Genies_specus.fa:ro # Always mount the genome fasta files to this location, named by organism common name
        - ./my_annotation_groups.tsv:/data/annotation_groups.tsv:ro # If you have annotation groups, mount the list file on this location
    ports:
      - "3000:80"
```

A cron task is configured to generate the report every day. You can consult the script error log by looking at /var/log/apollo_report.log.

## Configuring the Container

The following environment variables are also available:

```
APOLLO_URL: http://apollo:8080/ # Full URL to the Apollo server, accessible from the container
APOLLO_EXT_URL: http://example.org/somewhere/apollo/ # Full URL to the Apollo server, accessible from anywhere (default= APOLLO_URL)
APOLLO_USER: admin@apollo # Admin account to connect to apollo
APOLLO_PASS: password # Password to connect to apollo
ADMIN_USERS: userx@apollo,usery@apollo # Set this to a list of users who will have access to all the data from all users.
ALL_ADMINS: 0 # Set this to 1 if you want users to have access to other users information (ADMIN_USERS will be ignored)
DETAILED_REPORT: 0 # Set this to 1 if you want to display more detailed information for admin users
ANNOTATION_GROUPS: 1 # Set this to 0 if you don't want to validate AnnotGroup attribute
SPLIT_USERS: 1 # Set this to 0 if you don't want to remove the @something suffix from apollo user names
REPORT_JSON_PATH: /data/report/full_report.json # Location for a temp file, no need to change this in most cases
LOCAL_ONLY: for testing purpose only, will not try to contact a remote apollo server, will expect a raw gff extract from apollo to be mounted on /data/raw_apollo.gff, and a genome to be mounted on /data/genome.fa
```
