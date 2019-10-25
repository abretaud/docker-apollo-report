class Report:

    def __init__(self, checker, ok, errors, warnings):

        self.wa_url = checker.wa_url
        self.group_tags = checker.group_tags

        self.user_names = checker.names
        self.wa_errors = checker.wa_errors
        self.groups = checker.groups_stats
        self.genes_with_goid = checker.genes_with_goid
        self.genes_seen_once = checker.genes_seen_once
        self.splitted_genes = checker.splitted_genes
        self.duplicated_genes = checker.duplicated_genes

        self.ok = ok
        self.errors = errors
        self.warnings = warnings
        self.genes_by_users = checker.genes_by_users()
        self.genes_by_groups = checker.genes_by_groups()

        self.count_total_errors()
        self.count_total_warnings()
        self.count_total_ok()
        self.count_total_deleted()
        self.count_total_genes()

    def get_wa_url(self, gene):

        if hasattr(gene, "start"):
            start = gene.start
            end = gene.end
        else:
            start = gene.f.location.start
            end = gene.f.location.end

        return "%sannotator/loadLink?loc=%s%3A%s..%s" % (self.wa_url, gene.scaffold, start, end)

    def count_total_errors(self):

        self.total_errors = 0

        for ue in self.errors.values():
            self.total_errors += len(ue)

    def count_total_warnings(self):

        self.total_warnings = 0

        for uw in self.warnings.values():
            self.total_warnings += len(uw)

    def count_total_ok(self):

        self.total_ok = 0

        for ou in self.ok.values():
            self.total_ok += len(ou)

    def count_total_deleted(self):

        self.total_deleted = 0

        for ou in self.ok.values():
            self.total_deleted += len([g for g in ou if g.is_deleted])

    def count_total_genes(self):

        self.total_genes = 0

        for g in self.genes_by_users.values():
            self.total_genes += len(g)

    def render_wa_error(self, e):
        raise NotImplementedError("Please, implement this method")

    def render_error(self, e):
        raise NotImplementedError("Please, implement this method")

    def render_warning(self, w):
        raise NotImplementedError("Please, implement this method")

    def render_ok(self, g):

        return "Gene " + g.display_id + " located at " + self.get_wa_url(g) + " is ok (in group '" + '\', \''.join(g.groups) + "')"

    def render(self):
        raise NotImplementedError("Please, implement this method")
