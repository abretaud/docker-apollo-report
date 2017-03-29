#!/usr/bin/python

import sys, os, re
import argparse

from BCBio import GFF
from Bio import SeqIO

from wacheck.Gene import Gene
from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError
from wacheck.report.AdminTextReport import AdminTextReport
from wacheck.report.AdminHtmlReport import AdminHtmlReport
from wacheck.report.AdminJsonReport import AdminJsonReport
from wacheck.report.UserHtmlReport import UserHtmlReport

class WAChecker():

    def main(self):

        self.parse_args()

        # Prepare internal properties
        self.group_tags = ['AnnotGroup']
        if self.apollo_1x:
            self.group_tags += ['SFAnnot', 'CCAnnot', 'SF Annot']
        self.all_genes = {}
        self.wa_errors = []
        self.genes_seen_once = 0
        self.genes_with_goid = 0
        self.splitted_genes = {}
        self.duplicated_genes = {}

        self.compute_scaf_lengths()
        self.parse_groups()

        # Launch data validation
        self.validate_genes()
        self.post_validation()

        # Render reports
        errors = self.errors_by_users()
        warnings = self.warnings_by_users()
        oks = self.ok_by_users()
        genes_by_users = self.genes_by_users()

        self.names = sorted(genes_by_users.keys())

        # Admin report in txt
        admin_txt_report = AdminTextReport(self, oks, errors, warnings, genes_by_users)
        admin_txt_report.render()
        if self.report_admin_txt:
            admin_txt_report.save_to_file(self.report_admin_txt)

        # Admin report in html
        if self.report_admin_html:
            admin_html_report = AdminHtmlReport(self, oks, errors, warnings, genes_by_users)
            admin_html_report.save_to_file(self.report_admin_html)

        # Write user html reports if asked
        if self.report_dir:
            user_html_report = UserHtmlReport(self, oks, errors, warnings, genes_by_users)
            user_html_report.save_to_dir(self.report_dir)

        # Admin report in json
        if self.report_admin_json:
            admin_json_report = AdminJsonReport(self, oks, errors, warnings, genes_by_users)
            admin_json_report.save_to_file(self.report_admin_json)

        if self.output_valid or self.output_invalid:
            self.write_gff(oks)


    def parse_groups(self):
        self.allowed_groups = {}
        self.groups_stats = {}
        if not self.no_group:
            groups = open(self.groups_file)
            for g in groups:
                gattrs = g.strip().split("\t")
                if len(gattrs) < 1 or len(gattrs) > 2:
                    print "Failed loading annotation groups on line: "+user
                    sys.exit(1)
                if len(gattrs) == 2:
                    gos = [id.strip() for id in gattrs[1].strip().split(",")]
                gos = []
                self.allowed_groups[gattrs[0]] = gos

    def write_gff(self, oks):
        # Write output GFF
        if self.output_valid or self.output_invalid:
            all_ok = []
            for o in oks:
                all_ok += [ x.wa_id for x in oks[o] ]

        output_source = ["apollo"]

        if self.output_valid:
            out_handle = open(self.output_valid, "w")
            in_handle = open(self.in_file)

            recs = []
            for rec in GFF.parse(in_handle):
                rec.annotations = {}
                rec.seq = ""
                new_feats = []

                for f in rec.features:
                    if (f.type == "gene") and (f.qualifiers['ID'][0] in all_ok):
                        f.qualifiers['source'] = output_source
                        new_feats.append(f)
                        for child in f.sub_features: # mRNA
                            child.qualifiers['source'] = output_source
                            for gchild in child.sub_features: # exons, cds, ...
                                gchild.qualifiers['source'] = output_source
                                for ggchild in gchild.sub_features: # exotic stuff (non_canonical_five_prime_splice_site non_canonical_three_prime_splice_site stop_codon_read_through)
                                    ggchild.qualifiers['source'] = output_source

                rec.features = new_feats

                if len(rec.features):
                    recs.append(rec)

            GFF.write(recs, out_handle)

            in_handle.close()
            out_handle.close()

        if self.output_invalid:
            out_inv_handle = open(self.output_invalid, "w")
            in_handle = open(self.in_file)

            recs = []
            for rec in GFF.parse(in_handle):
                rec.annotations = {}
                rec.seq = ""
                new_feats = []

                for f in rec.features:
                    if (f.type != "gene" or ((f.type == "gene") and (f.qualifiers['ID'][0] not in all_ok))):
                        f.qualifiers['source'] = output_source
                        new_feats.append(f)
                        for child in f.sub_features: # mRNA
                            child.qualifiers['source'] = output_source
                            for gchild in child.sub_features: # exons, cds, ...
                                gchild.qualifiers['source'] = output_source
                                for ggchild in gchild.sub_features: # exotic stuff (non_canonical_five_prime_splice_site non_canonical_three_prime_splice_site stop_codon_read_through)
                                    ggchild.qualifiers['source'] = output_source

                rec.features = new_feats
                if len(rec.features):
                    recs.append(rec)

            GFF.write(recs, out_inv_handle)

            in_handle.close()
            out_inv_handle.close()


    def parse_args(self):

        parser = argparse.ArgumentParser()
        parser.add_argument("in_gff", help="The gff file to inspect")
        parser.add_argument("genome", help="Genome file (fasta)")
        parser.add_argument("-g", "--groups", help="List of annotation groups (optional, tabular, col1=human readable name, col2=comma-separated list of GO ids (GO:0000000))")
        parser.add_argument("-a", "--apollo", help="Apollo server url", required=True)
        parser.add_argument("-o", "--out_gff", help="Output gff file where valid genes will be written")
        parser.add_argument("-i", "--out_inv_gff", help="Output gff file where invalid genes will be written")
        parser.add_argument("--report_dir", help="Output directory where report files will be created (one file by user)")
        parser.add_argument("--report_admin_txt", help="Output an admin report in TXT format to given path")
        parser.add_argument("--report_admin_json", help="Output an admin report in JSON format to given path")
        parser.add_argument("--report_admin_html", help="Output an admin report in HTML format to given path")
        parser.add_argument("--apollo-1x", action="store_true", help="Add this flag when the --in_gff file comes from an Apollo 1.X version")
        parser.add_argument("--split-users", action="store_true", help="Add this flag to remove the @something suffix from apollo user names")
        args = parser.parse_args()

        self.wa_url = args.apollo
        if not self.wa_url.endswith('/'):
            self.wa_url +=  '/'
        self.genome = os.path.abspath(args.genome)
        if args.groups:
            self.groups_file = os.path.abspath(args.groups)
            self.no_group = False
        else:
            self.groups_file = None
            self.no_group = True

        self.in_file = os.path.abspath(args.in_gff)
        self.output_valid = os.path.abspath(args.out_gff)
        self.output_invalid = os.path.abspath(args.out_inv_gff)
        self.report_dir = None
        if args.report_dir:
            self.report_dir = os.path.abspath(args.report_dir)
        self.report_admin_txt = None
        if args.report_admin_txt:
            self.report_admin_txt = os.path.abspath(args.report_admin_txt)
        self.report_admin_html = None
        if args.report_admin_html:
            self.report_admin_html = os.path.abspath(args.report_admin_html)
        self.report_admin_json = None
        if args.report_admin_json:
            self.report_admin_json = os.path.abspath(args.report_admin_json)

        self.apollo_1x = args.apollo_1x
        self.split_users = args.split_users

        if self.report_dir and not os.path.isdir(self.report_dir):
            print "Directory '%s' does not exist" % self.report_dir
            sys.exit(1)

        print "Reading gff file '"+self.in_file+"'"


    def compute_scaf_lengths(self):
        # Compute the length of each scaffold
        print("Computing scaffold lengths...")
        self.scaf_lengths = {}
        for scaf in SeqIO.parse(self.genome, "fasta"):
            self.scaf_lengths[scaf.name] = len(scaf.seq)

    def validate_genes(self):
        in_handle = open(self.in_file)
        for rec in GFF.parse(in_handle):
            for f in rec.features:
                if (f.type == "gene"):

                    gene = Gene(f, rec.id, self.scaf_lengths[rec.id], self.allowed_groups, self.group_tags, self.apollo_1x, self.no_group, self.split_users)

                    self.all_genes[gene.wa_id] = gene

                    # Count number of genes with goid
                    if gene.has_goid:
                        self.genes_with_goid += 1

                    # Collect stats on groups
                    for g in gene.groups:
                        if g not in self.groups_stats:
                            self.groups_stats[g] = 0
                        self.groups_stats[g] += 1

                    new_part = gene.part
                    new_allele = gene.allele

                    # Collect wa_errors
                    self.wa_errors.extend(gene.wa_errors)

                    if not new_part and not new_allele:
                        self.genes_seen_once += 1

                    # keep track of splitted genes
                    if new_part:
                        part_gene_key = gene.display_id
                        if new_allele:
                            part_gene_key = gene.display_id+", allele "+new_allele
                        if part_gene_key not in self.splitted_genes:
                            self.splitted_genes[part_gene_key] = {}
                        if new_part in self.splitted_genes[part_gene_key]:
                            identical = self.splitted_genes[part_gene_key][new_part]

                            gene.errors.append(GeneError(GeneError.PART_SAME, gene, {'other_name': identical.display_id, 'other_scaff': identical.scaffold, 'other_start': identical.f.location.start, 'other_end': identical.f.location.end}))

                        self.splitted_genes[part_gene_key][new_part] = gene


                    # keep track of duplicated genes
                    if new_allele:
                        allele_gene_key = gene.display_id
                        if allele_gene_key not in self.duplicated_genes:
                            self.duplicated_genes[allele_gene_key] = {}
                        if new_allele in self.duplicated_genes[allele_gene_key]:
                            identical = self.duplicated_genes[allele_gene_key][new_allele]

                            if identical.part == new_part:

                                gene.errors.append(GeneError(GeneError.ALLELE_SAME, gene, {'other_name': identical.display_id, 'other_scaff': identical.scaffold, 'other_start': identical.f.location.start, 'other_end': identical.f.location.end}))

                        self.duplicated_genes[allele_gene_key][new_allele] = gene
                else:
                    fake_gene = Gene(f, rec.id, self.scaf_lengths[rec.id], self.allowed_groups, self.group_tags, self.apollo_1x)
                    self.wa_errors.append(WAError(WAError.UNEXPECTED_FEATURE, fake_gene))

        in_handle.close()


    def errors_by_users(self):

        errors = {}

        for g in self.all_genes.values():
            if g.owner not in errors:
                errors[g.owner] = []
            errors[g.owner].extend(g.errors)

        return errors


    def warnings_by_users(self):

        warnings = {}

        for g in self.all_genes.values():
            if g.owner not in warnings:
                warnings[g.owner] = []
            warnings[g.owner].extend(g.warnings)

        return warnings


    def ok_by_users(self):

        ok = {}

        for g in self.all_genes.values():
            if len(g.errors) == 0:
                if g.owner not in ok:
                    ok[g.owner] = []
                ok[g.owner].append(g)

        return ok


    def genes_by_users(self):

        genes = {}

        for g in self.all_genes.values():
            if g.owner not in genes:
                genes[g.owner] = []
            genes[g.owner].append(g)

        return genes


    def post_validation(self):

        # validate splitted and duplicated genes once we collected the whole list
        for s in self.splitted_genes.keys():
            if len(self.splitted_genes[s]) == 1:
                for p in self.splitted_genes[s].keys():
                    gene = self.splitted_genes[s][p]

                    if len(gene.display_id) == 32 and re.match("^[A-F0-9]+$", gene.display_id): # If there is no name, it's probably the cause of the problem
                        gene.errors.append(GeneError(GeneError.PART_SINGLE, gene))
                    else: # If there is a symbol it's probably an incomplete gene
                        gene.warnings.append(GeneError(GeneError.PART_SINGLE_NAMED, gene))

                    self.all_genes[gene.wa_id] = gene

        for s in self.duplicated_genes.keys():
            if len(self.duplicated_genes[s]) == 1:
                for p in self.duplicated_genes[s].keys():
                    gene = self.duplicated_genes[s][p]

                    gene.errors.append(GeneError(GeneError.ALLELE_SINGLE, gene))

                    self.all_genes[gene.wa_id] = gene


if __name__ == '__main__':
    wachecker = WAChecker()

    wachecker.main()
