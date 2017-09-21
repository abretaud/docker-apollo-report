import re
import string

from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError

class Gene:

    def __init__(self, f, scaffold, scaffold_size, allowed_groups, group_tags, apollo_1x = False, no_group = False, split_users = False):
        self.f = f
        self.scaffold = scaffold
        self.scaffold_size = scaffold_size
        self.wa_id = f.qualifiers['ID'][0]
        self.display_id = self.wa_id

        self.symbol = None
        self.name = None

        # Remove the @something suffix from owner names
        if split_users:
            self.owner = re.sub(r"^(.+)@[a-zA-Z0-9]+$", r"\1", self.get_tag_value('owner'))
        else:
            self.owner = self.get_tag_value('owner')

        self.allowed_groups = allowed_groups
        self.group_tags = group_tags

        self.apollo_1x = apollo_1x
        self.no_group = no_group

        self.has_goid = False
        self.groups = []

        self.errors = []
        self.warnings = []
        self.wa_errors = []

        self.is_deleted = False
        if (not self.apollo_1x) and 'status' in self.f.qualifiers and self.f.qualifiers['status'] and self.f.qualifiers['status'][0].lower() == "deleted":
            self.is_deleted = True

        if not self.is_deleted:
            self.check_feature_limits()
            self.check_sub_features_mrna()

            self.check_symbol()
            self.check_sub_features()
            self.check_cds()
            self.check_intron()
            self.check_name()
            self.check_groups()
            self.check_dbxref()

            self.check_status()
        else:
            self.check_deleted_name()

        allowed_parts = [str(x) for x in range(1,30)]
        self.part = self.get_tag_value('Part', allowed_parts) # Must be an integer
        self.allele = self.get_tag_value('Allele', list(string.ascii_uppercase)) # Must be an uppercase letter


    def get_tag_value(self, key, allowed = []):
        for qk in self.f.qualifiers.keys():
            if key.lower() == qk.strip().lower():
                new_value = self.f.qualifiers[qk][0].strip()
                if len(allowed) > 0 and new_value not in allowed:
                    self.errors.append(GeneError(GeneError.ATTRIBUTE_INVALID, self, {'key': key, 'value': new_value}))

                return new_value

        return None


    def check_feature_limits(self):

        if self.f.location.start > self.scaffold_size:
            self.wa_errors.append(WAError(WAError.OUTSIDE_SCAFFOLD_START, self))
        if self.f.location.end > self.scaffold_size:
            self.wa_errors.append(WAError(WAError.OUTSIDE_SCAFFOLD_END, self))


    def check_sub_features_mrna(self):

        for child in self.f.sub_features:
            if child.type != "mRNA":
                self.wa_errors.append(WAError(WAError.UNEXPECTED_SUB_FEATURE, self, {'child_id': child.qualifiers['ID'][0], 'child_type': child.type}))


    def check_symbol(self):

        if 'symbol' not in self.f.qualifiers or self.f.qualifiers['symbol'][0] == "" or self.f.qualifiers['symbol'][0] == "true":
            self.errors.append(GeneError(GeneError.SYMBOL_MISSING, self))
        else:
            symbol = self.f.qualifiers['symbol'][0].strip()
            self.display_id = symbol
            if not re.match("^[A-Za-z0-9-_.()/]+$", symbol) :
                self.errors.append(GeneError(GeneError.SYMBOL_INVALID, self, {'symbol': symbol}))

            elif re.match("^[A-Z]{2,3}[0-9]{5,8}-R[A-Z]$", symbol) :
                self.errors.append(GeneError(GeneError.SYMBOL_NOT_ID, self, {'symbol': symbol}))

            else:
                self.symbol = self.f.qualifiers['symbol'][0].strip()


    def check_sub_features(self):

        if len(self.f.sub_features) > 1:
            foundOverlap = False
            for sub1 in self.f.sub_features:
                firstChild = sub1
                start1 = firstChild.location.start
                end1 = firstChild.location.end
                for sub2 in sub1.sub_features:
                    if (sub1.qualifiers['ID'][0] != sub2.qualifiers['ID'][0]):
                        start2 = sub2.location.start
                        end2 = sub2.location.end
                        if ((start2 >= start1 and start2 <= end1) or (end2 >= start1 and end2 <= end1) or (start1 >= start2 and start1 <= end2) or (end1 >= start2 and end1 <= end2)):
                            foundOverlap = True
            if not foundOverlap:
                self.wa_errors.append(WAError(WAError.MULTIPLE_SUB_FEATURE, self, {'num_children': len(self.f.sub_features)}))
            else:
                self.check_multiple_mrnas()

    def check_multiple_mrnas(self):

        if len(self.f.sub_features) > 1:
            gene_name = self.f.qualifiers['ID'][0]
            for child in self.f.sub_features:
                if child.type == "mRNA":
                    if len(child.qualifiers['ID'][0]) < len(gene_name) or not child.qualifiers['ID'][0].startswith(gene_name) or re.match("^ [A-F]{1,2}$", child.qualifiers['ID'][0][len(gene_name):]):
                        self.errors.append(GeneError(GeneError.INVALID_MRNA_NAME, self, {'gene_name': gene_name}))


    def check_intron(self):

        if len(self.f.sub_features) > 0:
            exon_coords = {}

            # Find positions
            for mrna in self.f.sub_features:
                for gchild in mrna.sub_features:
                    if gchild.type == "exon":
                        exon_coords[gchild.location.start] = gchild.location.end

            # Check minimum intron size
            start_sorted = sorted(exon_coords)
            previous_end = None
            for exon_start in start_sorted:
                if previous_end != None:
                    intron_size = exon_start - previous_end
                    if intron_size < 9:
                        self.warnings.append(GeneError(GeneError.INTRON_TOO_SMALL, self, {'len': intron_size, 'start': exon_start, 'end': previous_end}))

                previous_end = exon_coords[exon_start]

    def check_cds(self):

        # Check the total length of CDS
        if len(self.f.sub_features) > 0:
            cdsLen = 0
            for sub1 in self.f.sub_features:
                for sub2 in sub1.sub_features:
                    if sub2.type == 'CDS':
                        start = sub2.location.start
                        end = sub2.location.end
                        if end > start:
                            cdsLen += end - start
                        else:
                            cdsLen += start - end
            if cdsLen == 0:
                self.errors.append(GeneError(GeneError.CDS_IS_NULL, self))
            if cdsLen < 20:
                self.warnings.append(GeneError(GeneError.CDS_IS_SMALL, self, {'len': cdsLen}))


    def check_name(self):

        if 'Name' not in self.f.qualifiers or self.f.qualifiers['Name'][0] == "" or self.f.qualifiers['Name'][0] == "true":
                self.errors.append(GeneError(GeneError.NAME_MISSING, self))
        else:
            name = self.f.qualifiers['Name'][0].strip()
            if len(name) == 32 and re.match("^[A-F0-9]+$", name):
                self.errors.append(GeneError(GeneError.NAME_INVALID, self, {'name': name}))

            elif 'putative' in name.lower():
                self.warnings.append(GeneError(GeneError.PUTATIVE, self, {'name': name}))
            elif 'similar to' in name.lower():
                self.errors.append(GeneError(GeneError.SIMILAR_TO, self, {'name': name}))
            elif '-like' in name.lower():
                self.warnings.append(GeneError(GeneError.SIMILAR_TO, self, {'name': name}))

            elif re.match("^[A-Z]{2,3}[0-9]{5,8}-R[A-Z]$", name):
                self.errors.append(GeneError(GeneError.NAME_NOT_ID, self, {'name': name}))

            else:
                self.name = self.f.qualifiers['Name'][0].strip()


    def check_deleted_name(self):

        if 'Name' not in self.f.qualifiers or self.f.qualifiers['Name'][0] == "" or self.f.qualifiers['Name'][0] == "true":
            self.errors.append(GeneError(GeneError.DELETED_MISSING_NAME, self))
        else:
            self.name = self.f.qualifiers['Name'][0].strip()
            if not re.match("^[A-Z]{2,3}[0-9]{5,8}-R[A-Z]$", self.name):
                self.errors.append(GeneError(GeneError.DELETED_WRONG_NAME, self, {'name': self.name}))


    def check_group(self, group):

        for ag in self.allowed_groups:
            if group.strip().lower() == ag.strip().lower():
                return ag
        return group


    def check_groups(self):

        for tag in self.group_tags:

            # In gff, the attribute will have a lowercase first letter
            gff_tag = tag[0].lower() + tag[1:]

            if gff_tag in self.f.qualifiers:
                for group in self.f.qualifiers[gff_tag]:

                    group = self.check_group(group)

                    if group != "":
                        if group not in self.groups:
                            self.groups.append(group)
                        else:
                            self.warnings.append(GeneError(GeneError.GROUP_MULTIPLE_SAME, self, {'group': group}))

                        if group not in self.allowed_groups:
                            self.errors.append(GeneError(GeneError.GROUP_UNKNOWN, self, {'group': group}))
                    else:
                        self.errors.append(GeneError(GeneError.GROUP_UNKNOWN, self, {'group': group}))

        if len(self.groups) == 0:
            self.groups.append('Unknown')
            if not self.no_group:
                self.errors.append(GeneError(GeneError.GROUP_NONE, self))
        elif len(self.groups) > 1:
            self.warnings.append(GeneError(GeneError.GROUP_MULTIPLE, self))

    def check_dbxref(self):

        if 'Dbxref' in self.f.qualifiers:
            for dbxref in self.f.qualifiers['Dbxref']:
                splitted_dbxref = dbxref.split(":")
                db = splitted_dbxref[0].strip()
                xref=":".join(splitted_dbxref[1:]).strip()

                for t in self.group_tags:
                    if t.lower() == db.lower():
                        self.errors.append(GeneError(GeneError.GROUP_MISPLACED, self, {'tag': t}))

                if db.lower() not in ['go', 'pmid', 'ncbi', 'uniprot']:
                    self.warnings.append(GeneError(GeneError.DBXREF_UNKNOWN, self, {'dbxref': dbxref}))

                if dbxref.startswith('GO'):
                    self.has_goid = True

    def check_status(self):

        if (not self.apollo_1x) and ('status' not in self.f.qualifiers or (self.f.qualifiers['status'][0].lower() == "needs review")):
            self.errors.append(GeneError(GeneError.NEEDS_REVIEW, self))
