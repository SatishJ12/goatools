"""Show two methods to write the same data into: xlsx file, tsv file, and text file."""

import sys

from goatools.test_data.genes_NCBI_10090_ProteinCoding import GeneID2nt as GeneID2nt_mus
from test_nbt3102 import get_geneid2symbol, get_goeaobj
from goatools.wr_tbl import get_fmtflds, wr_xlsx, wr_tsv, prt_txt, _set_xlsx_colwidths
import filecmp


def test_wr_methods(log=sys.stdout):
    """Demonstrate printing a subset of all available fields using two methods."""
    # 1. Gene Ontology Enrichment Analysis
    #    1a. Initialize: Load ontologies, associations, and population gene IDs
    taxid = 10090 # Mouse study
    geneids_pop = GeneID2nt_mus.keys() # Mouse protein-coding genes
    goeaobj = get_goeaobj("fdr_bh", geneids_pop, taxid)
    #    1b. Run GOEA
    geneids_study = get_geneid2symbol("nbt.3102-S4_GeneIDs.xlsx")
    keep_if = lambda nt: getattr(nt, "p_fdr_bh") < 0.05 # keep if results are significant
    goea_results = goeaobj.run_study(geneids_study, keep_if=keep_if)
    # 2. Write results
    #    Write parameters:
    #    The format_string names below are the same names as in the namedtuple field_names.
    prtfmt = "{GO} {NS} {level:>2} {depth:>2} {p_fdr_bh:5.2e} {study_count:>5} {name}\n"
    wr_params = {
      # Format for printing in text format
      'prtfmt' : prtfmt, 
      # Format for p-values in tsv and xlsx format
      'fld2fmt' : {'p_fdr_bh' : '{:8.2e}'}, 
      # Print a subset namedtuple fields, don't print all fields in namedtuple.
      'prt_flds' : get_fmtflds(prtfmt) 
    }
    #    2a. Use the write functions inside the GOEnrichmentStudy class.
    _wr_3fmt_goeaobj(goea_results, goeaobj, wr_params, log)
    #    2b. Use the write functions straight from the wr_tbl package to print a list of namedtuples.
    _wr_3fmt_wrtbl(goea_results, wr_params, log)
    assert filecmp.cmp('nbt3102_subset_obj.tsv', 'nbt3102_subset_nt.tsv')



def _wr_3fmt_goeaobj(goea_results, goeaobj, wr_params, log):
    """Using GOEnrichmentStudy object, demonstrate printing a subset of GOEA fields."""
    # List of all fields, printable or not, available from GOEnrichmentRecord
    log.write("\nGOEnrichmentRecord FIELDS: {F}\n".format(F=" ".join(goea_results[0].get_prtflds_all())))
    # Use the subset of namedtuple fields_names that are listed in the format string:
    # Same format: print to screen and print to file:
    goeaobj.prt_txt(log, goea_results, **wr_params) # Print to screen
    goeaobj.wr_txt("nbt3102_subset_obj.txt", goea_results, **wr_params)
    # Print to Excel Spreadsheet
    title="Print subset of fields from GOEnrichmentRecord"
    goeaobj.wr_xlsx("nbt3102_subset_obj.xlsx", goea_results, title=title, **wr_params)
    # Print to tab-separated file
    goeaobj.wr_tsv("nbt3102_subset_obj.tsv", goea_results, **wr_params)


def _wr_3fmt_wrtbl(goea_results, wr_params, log):
    """Using functions in the wr_tbl pkg, demonstrate printing a subset of namedtuple fields."""
    from goatools.go_enrichment import get_nts
    goea_nts = get_nts(goea_results)
    # List of all fields, printable or not, in namedtuple (nt):
    log.write("\nnamedtuple FIELDS: {F}\n".format(F=" ".join(goea_nts[0]._fields)))
    # Print to Excel Spreadsheet
    title="Print subset of namedtuple fields"
    wr_xlsx("nbt3102_subset_nt.xlsx", goea_nts, title=title, **wr_params)
    # Print to tab-separated file
    wr_tsv("nbt3102_subset_nt.tsv", goea_nts, **wr_params)


if __name__ == '__main__':
    test_wr_methods(sys.stdout)
