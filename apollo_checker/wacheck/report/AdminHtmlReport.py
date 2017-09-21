from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError

from wacheck.report.HtmlReport import HtmlReport

from datetime import datetime

class AdminHtmlReport(HtmlReport):

    def __init__(self, checker, ok, errors, warnings):

        HtmlReport.__init__(self, checker, ok, errors, warnings)

    def save_to_file(self, path):

        report = self.render()

        out_handle = open(path, "w")

        out_handle.write(report)

        out_handle.close()

    def render_by_user(self):

        res = ""

        for u in self.user_names:

            if len(self.errors[u]) == 0 and len(self.warnings[u]) == 0 and len(self.ok[u]) == 0:
                res += "<h3> ** "+self.user_names[u]+": no annotation found</h3>"
                res += "\n\n\n"

            else:
                res += "<h3> ** "+u+":</h3>\n"

                if self.errors and u in self.errors and len(self.errors[u]) > 0:
                    res += "<p>The following "+str(len(self.errors[u]))+" <b>errors</b> were found (blocking):</p><ul>\n"
                    for e in self.errors[u]:
                        res += "<li>"+self.render_error(e)+"</li>\n"
                    res += "</ul>\n\n"

                if self.warnings and u in self.warnings and len(self.warnings[u]) > 0:
                    res += "<p>The following "+str(len(self.warnings[u]))+" <b>warnings</b> were found (non blocking, potential issues):</p><ul>\n"
                    for w in self.warnings[u]:
                        res += "<li>"+self.render_warning(w)+"</li>\n"
                    res += "</ul>\n\n"

                if self.ok and u in self.ok and len(self.ok[u]) > 0:
                    res += "<p>The following "+str(len(self.ok[u]))+" genes are <b>valid</b>:</p><ul>\n"
                    for o in self.ok[u]:
                        res += "<li>"+self.render_ok(o)+"</li>\n"
                    res += "</ul>\n\n"

                res += "\n"

        return res


    def render_splitted(self):

        res = ""

        res += "\n\n"
        res += "<h2>Splitted genes:</h2><ul>\n\n"

        for gene, parts in self.splitted_genes.items():
            pl = ()
            locs = ()
            for p_id, part in parts.items():
                pl += ("<a href=\""+self.get_wa_url(part.scaffold, part.f.location.start, part.f.location.end)+"\">"+p_id+"</a>",)
            res += "<li>"+gene+": "+str(len(parts))+" parts ("+", ".join(sorted(pl))+")</li>\n"

        res += "</ul>"

        return res


    def render_parts(self):

        part_counts = {}
        for gene, parts in self.splitted_genes.items():
            for p_id in parts.keys():
                if p_id not in part_counts:
                    part_counts[p_id] = 0
                part_counts[p_id] += 1

        res = ""

        res += "\n\n"
        res += "<h2>Parts repartition:</h2><ul>\n\n"
        for p in sorted(part_counts.keys()):
            res += "<li>"+p+": "+str(part_counts[p])+"</li>\n"

        res += "</ul>"

        return res


    def render_duplicated(self):

        res = ""

        res += "\n\n"
        res += "<h2>Duplicated genes:</h2><ul>\n\n"

        for gene, copies in self.duplicated_genes.items():
            pl = ()
            locs = ()
            for c_id, copy in copies.items():
                pl += ("<a href=\""+self.get_wa_url(copy.scaffold, copy.f.location.start, copy.f.location.end)+"\">"+c_id+"</a> ("+("-" if str(copy.f.location.strand) == "-1" else "+")+")",)
            res += "<li>"+gene+"\t"+str(len(copies))+"\t"+", ".join(pl)+"</li>\n"

        res += "</ul>"

        return res


    def render_alleles(self):

        allele_counts = {}
        for gene, copies in self.duplicated_genes.items():
            for c_id in copies.keys():
                if c_id not in allele_counts:
                    allele_counts[c_id] = 0
                allele_counts[c_id] += 1

        res = ""

        res += "\n\n"
        res += "<h2>Alleles repartition:</h2><ul>\n\n"
        for a in sorted(allele_counts.keys()):
            res += "<li>"+a+": "+str(allele_counts[a])+"</li>\n"

        res += "</ul>"

        return res


    def render_groups(self):

        res = ""

        res += "\n\n"
        res += "<h2>Group repartition:</h2><ul>\n\n"
        for g_name, g_num in iter(sorted(self.groups.iteritems(), key=lambda v: v[0].upper())):
            res += "<li>"+g_name+": "+str(g_num)+"</li>\n"

        res += "</ul>"

        return res


    def render_users(self):

        res = ""

        res += "\n\n"
        res += "<h2>User repartition:</h2><ul>\n\n"
        for u in sorted(self.user_names, key=lambda v: v.upper()):
            total_num_genes = len(self.genes_by_users[u])
            num_ok = 0
            if u in self.ok:
                num_ok = len(self.ok[u])
            num_warn = 0
            if u in self.warnings:
                num_warn = len(self.warnings[u])
            num_err = 0
            if u in self.errors:
                num_err = len(self.errors[u])

            if total_num_genes > 0:
                res += "<li>"+u+": "+str(total_num_genes)+" ("+str(num_ok)+" valid genes, "+str(total_num_genes-num_ok)+" invalid genes, "+str(num_warn)+" warnings, "+str(num_err)+" issues)</li>\n"

        res += "</ul>"

        return res


    def render_stats(self):

        res = ""

        res += "\n\n"
        res += "<h2>General stats:</h2>\n\n"
        res += "<p>"+str(self.genes_with_goid)+" genes have at least one goid</p>"

        res += "<p></p>\n\n"
        res += "<p>Found "+str(self.total_genes)+" genes ("+str(self.total_ok)+" valid genes, "+str(self.total_genes-self.total_ok)+" invalid genes, "+str(self.total_warnings)+" warnings, "+str(self.total_errors)+" issues)</p><ul>\n"
        res += "      <li>"+str(self.genes_seen_once)+" genes with only 1 allele and 1 part</li>\n"
        res += "      <li>"+str(len(self.duplicated_genes))+" genes (or parts of genes) with multiple alleles</li>\n"
        res += "      <li>"+str(len(self.splitted_genes))+" genes (or alleles) with multiple parts</li>\n"

        res += "</ul>"

        return res


    def render(self):

        res = """
        <html>
        <head>
        <meta charset="UTF-8">
        </head>
        <body>

        <h1>Manual annotation report</h1>"""

        res += "<p>This is an automatic report concerning the genes that were manually annotated.</p>"

        res += "<p>This report is updated every night, and the present report have been generated on: <b>"+str(datetime.now())+"</b> (Paris, France time).</p>"

        if len(self.wa_errors) > 0:
            res += "\n\n\n"
            res += "<h2>Found "+str(len(self.wa_errors))+" unexpected errors in the gff produced by WebApollo:</h2><ul>\n"
            for e in self.wa_errors:
                res += "    <li>"+self.render_wa_error(e)+"</li>\n"

            res += "</ul>"

        res += self.render_by_user()
        res += self.render_splitted()
        res += self.render_parts()
        res += self.render_duplicated()
        res += self.render_alleles()
        res += self.render_groups()
        res += self.render_users()
        res += self.render_stats()


        res += """</body>
        </html>
        """

        return res
