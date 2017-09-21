from wacheck.error.GeneError import GeneError
from wacheck.error.WAError import WAError

from wacheck.report.HtmlReport import HtmlReport

import os
from datetime import datetime

class UserHtmlReport(HtmlReport):

    def __init__(self, checker, ok, errors, warnings):

        HtmlReport.__init__(self, checker, ok, errors, warnings)


    def save_to_dir(self, report_dir):

        for u in self.user_names:
            user_report_path = os.path.normpath(report_dir) + os.sep + u + '.html'

            report = self.render(u)

            out_handle = open(user_report_path, "w")

            out_handle.write(report)

            out_handle.close()

            print "Wrote '"+u+"' report to "+user_report_path


    def render(self, u):

        res = """
        <html>
        <head>
        <meta charset="UTF-8">
        </head>
        <body>

        <h1>Manual annotation report</h1>"""

        res += "<p>This is an automatic report concerning the genes that you manually annotated.</p>"

        res += "<p>The aim of this report is to give you some feedback on the gene(s) you have annotated. It is updated every night, and the present report have been generated on: <b>"+str(datetime.now())+"</b> (Paris, France time).</p>"

        res += "<p>We have identified "+str(len(self.errors[u]))+" issues with the following genes (these genes will not be included in the next Official Gene Set until their issues are fixed):</p>\n\n"

        res += "<ul>"
        res += self.render_user_errors(u)
        res += "</ul>"

        res += "<p>We also found "+str(len(self.warnings[u]))+" warnings (potential issues) with the following genes (these genes will be included in the next Official Gene Set, but you should check them):</p>\n\n"

        res += "<ul>"
        res += self.render_user_warnings(u)
        res += "</ul>"

        res += """<p>We ask you kindly to fix these problems using the WebApollo server (just click on each link above, and don't forget to login).</p>
        <p>As this is an automatic validation, there may be some false positive in this issue list. If you think your gene is already properly annotated, leave it as it is. If you have any doubt, contact us (see below).</p>"""

        res += """<p>Briefly:</p>
        <ul>"""
        res += "<li>each gene should have an "+self.group_tags[0]+" attribute with the name of an annotation groups as written in the wiki.</li>"

        res += """<li>Each gene should have a 'Symbol' (short name without spaces and special characters), and a 'Name' (long human readable name).</li>
        <li>Heterozyous alleles should have an "Allele" tag with values "A", "B", "C", and so on. Every alleles of a same gene should have the same 'Symbol'.</li>
        <li>In case of genes spread on multiple scaffolds, each part should have a "Part" tag with values "1", "2", "3", and so on. Every part of a same gene should have the same 'Symbol'.</li>
        </ul>"""

        res += "<p>When the error comment \"is not in any group (add an "+self.group_tags[0]+" attribute)\" is found, it means that the annotator forgot to mention their annotation group when annotating their genes. In order to correct, please refer to the wiki, guidelines for annotation, manual curation process, register your gene. In case you do not find the right keyword in the current annotation group list, please let us know what keyword you suggest, we may add new groups names in the list.</p>"

        if self.ok and u in self.ok:
            res += "<p><p>For your information, you have already properly anotated the following "+str(len(self.ok[u]))+" genes:</p>\n\n"

            res += "<ul>"
            res += self.render_user_ok(u)
            res += "</ul>"
        else:
            res += "<p><p>For your information, none of the gene you annotated are currently properly anotated.\n\n"

        res += """
        </body>
        </html>
        """

        return res


    def render_user_errors(self, u):

        res = ""

        if len(self.errors[u]) == 0:
            res += "<li>No issues found</li>"
            res += "\n\n"

        else:
            for e in self.errors[u]:
                res += "<li>"+self.render_error(e)+"</li>\n"
            res += "\n\n"

        return res


    def render_user_warnings(self, u):

        res = ""

        if len(self.warnings[u]) == 0:
            res += "<li>No warnings found</li>"
            res += "\n\n"

        else:
            for e in self.warnings[u]:
                res += "<li>"+self.render_warning(e)+"</li>\n"
            res += "\n\n"

        return res


    def render_user_ok(self, u):

        res = ""

        if len(self.ok[u]) == 0:
            res += "<li>No valid gene found</li>"
            res += "\n\n"

        else:
            for e in self.ok[u]:
                res += "<li>"+self.render_ok(e)+"</li>\n"
            res += "\n\n"

        return res
