import json
from collections import OrderedDict
from datetime import datetime

from wacheck.report.HtmlReport import HtmlReport


class AdminJsonReport(HtmlReport):

    def __init__(self, checker, ok, errors, warnings, permissions):

        HtmlReport.__init__(self, checker, ok, errors, warnings)
        self.permissions = permissions

    def save_to_file(self, path):

        report = self.render()

        out_handle = open(path, "w")

        out_handle.write(report)

        out_handle.close()

    def render_by_user(self):

        res = OrderedDict()
        for u in self.user_names:

            res[u] = {'errors': [], 'warnings': [], 'ok': [], 'deleted': [], 'num_genes': len(self.genes_by_users[u])}

            if self.errors and u in self.errors and len(self.errors[u]) > 0:
                for e in self.errors[u]:
                    res[u]['errors'].append(self.render_error(e))

            if self.warnings and u in self.warnings and len(self.warnings[u]) > 0:
                for w in self.warnings[u]:
                    res[u]['warnings'].append(self.render_warning(w))

            if self.ok and u in self.ok and len(self.ok[u]) > 0:
                for o in self.ok[u]:
                    if o.is_deleted:
                        res[u]['deleted'].append(self.render_deleted(o))
                    else:
                        res[u]['ok'].append(self.render_ok(o))

        return res

    def render_by_group(self):

        res = OrderedDict()

        for group_name, genes in self.genes_by_groups.items():

            res[group_name] = {'errors': [], 'warnings': [], 'ok': [], 'num_genes': len(genes)}

            for gene in genes:

                if gene.errors:
                    for e in gene.errors:
                        res[group_name]['errors'].append(self.render_error(e))

                if gene.warnings:
                    for w in gene.warnings:
                        res[group_name]['warnings'].append(self.render_warning(w))

                if not gene.errors:
                    if not gene.is_deleted:
                        res[group_name]['ok'].append(self.render_ok(gene))
                    # Deleted genes are not in any group...

        # Move unknowns at the end of the list
        if 'Unknown' in res:
            unknowns = res['Unknown']
            del res['Unknown']
            res['Unknown (no group defined)'] = unknowns

        return res

    def render_splitted(self):

        res = OrderedDict()

        for gene, parts in self.splitted_genes.items():
            pl = ()
            for p_id, part in parts.items():
                pl += ("<a href=\"" + self.get_wa_url(part) + "\">" + p_id + "</a>",)
            res[gene] = sorted(pl)

        return res

    def render_parts(self):

        res = OrderedDict()

        part_counts = OrderedDict()
        for gene, parts in self.splitted_genes.items():
            for p_id in parts.keys():
                if p_id not in part_counts:
                    part_counts[p_id] = 0
                part_counts[p_id] += 1

        for p in sorted(part_counts.keys()):
            res[p] = str(part_counts[p])

        return res

    def render_duplicated(self):

        res = OrderedDict()

        for gene, copies in self.duplicated_genes.items():
            pl = ()
            for c_id, copy in copies.items():
                pl += ("<a href=\"" + self.get_wa_url(copy) + "\">" + c_id + "</a> (" + ("-" if str(copy.f.location.strand) == "-1" else "+") + ")",)
            res[gene] = pl

        return res

    def render_alleles(self):

        res = OrderedDict()

        allele_counts = OrderedDict()
        for gene, copies in self.duplicated_genes.items():
            for c_id in copies.keys():
                if c_id not in allele_counts:
                    allele_counts[c_id] = 0
                allele_counts[c_id] += 1

        for a in sorted(allele_counts.keys()):
            res[a] = allele_counts[a]

        return res

    def render_groups(self):

        res = OrderedDict()

        for g_name, g_num in iter(sorted(self.groups.items(), key=lambda v: v[0].upper())):
            res[g_name] = g_num

        return res

    def render_stats(self):

        res = OrderedDict()

        res['goid'] = self.genes_with_goid

        res['total_genes'] = self.total_genes
        res['genes_ok'] = self.total_ok
        res['genes_invalid'] = self.total_genes - self.total_ok
        res['total_warnings'] = self.total_warnings
        res['total_errors'] = self.total_errors
        res['total_deleted'] = self.total_deleted
        res['genes_seen_once'] = self.genes_seen_once

        return res

    def render(self):

        res = OrderedDict()
        res['time'] = str(datetime.now())
        res['wa_errors'] = []

        if len(self.wa_errors) > 0:
            for e in self.wa_errors:
                res['wa_errors'].append(self.render_wa_error(e))

        res['genes_by_users'] = self.render_by_user()
        res['genes_by_groups'] = self.render_by_group()
        res['splitted'] = self.render_splitted()
        res['parts'] = self.render_parts()
        res['duplicated'] = self.render_duplicated()
        res['alleles'] = self.render_alleles()
        res['groups'] = self.render_groups()
        res['global_stats'] = self.render_stats()
        res['permissions'] = self.permissions

        return json.dumps(res)
