class GeneError:
    # Error codes
    SYMBOL_MISSING = 1
    SYMBOL_INVALID = 2
    MULTIPLE_MRNAS = 3
    CDS_IS_NULL = 4
    CDS_IS_SMALL = 5
    NAME_MISSING = 6
    NAME_INVALID = 7
    DBXREF_UNKNOWN = 8
    GROUP_MISPLACED = 9
    GROUP_UNKNOWN = 10
    GROUP_NONE = 11
    GROUP_MULTIPLE = 12
    GROUP_MULTIPLE_SAME = 13
    ATTRIBUTE_INVALID = 14
    PART_SAME = 15
    PART_SINGLE = 16
    PART_SINGLE_NAMED = 17
    ALLELE_SAME = 18
    ALLELE_SINGLE = 19
    INTRON_TOO_SMALL = 20
    NEEDS_REVIEW = 21
    INVALID_MRNA_NAME = 22
    SIMILAR_TO = 23
    PUTATIVE = 24
    SYMBOL_NOT_ID = 25
    NAME_NOT_ID = 26
    SYMBOL_NOT_UNIQUE = 27
    NAME_NOT_UNIQUE = 28
    DELETED_MISSING_NAME = 29
    DELETED_WRONG_NAME = 30

    def __init__(self, code, gene, error_desc = {}):

        self.code = code # The error code of the current error (see constants)
        self.gene = gene
        self.wa_id = gene.wa_id # The webapollo id of the gene
        self.display_id = gene.display_id # The name of the gene to display (can be symbol or wa_id)
        self.scaffold = gene.scaffold # The scaffold where the gene is
        self.start = gene.f.location.start # Start position on the scaffold
        self.end = gene.f.location.end # End position on the scaffold
        self.error_desc = error_desc # A dict containing other informations on the error
