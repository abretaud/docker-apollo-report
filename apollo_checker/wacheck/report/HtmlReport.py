from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError
from wacheck.report.Report import Report


class HtmlReport(Report):

    def render_wa_error(self, e):

        if e.code == WAError.UNEXPECTED_FEATURE:
            return "Unexpected '" + e.gene.f.type + "' feature <a href=\"" + self.get_wa_url(e) + "\">" + e.gene.wa_id + "</a>, it will not be used in future OGS."

        if e.code == WAError.UNEXPECTED_SUB_FEATURE:
            return "unexpected '" + e.error_desc['child_type'] + "' sub-element <a href=\"" + self.get_wa_url(e) + "\">" + e.error_desc['child_id'] + "</a> for gene '" + e.gene.wa_id + "'"

        if e.code == WAError.OUTSIDE_SCAFFOLD_START:
            return "ERROR: " + e.gene.wa_id + " start position " + str(e.start) + " is higher than the scaffold size " + str(e.gene.scaffold_size)

        if e.code == WAError.OUTSIDE_SCAFFOLD_END:
            return "ERROR: " + e.gene.wa_id + " end position " + str(e.end) + " is higher than the scaffold size " + str(e.gene.scaffold_size)

        if e.code == WAError.MULTIPLE_SUB_FEATURE:
            return "ERROR: multiple child element (" + str(e.error_desc['num_children']) + ") for gene <a href=\"" + self.get_wa_url(e) + "\">" + e.gene.wa_id + "</a>"

        if e.code == WAError.WRONG_GENE_START:
            return "ERROR: " + e.gene.wa_id + " start position " + str(e.start) + " is not coherent with its children (expected " + str(e.error_desc['expected']) + ")"

        if e.code == WAError.WRONG_GENE_END:
            return "ERROR: " + e.gene.wa_id + " end position " + str(e.end) + " is not coherent with its children (expected " + str(e.error_desc['expected']) + ")"

        if e.code == WAError.WRONG_GENE_STRAND:
            return "ERROR: " + e.gene.wa_id + " strand " + str(e.strand) + " is not coherent with its children (expected " + str(e.error_desc['expected']) + ")"

    def render_error(self, e):

        if e.code == GeneError.SYMBOL_MISSING:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is missing a 'symbol'."

        if e.code == GeneError.SYMBOL_INVALID:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> have an invalid 'symbol': '" + e.error_desc['symbol'] + "'. Use only letters digits and -_.()/ characters."

        if e.code == GeneError.MULTIPLE_MRNAS:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> have " + str(e.error_desc['num']) + " transcripts. Check that they are real splice variants and not erroneous duplications."

        if e.code == GeneError.CDS_IS_NULL:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> CDS length is null (0). Check that the gene contains a start codon and that the exons are properly defined."

        if e.code == GeneError.CDS_IS_SMALL:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> CDS length is very small (" + str(e.error_desc['len']) + "). Check that the gene contains a start codon and that the exons are properly defined."

        if e.code == GeneError.NAME_MISSING:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is missing a 'Name'."

        if e.code == GeneError.NAME_INVALID:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> should have a human readable 'Name' instead of '" + e.error_desc['name'] + "'."

        if e.code == GeneError.DBXREF_UNKNOWN:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has an unknown dbxref type: '" + e.error_desc['dbxref'] + "'."

        if e.code == GeneError.GROUP_MISPLACED:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> have " + e.error_desc['tag'] + " as a gene DBXref instead of an attribute."

        if e.code == GeneError.GROUP_UNKNOWN:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is in an unknown " + self.group_tags[0] + " group '" + e.error_desc['group'] + "' (check the spelling)."

        if e.code == GeneError.GROUP_NONE:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is not in any group (add an " + self.group_tags[0] + " attribute)."

        if e.code == GeneError.GROUP_MULTIPLE:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is in multiple annotations groups: '" + "', '".join(e.gene.groups) + "'."

        if e.code == GeneError.GROUP_MULTIPLE_SAME:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has been added to the same annotation group '" + e.error_desc['group'] + "' multiple times."

        if e.code == GeneError.ATTRIBUTE_INVALID:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> have an invalid '" + e.error_desc['key'] + "' attribute value ('" + e.error_desc['value'] + "')"

        if e.code == GeneError.PART_SAME:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> and " + e.error_desc['other_name'] + " located at " + self.get_wa_url_other(e.error_desc['other_scaff'], e.error_desc['other_start'], e.error_desc['other_end']) + " are marked as the same part of a gene. If they are the same part of different alleles, add 'Allele' tags to both."

        if e.code == GeneError.PART_SINGLE:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if e.code == GeneError.PART_SINGLE_NAMED:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if e.code == GeneError.ALLELE_SAME:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> and " + e.error_desc['other_name'] + " located at " + self.get_wa_url_other(e.error_desc['other_scaff'], e.error_desc['other_start'], e.error_desc['other_end']) + " are marked as the same allele of a duplicated gene. If they are different parts of the same allele, add 'Part' tags to both."

        if e.code == GeneError.ALLELE_SINGLE:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is the only allele of a gene. If the gene has no other allele, you should remove the 'allele' tag. Otherwise, check that all alleles of the same gene have the same 'symbol'"

        if e.code == GeneError.INTRON_TOO_SMALL:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> contains very short introns. This is not supposed to happen on most genes, check that the gene structure is correct."

        if e.code == GeneError.NEEDS_REVIEW:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is not yet Approved. Change its status once you have finished working on it."

        if e.code == GeneError.INVALID_MRNA_NAME:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has invalid name for its isoforms. Each isoform should be named '<name of the gene> X', where X is a letter (from A to Z)  (e.g. : gluthatione s-transferase A)."

        if e.code == GeneError.SIMILAR_TO:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> contains 'similar to' or '-like' in its name. Use 'putative' instead, and only if you have real doubts on the naming of this gene. If you have sufficient supporting evidences, just write the gene name without 'putative'."

        if e.code == GeneError.SYMBOL_NOT_ID:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has an invalid symbol: don't use OGS ids like DV0000123-RA, they will be generated on OGS release."

        if e.code == GeneError.NAME_NOT_ID:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has an invalid name: don't use OGS ids like DV0000123-RA, they will be generated on OGS release."

        if e.code == GeneError.SYMBOL_NOT_UNIQUE:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has a symbol which is not unique."

        if e.code == GeneError.NAME_NOT_UNIQUE:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> has a name which is not unique."

        if e.code == GeneError.DELETED_MISSING_NAME:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is marked as deleted but doesn't have a gene name."

        if e.code == GeneError.DELETED_WRONG_NAME:
            return "Gene <a href=\"" + self.get_wa_url(e) + "\">" + e.display_id + "</a> is marked as deleted but has a wrong gene name '" + e.error_desc['name'] + "'."

        return "Unexpected error %s" % e.code

    def render_warning(self, w):

        if w.code == GeneError.SYMBOL_MISSING:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is missing a 'symbol'."

        if w.code == GeneError.SYMBOL_INVALID:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> have an invalid 'symbol': '" + w.error_desc['symbol'] + "'. Use only letters digits and -_.()/ characters."

        if w.code == GeneError.MULTIPLE_MRNAS:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> have " + str(w.error_desc['num']) + " transcripts. Check that they are real splice variants and not erroneous duplications."

        if w.code == GeneError.CDS_IS_NULL:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> CDS length is null (0). Check that the gene contains a start codon and that the exons are properly defined."

        if w.code == GeneError.CDS_IS_SMALL:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> CDS length is very small (" + str(w.error_desc['len']) + "). Check that the gene contains a start codon and that the exons are properly defined."

        if w.code == GeneError.NAME_MISSING:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is missing a 'Name'."

        if w.code == GeneError.NAME_INVALID:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> should have a human readable 'Name' instead of '" + w.error_desc['name'] + "'."

        if w.code == GeneError.DBXREF_UNKNOWN:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> has an unknown dbxref type: '" + w.error_desc['dbxref'] + "'."

        if w.code == GeneError.GROUP_MISPLACED:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> have " + w.error_desc['tag'] + " as a gene DBXref instead of a attribute."

        if w.code == GeneError.GROUP_UNKNOWN:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is in an unknown " + self.group_tags[0] + " group '" + w.error_desc['group'] + "' (check the spelling)."

        if w.code == GeneError.GROUP_NONE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is not in any group (add an " + self.group_tags[0] + " attribute)."

        if w.code == GeneError.GROUP_MULTIPLE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is in multiple annotations groups: '" + "', '".join(w.gene.groups) + "'."

        if w.code == GeneError.GROUP_MULTIPLE_SAME:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> has been added to the same annotation group '" + w.error_desc['group'] + "' multiple times."

        if w.code == GeneError.ATTRIBUTE_INVALID:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> have an invalid '" + w.error_desc['key'] + "' attribute value ('" + w.error_desc['value'] + "')"

        if w.code == GeneError.PART_SAME:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> and <a href=\"" + self.get_wa_url_other(w.error_desc['other_scaff'], w.error_desc['other_start'], w.error_desc['other_end']) + "\">" + w.error_desc['other_name'] + "</a> are marked as the same part of a gene. If they are the same part of different alleles, add 'Allele' tags to both."

        if w.code == GeneError.PART_SINGLE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if w.code == GeneError.PART_SINGLE_NAMED:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if w.code == GeneError.ALLELE_SAME:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> and <a href=\"" + self.get_wa_url_other(w.error_desc['other_scaff'], w.error_desc['other_start'], w.error_desc['other_end']) + "\">" + w.error_desc['other_name'] + "</a> are marked as the same allele of a duplicated gene. If they are different parts of the same allele, add 'Part' tags to both."

        if w.code == GeneError.ALLELE_SINGLE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is the only allele of a gene. If the gene has no other allele, you should remove the 'allele' tag. Otherwise, check that all alleles of the same gene have the same 'symbol'"

        if w.code == GeneError.INTRON_TOO_SMALL:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> contains very short introns. This is not supposed to happen on most genes, check that the gene structure is correct."

        if w.code == GeneError.NEEDS_REVIEW:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is not yet Approved. Change its status once you have finished working on it."

        if w.code == GeneError.PUTATIVE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> contains 'putative' in its name. Use this only if you have real doubts on the naming of this gene. If you have sufficient supporting evidences, just write the gene name without 'putative'."

        if w.code == GeneError.SIMILAR_TO:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> contains 'similar to' or '-like' in its name. Use 'putative' instead, and only if you have real doubts on the naming of this gene. If you have sufficient supporting evidences, just write the gene name without 'putative'."

        if w.code == GeneError.SYMBOL_NOT_ID:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> has an invalid symbol: don't use OGS ids like DV0000123-RA, they will be generated on OGS release."

        if w.code == GeneError.NAME_NOT_ID:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> has an invalid name: don't use OGS ids like DV0000123-RA, they will be generated on OGS release."

        if w.code == GeneError.SYMBOL_NOT_UNIQUE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> has a symbol which is not unique."

        if w.code == GeneError.NAME_NOT_UNIQUE:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> has a name which is not unique."

        if w.code == GeneError.DELETED_MISSING_NAME:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is marked as deleted but doesn't have a gene name."

        if w.code == GeneError.DELETED_WRONG_NAME:
            return "Gene <a href=\"" + self.get_wa_url(w) + "\">" + w.display_id + "</a> is marked as deleted but has a wrong gene name '" + w.error_desc['name'] + "'."

        return "Unexpected warning %s" % w.code

    def render_ok(self, g):

        return "Gene <a href=\"" + self.get_wa_url(g) + "\">" + g.display_id + "</a> is ok (in group '" + '\', \''.join(g.groups) + "')"

    def render_deleted(self, g):

        return "Gene <a href=\"" + self.get_wa_url(g) + "\">" + g.name + "</a> will be deleted"
