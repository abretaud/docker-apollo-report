FROM php:7-apache

MAINTAINER Anthony Bretaudeau <anthony.bretaudeau@inra.fr>

ENV TINI_VERSION v0.9.0
RUN set -x \
    && curl -fSL "https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini" -o /usr/local/bin/tini \
    && chmod +x /usr/local/bin/tini

ENTRYPOINT ["/usr/local/bin/tini", "--"]

WORKDIR /var/www

VOLUME ["/data/report/"]

# Install packages and PHP-extensions
RUN apt-get -q update && \
    DEBIAN_FRONTEND=noninteractive apt-get -yq --no-install-recommends install \
    wget git cron python-pip python-dev python-numpy jq python-setuptools \
 && rm -rf /var/lib/apt/lists/*

# Install gffread
RUN wget http://cole-trapnell-lab.github.io/cufflinks/assets/downloads/cufflinks-2.2.1.Linux_x86_64.tar.gz \
 && tar -xzvf cufflinks-2.2.1.Linux_x86_64.tar.gz \
 && cp cufflinks-2.2.1.Linux_x86_64/gffread /usr/bin/gffread \
 && rm -rf cufflinks-2.2.1.Linux_x86_64.tar.gz cufflinks-2.2.1.Linux_x86_64

RUN pip install bcbio-gff biopython unicode

ENV APOLLO_URL="http://apollo:8080/" \
    APOLLO_USER="admin@apollo" \
    APOLLO_PASS="password" \
    APOLLO_MOUNTPOINT=""\
    ALL_ADMINS=0 \
    DETAILED_REPORT=0 \
    ANNOTATION_GROUPS=1 \
    SPLIT_USERS=1 \
    LOCAL_ONLY=0 \
    ENABLE_OP_CACHE=1 \
    REPORT_PATH=/data/report/

ADD entrypoint.sh /
ADD ./scripts/ /scripts/
ADD ./report_viewer/* /var/www/html/
ADD ./apollo_checker/ /opt/apollo_checker/

RUN ln -s /data/report/ /var/www/html/report_data/

CMD ["/entrypoint.sh"]
