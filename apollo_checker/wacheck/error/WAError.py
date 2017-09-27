class WAError:

    # Error codes
    UNEXPECTED_FEATURE = 1
    OUTSIDE_SCAFFOLD_START = 2
    OUTSIDE_SCAFFOLD_END = 3
    UNEXPECTED_SUB_FEATURE = 4
    MULTIPLE_SUB_FEATURE = 5
    WRONG_GENE_START = 6
    WRONG_GENE_END = 7
    WRONG_GENE_STRAND = 8

    def __init__(self, code, gene, error_desc = {}):

        self.code = code # The error code of the current error (see constants)
        self.gene = gene
        self.wa_id = gene.wa_id
        self.display_id = gene.display_id
        self.scaffold = gene.scaffold
        self.start = gene.f.location.start
        self.end = gene.f.location.end
        self.strand = gene.f.location.strand
        self.error_desc = error_desc
