#!/usr/bin/python

import argparse
import copy
import os
import re
import sys
import unicodedata

from BCBio import GFF

from Bio import SeqIO

from wacheck.Gene import Gene
from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError
from wacheck.report.AdminJsonReport import AdminJsonReport


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


class WAChecker():

    def main(self):

        self.parse_args()

        # Prepare internal properties
        self.group_tags = ['AnnotGroup']
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
        genes_by_groups = self.genes_by_groups()

        self.names = sorted(self.genes_by_users().keys())

        # Write reports
        admin_json_report = AdminJsonReport(self, oks, errors, warnings)
        admin_json_report.save_to_file(self.report_admin_json)

        self.write_gff(oks)

        if not self.no_group:
            self.write_gff_by_groups(genes_by_groups, valid_only=True)
            self.write_gff_by_groups(genes_by_groups, valid_only=False)

        self.write_deleted(oks)

    def parse_groups(self):
        self.allowed_groups = {}
        self.groups_stats = {}
        if not self.no_group:
            groups = open(self.groups_file)
            for g in groups:
                gattrs = g.strip().split("\t")
                if len(gattrs) < 1 or len(gattrs) > 2:
                    print("Failed loading annotation groups on line: %s" % g)
                    sys.exit(1)
                if len(gattrs) == 2:
                    gos = [id.strip() for id in gattrs[1].strip().split(",")]
                gos = []
                self.allowed_groups[gattrs[0]] = gos

    def write_gff(self, oks):
        # Write output GFF
        if self.output_valid or self.output_invalid:
            all_ok = []
            deleted = []
            for o in oks:
                all_ok += [x.wa_id for x in oks[o] if not x.is_deleted]
                deleted += [x.wa_id for x in oks[o] if x.is_deleted]

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
                        for child in f.sub_features:  # mRNA
                            child.qualifiers['source'] = output_source
                            for gchild in child.sub_features:  # exons, cds, ...
                                gchild.qualifiers['source'] = output_source
                                for ggchild in gchild.sub_features:  # exotic stuff (non_canonical_five_prime_splice_site non_canonical_three_prime_splice_site stop_codon_read_through)
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
                        for child in f.sub_features:  # mRNA
                            child.qualifiers['source'] = output_source
                            for gchild in child.sub_features:  # exons, cds, ...
                                gchild.qualifiers['source'] = output_source
                                for ggchild in gchild.sub_features:  # exotic stuff (non_canonical_five_prime_splice_site non_canonical_three_prime_splice_site stop_codon_read_through)
                                    ggchild.qualifiers['source'] = output_source

                rec.features = new_feats
                if len(rec.features):
                    recs.append(rec)

            GFF.write(recs, out_inv_handle)

            in_handle.close()
            out_inv_handle.close()

    def write_gff_by_groups(self, oks, valid_only):

        output_source = ["apollo"]

        # Write output GFF
        waid_to_group = {}
        for group in oks:
            waid_to_group = {**waid_to_group, **{x.wa_id: group for x in oks[group] if not x.is_deleted}}

        if valid_only:
            in_handle = open(self.output_valid)
            suffix = "_valid"
        else:
            in_handle = open(self.in_file)
            suffix = "_raw"

        recs = {}
        for rec in GFF.parse(in_handle):
            new_feats = {}

            for f in rec.features:
                if (f.type == "gene") and (f.qualifiers['ID'][0] in waid_to_group):
                    group = waid_to_group[f.qualifiers['ID'][0]]
                    f.qualifiers['source'] = output_source
                    if group not in new_feats:
                        new_feats[group] = []
                    new_feats[group].append(f)
                    for child in f.sub_features:  # mRNA
                        child.qualifiers['source'] = output_source
                        for gchild in child.sub_features:  # exons, cds, ...
                            gchild.qualifiers['source'] = output_source
                            for ggchild in gchild.sub_features:  # exotic stuff (non_canonical_five_prime_splice_site non_canonical_three_prime_splice_site stop_codon_read_through)
                                ggchild.qualifiers['source'] = output_source

            for group in new_feats:
                rec.annotations = {}
                rec.seq = ""
                newrec = copy.deepcopy(rec)
                newrec.features = new_feats[group]

                if len(newrec.features):
                    if group not in recs:
                        recs[group] = []
                    recs[group].append(newrec)

        for group in recs:
            out_file = os.path.join(self.output_by_groups, "%s%s.gff" % (slugify(group), suffix))
            with open(out_file, "a") as out_handle:
                GFF.write(recs[group], out_handle)

        in_handle.close()

    def write_deleted(self, oks):
        # Write output tsv
        deleted = []
        for o in oks:
            deleted += [x.name for x in oks[o] if x.is_deleted]

        out_handle = open(self.output_deleted, "w")

        for d in deleted:
            out_handle.write(d + '\n')

        out_handle.close()

    def parse_args(self):

        parser = argparse.ArgumentParser()
        parser.add_argument("in_gff", help="The gff file to inspect")
        parser.add_argument("genome", help="Genome file (fasta)")
        parser.add_argument("-g", "--groups", help="List of annotation groups (optional, tabular, col1=human readable name, col2=comma-separated list of GO ids (GO:0000000))")
        parser.add_argument("-a", "--apollo", help="Apollo server url", required=True)
        parser.add_argument("-o", "--out", help="Output directory")
        parser.add_argument("--split-users", action="store_true", help="Add this flag to remove the @something suffix from apollo user names")
        args = parser.parse_args()

        self.wa_url = args.apollo
        if not self.wa_url.endswith('/'):
            self.wa_url += '/'
        self.genome = os.path.abspath(args.genome)
        if args.groups:
            self.groups_file = os.path.abspath(args.groups)
            self.no_group = False
        else:
            self.groups_file = None
            self.no_group = True

        self.in_file = os.path.abspath(args.in_gff)
        self.output_valid = os.path.join(os.path.abspath(args.out), 'valid.gff')
        self.output_invalid = os.path.join(os.path.abspath(args.out), 'invalid.gff')
        self.output_deleted = os.path.join(os.path.abspath(args.out), 'deleted.tsv')
        self.report_admin_json = os.path.join(os.path.abspath(args.out), "report.json")

        os.makedirs(args.out, exist_ok=True)

        if not self.no_group:
            self.output_by_groups = os.path.join(os.path.abspath(args.out), 'by_groups')
            os.makedirs(self.output_by_groups, exist_ok=True)

        self.split_users = args.split_users

        print("Reading gff file '%s'" % self.in_file)

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
                if (f.type == "gene") and ('status' not in f.qualifiers or not f.qualifiers['status'] or f.qualifiers['status'][0].lower() != "deleted"):

                    gene = Gene(f, rec.id, self.scaf_lengths[rec.id], self.allowed_groups, self.group_tags, self.no_group, self.split_users)

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
                            part_gene_key = gene.display_id + ", allele " + new_allele
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
                elif 'status' in f.qualifiers and f.qualifiers['status'] and f.qualifiers['status'][0].lower() == "deleted":
                    gene = Gene(f, rec.id, self.scaf_lengths[rec.id], self.allowed_groups, self.group_tags, self.no_group, self.split_users)

                    self.all_genes[gene.wa_id] = gene
                else:
                    fake_gene = Gene(f, rec.id, self.scaf_lengths[rec.id], self.allowed_groups, self.group_tags)
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

    def genes_by_groups(self):

        groups = {}

        for g in self.all_genes.values():
            for o in g.groups:
                if o not in groups:
                    groups[o] = []
                groups[o].append(g)

        return groups

    def post_validation(self):

        # validate splitted and duplicated genes once we collected the whole list
        for s in self.splitted_genes.keys():
            if len(self.splitted_genes[s]) == 1:
                for p in self.splitted_genes[s].keys():
                    gene = self.splitted_genes[s][p]

                    if len(gene.display_id) == 32 and re.match("^[A-F0-9]+$", gene.display_id):  # If there is no name, it's probably the cause of the problem
                        gene.errors.append(GeneError(GeneError.PART_SINGLE, gene))
                    else:  # If there is a symbol it's probably an incomplete gene
                        gene.warnings.append(GeneError(GeneError.PART_SINGLE_NAMED, gene))

                    self.all_genes[gene.wa_id] = gene

        for s in self.duplicated_genes.keys():
            if len(self.duplicated_genes[s]) == 1:
                for p in self.duplicated_genes[s].keys():
                    gene = self.duplicated_genes[s][p]

                    gene.errors.append(GeneError(GeneError.ALLELE_SINGLE, gene))

                    self.all_genes[gene.wa_id] = gene

        # Check symbol and name are unique
        seen_symbols = {}
        warned_symbols = []
        for g in self.all_genes.values():
            if not g.allele and not g.part and not g.is_deleted and g.symbol is not None:
                if g.symbol not in seen_symbols:
                    seen_symbols[g.symbol] = g
                else:
                    if g.symbol not in warned_symbols:
                        seen_symbols[g.symbol].errors.append(GeneError(GeneError.SYMBOL_NOT_UNIQUE, seen_symbols[g.symbol]))
                    warned_symbols.append(g.symbol)
                    g.errors.append(GeneError(GeneError.SYMBOL_NOT_UNIQUE, g))

        seen_names = {}
        warned_names = []
        for g in self.all_genes.values():
            if not g.allele and not g.part and not g.is_deleted and g.name is not None:
                if g.name not in seen_names:
                    seen_names[g.name] = g
                else:
                    if g.name not in warned_names:
                        seen_names[g.name].errors.append(GeneError(GeneError.NAME_NOT_UNIQUE, seen_names[g.name]))
                    warned_names.append(g.name)
                    g.errors.append(GeneError(GeneError.NAME_NOT_UNIQUE, g))


if __name__ == '__main__':
    wachecker = WAChecker()

    wachecker.main()
