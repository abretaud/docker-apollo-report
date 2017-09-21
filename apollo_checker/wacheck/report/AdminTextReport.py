from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError

from wacheck.report.TextReport import TextReport

class AdminTextReport(TextReport):

    def __init__(self, checker, ok, errors, warnings):

        TextReport.__init__(self, checker, ok, errors, warnings)

        print self.render()

    def save_to_file(self, path):

        report = self.render()

        out_handle = open(path, "w")

        out_handle.write(report)

        out_handle.close()

    def render_by_user(self):

        res = ""

        for u in self.user_names:

            if len(self.errors[u]) == 0 and len(self.warnings[u]) == 0 and len(self.ok[u]) == 0:
                res += " ** "+u+": no annotation found"
                res += "\n\n\n"

            else:
                res += " ** "+u+":\n"

                if self.errors and u in self.errors and len(self.errors[u]) > 0:
                    res += "The following "+str(len(self.errors[u]))+" errors were found (blocking):\n"
                    for e in self.errors[u]:
                        res += "    "+self.render_error(e)+"\n"
                    res += "\n\n"

                if self.warnings and u in self.warnings and len(self.warnings[u]) > 0:
                    res += "The following "+str(len(self.warnings[u]))+" warnings were found (non blocking, potential issues):\n"
                    for w in self.warnings[u]:
                        res += "    "+self.render_warning(w)+"\n"
                    res += "\n\n"

                if self.ok and u in self.ok and len(self.ok[u]) > 0:
                    res += "The following "+str(len(self.ok[u]))+" genes are valid:\n"
                    for o in self.ok[u]:
                        res += "    "+self.render_ok(o)+"\n"
                    res += "\n\n"

                res += "\n"

        return res


    def render_splitted(self):

        res = ""

        res += "\n\n"
        res += "Splitted genes:\n\n"

        for gene, parts in self.splitted_genes.items():
            pl = ()
            locs = ()
            for p_id, part in parts.items():
                pl += (p_id,)
                locs += (part.scaffold+":"+str(part.f.location.start)+".."+str(part.f.location.end),)
            res += gene+": "+str(len(parts))+" parts ("+", ".join(sorted(pl))+")   ["+", ".join(locs)+"]\n"

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
        res += "Parts repartition:\n\n"
        for p in sorted(part_counts.keys()):
            res += p+": "+str(part_counts[p])+"\n"

        return res


    def render_duplicated(self):

        res = ""

        res += "\n\n"
        res += "Duplicated genes:\n\n"

        for gene, copies in self.duplicated_genes.items():
            pl = ()
            locs = ()
            for c_id, copy in copies.items():
                pl += (c_id,)
                locs += (copy.scaffold+"\t"+str(copy.f.location.start)+"\t"+str(copy.f.location.end)+"\t"+("-" if str(copy.f.location.strand) == "-1" else "+"),)
        #    res += gene+": "+str(len(copies))+" alleles ("+", ".join(sorted(pl))+")   ["+", ".join(locs)+"]"+"\n"
            res += gene+"\t"+str(len(copies))+"\t"+",".join(sorted(pl))+"\t"+"\t".join(locs)+"\n"

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
        res += "Alleles repartition:\n\n"
        for a in sorted(allele_counts.keys()):
            res += a+": "+str(allele_counts[a])+"\n"

        return res


    def render_groups(self):

        res = ""

        res += "\n\n"
        res += "Group repartition:\n\n"
        for g_name, g_num in iter(sorted(self.groups.iteritems(), key=lambda v: v[0].upper())):
            res += g_name+": "+str(g_num)+"\n"

        return res


    def render_users(self):

        res = ""

        res += "\n\n"
        res += "User repartition:\n\n"
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
                res += u+": "+str(total_num_genes)+" ("+str(num_ok)+" valid genes, "+str(total_num_genes-num_ok)+" invalid genes, "+str(num_warn)+" warnings, "+str(num_err)+" issues)\n"

        return res


    def render_stats(self):

        res = ""

        res += "\n\n"
        res += str(self.genes_with_goid)+" genes have at least one goid"

        res += "\n\n"
        res += "Found "+str(self.total_genes)+" genes ("+str(self.total_ok)+" valid genes, "+str(self.total_genes-self.total_ok)+" invalid genes, "+str(self.total_warnings)+" warnings, "+str(self.total_errors)+" issues)\n"
        res += "      "+str(self.genes_seen_once)+" genes with only 1 allele and 1 part\n"
        res += "      "+str(len(self.duplicated_genes))+" genes (or parts of genes) with multiple alleles\n"
        res += "      "+str(len(self.splitted_genes))+" genes (or alleles) with multiple parts\n"

        return res


    def render(self):

        res = ""

        res += self.render_by_user()
        res += self.render_splitted()
        res += self.render_parts()
        res += self.render_duplicated()
        res += self.render_alleles()
        res += self.render_groups()
        res += self.render_users()
        res += self.render_stats()

        if len(self.wa_errors) > 0:
            res += "\n\n\n"
            res += "Found "+str(len(self.wa_errors))+" unexpected errors in the gff produced by WebApollo:\n"
            for e in self.wa_errors:
                res += "    "+self.render_wa_error(e)+"\n"

        return res
