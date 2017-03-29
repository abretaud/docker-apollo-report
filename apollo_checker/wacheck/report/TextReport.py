from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError

from wacheck.report.Report import Report

class TextReport(Report):

    def render_wa_error(self, e):

        if e.code == WAError.UNEXPECTED_FEATURE:
            return "ERROR: unexpected feature of type '"+e.gene.f.type+"' (ID="+e.gene.wa_id+") located at "+self.get_wa_url(e.scaffold, e.start, e.end)

        if e.code == WAError.OUTSIDE_SCAFFOLD_START:
            return "ERROR: "+e.gene.wa_id+" start position "+str(e.start)+" is higher than the scaffold size "+str(e.gene.scaffold_size)

        if e.code == WAError.OUTSIDE_SCAFFOLD_END:
            return "ERROR: "+e.gene.wa_id+" end position "+str(e.end)+" is higher than the scaffold size "+str(e.gene.scaffold_size)

        if e.code == WAError.UNEXPECTED_SUB_FEATURE:
            return "ERROR: unexpected element '"+e.error_desc['child_id']+"' of type '"+e.error_desc['child_type']+"' for gene '"+e.gene.wa_id+"' located at "+self.get_wa_url(e.scaffold, e.start, e.end)

        if e.code == WAError.MULTIPLE_SUB_FEATURE:
            return "ERROR: multiple child element ("+str(e.error_desc['num_children'])+") for gene '"+e.gene.wa_id+"' located at "+self.get_wa_url(e.scaffold, e.start, e.end)


    def render_error(self, e):

        if e.code == GeneError.SYMBOL_MISSING:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is missing a 'symbol'."

        if e.code == GeneError.SYMBOL_INVALID:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" have an invalid 'symbol': '"+e.error_desc['symbol']+"'. Use only letters digits and -_.()/ characters."

        if e.code == GeneError.MULTIPLE_MRNAS:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" have "+str(e.error_desc['num'])+" transcripts. Check that they are real splice variants and not erroneous duplications."

        if e.code == GeneError.CDS_IS_NULL:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" CDS length is null (0). Check that the gene contains a start codon and that the exons are properly defined."

        if e.code == GeneError.CDS_IS_SMALL:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" CDS length is very small ("+str(e.error_desc['len'])+"). Check that the gene contains a start codon and that the exons are properly defined."

        if e.code == GeneError.NAME_MISSING:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is missing a 'Name'."

        if e.code == GeneError.NAME_INVALID:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" should have a human readable 'Name' instead of '"+e.error_desc['name']+"'."

        if e.code == GeneError.DBXREF_UNKNOWN:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" has an unknown dbxref type: '"+e.error_desc['dbxref']+"'."

        if e.code == GeneError.GROUP_MISPLACED:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" have "+e.error_desc['tag']+" as a gene DBXref instead of an attribute."

        if e.code == GeneError.GROUP_UNKNOWN:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is in an unknown "+self.group_tags[0]+" group '"+e.error_desc['group']+"' (check the spelling)."

        if e.code == GeneError.GROUP_NONE:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is not in any group (add an "+self.group_tags[0]+" attribute)."

        if e.code == GeneError.GROUP_MULTIPLE:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is in multiple annotations groups: '"+"', '".join(w.gene.groups)+"'."

        if e.code == GeneError.GROUP_MULTIPLE_SAME:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" has been added to the same annotation group '"+e.error_desc['group']+"' multiple times."

        if e.code == GeneError.ATTRIBUTE_INVALID:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" have an invalid '"+e.error_desc['key']+"' attribute value ('"+e.error_desc['value']+"')"

        if e.code == GeneError.PART_SAME:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" and "+e.error_desc['other_name']+" located at "+self.get_wa_url(e.error_desc['other_scaff'], e.error_desc['other_start'], e.error_desc['other_end'])+" are marked as the same part of a gene. If they are the same part of different alleles, add 'Allele' tags to both."

        if e.code == GeneError.PART_SINGLE:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if e.code == GeneError.PART_SINGLE_NAMED:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if e.code == GeneError.ALLELE_SAME:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" and "+e.error_desc['other_name']+" located at "+self.get_wa_url(e.error_desc['other_scaff'], e.error_desc['other_start'], e.error_desc['other_end'])+" are marked as the same allele of a duplicated gene. If they are different parts of the same allele, add 'Part' tags to both."

        if e.code == GeneError.ALLELE_SINGLE:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is the only allele of a gene. If the gene has no other allele, you should remove the 'allele' tag. Otherwise, check that all alleles of the same gene have the same 'symbol'"

        if e.code == GeneError.INTRON_TOO_SMALL:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" contains very short introns. This is not supposed to happen on most genes, check that the gene structure is correct."

        if e.code == GeneError.NEEDS_REVIEW:
            return "Gene "+e.display_id+" located at "+self.get_wa_url(e.scaffold, e.start, e.end)+" is not yet Approved. Change its status once you have finished working on it."

        return "Unexpected error %s" % e.code


    def render_warning(self, w):

        if w.code == GeneError.SYMBOL_MISSING:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is missing a 'symbol'."

        if w.code == GeneError.SYMBOL_INVALID:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" have an invalid 'symbol': '"+w.error_desc['symbol']+"'. Use only letters digits and -_.()/ characters."

        if w.code == GeneError.MULTIPLE_MRNAS:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" have "+str(w.error_desc['num'])+" transcripts. Check that they are real splice variants and not erroneous duplications."

        if w.code == GeneError.CDS_IS_NULL:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" CDS length is null (0). Check that the gene contains a start codon and that the exons are properly defined."

        if w.code == GeneError.CDS_IS_SMALL:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" CDS length is very small ("+str(w.error_desc['len'])+"). Check that the gene contains a start codon and that the exons are properly defined."

        if w.code == GeneError.NAME_MISSING:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is missing a 'Name'."

        if w.code == GeneError.NAME_INVALID:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" should have a human readable 'Name' instead of '"+e.error_desc['name']+"'."

        if w.code == GeneError.DBXREF_UNKNOWN:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" has an unknown dbxref type: '"+w.error_desc['dbxref']+"'."

        if w.code == GeneError.GROUP_MISPLACED:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" have "+w.error_desc['tag']+" as a gene DBXref instead of an attribute."

        if w.code == GeneError.GROUP_UNKNOWN:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is in an unknown "+self.group_tags[0]+" group '"+w.error_desc['group']+"' (check the spelling)."

        if w.code == GeneError.GROUP_NONE:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is not in any group (add an "+self.group_tags[0]+" attribute)."

        if w.code == GeneError.GROUP_MULTIPLE:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is in multiple annotations groups: '"+"', '".join(w.gene.groups)+"'."

        if w.code == GeneError.GROUP_MULTIPLE_SAME:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" has been added to the same annotation group '"+w.error_desc['group']+"' multiple times."

        if w.code == GeneError.ATTRIBUTE_INVALID:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" have an invalid '"+w.error_desc['key']+"' attribute value ('"+w.error_desc['value']+"')"

        if w.code == GeneError.PART_SAME:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" and "+w.error_desc['other_name']+" located at "+self.get_wa_url(w.error_desc['other_scaff'], w.error_desc['other_start'], w.error_desc['other_end'])+" are marked as the same part of a gene. If they are the same part of different alleles, add 'Allele' tags to both."

        if w.code == GeneError.PART_SINGLE:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if w.code == GeneError.PART_SINGLE_NAMED:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is the only part of a gene. If the gene is complete, you should remove the 'part' tag. Otherwise, check that all the parts of the gene have exactly the same 'symbol'. If the gene is incomplete, leave it like this."

        if w.code == GeneError.ALLELE_SAME:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" and "+w.error_desc['other_name']+" located at "+self.get_wa_url(w.error_desc['other_scaff'], w.error_desc['other_start'], w.error_desc['other_end'])+" are marked as the same allele of a duplicated gene. If they are different parts of the same allele, add 'Part' tags to both."

        if w.code == GeneError.ALLELE_SINGLE:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is the only allele of a gene. If the gene has no other allele, you should remove the 'allele' tag. Otherwise, check that all alleles of the same gene have the same 'symbol'"

        if w.code == GeneError.INTRON_TOO_SMALL:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" contains very short introns. This is not supposed to happen on most genes, check that the gene structure is correct."

        if w.code == GeneError.NEEDS_REVIEW:
            return "Gene "+w.display_id+" located at "+self.get_wa_url(w.scaffold, w.start, w.end)+" is not yet Approved. Change its status once you have finished working on it."

        return "Unexpected warning %s" % w.code


    def render_ok(self, g):

        return "Gene "+g.display_id+" located at "+self.get_wa_url(g.scaffold, g.f.location.start, g.f.location.end)+" is ok (in group '"+'\', \''.join(g.groups)+"')"
