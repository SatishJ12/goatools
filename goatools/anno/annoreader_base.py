"""Read an Association File and store the data in a Python object."""

import sys
import timeit
import datetime
from datetime import date
# import os
# import re
import collections as cx
from goatools.evidence_codes import EvidenceCodes
from goatools.anno.opts import AnnoOptions

__copyright__ = "Copyright (C) 2016-2019, DV Klopfenstein, H Tang. All rights reserved."
__author__ = "DV Klopfenstein"


# pylint: disable=broad-except,too-few-public-methods,line-too-long
class AnnoReaderBase(object):
    """Reads a Gene Association File. Returns a Python object."""

    tic = timeit.default_timer()

    # Expected values for a Qualifier
    exp_qualifiers = set([
        # Seen in both GAF and gene2go
        'not', 'contributes_to', 'colocalizes_with',
        # Seen in gene2go
        # TBD: resolve gaf(not|contributes_to) v gene2go(contributes_to)
        #'not contributes_to', 'not colocalizes_with',
        #
        # Although thee go not appear in:
        #     http://geneontology.org/page/go-annotation-conventions#qual
        # they do appear in more than one July 2018 GAFs:
        #     'enables', 'involved_in', 'part_of',
    ])

    def __init__(self, name, filename=None, **kws):
        # kws: allow_missing_symbol
        self.name = name
        self.filename = filename
        self.evobj = EvidenceCodes()
        # Read anotation file, store namedtuples:
        #     Gene2GoReader(filename=None, taxids=None):
        #     GafReader(filename=None, hdr_only=False, prt=sys.stdout, allow_missing_symbol=False):
        #     GpadReader(filename=None, hdr_only=False):
        self.hdr = None
        self.datobj = None
        # pylint: disable=no-member
        self.associations = self._init_associations(filename, **kws)
        # assert self.associations, 'NO ANNOTATIONS FOUND: {ANNO}'.format(ANNO=filename)

    def get_name(self):
        """Return type of annotation"""
        return self.name

    def get_taxid(self):
        """Return taxid, if one was provided, otherwise return -1"""
        return -1

    def get_population(self):
        """Get population IDs (all DB_IDs)"""
        return self._get_population(self.associations)

    def get_ids_g_goids(self, goids):
        """Get database IDs (DB_IDs), given a set of GO IDs."""
        return set(nt.DB_ID for nt in self.associations if nt.GO_ID in goids)

    @staticmethod
    def _get_population(associations):
        """Get all IDs in the associations"""
        return set(nt.DB_ID for nt in associations)

    def get_id2gos(self, **kws):
        """Get associations in dict, id2gos"""
        options = AnnoOptions(**kws)
        return self._get_annotations_dct(self.associations, options)

    def prt_qualifiers(self, prt=sys.stdout):
        """Print Qualifiers: 1,462 colocalizes_with; 1,454 contributes_to; 1,157 not"""
        # 13 not colocalizes_with   (TBD: CHK - Seen in gene2go, but not gafs)
        #  4 not contributes_to     (TBD: CHK - Seen in gene2go, but not gafs)
        self._prt_qualifiers(self.associations, prt)

    @staticmethod
    def _prt_qualifiers(associations, prt=sys.stdout):
        """Print Qualifiers found in the annotations.
           QUALIFIERS:
                1,462 colocalizes_with
                1,454 contributes_to
                1,157 not
                   13 not colocalizes_with   (TBD: CHK - Seen in gene2go, but not gafs)
                    4 not contributes_to     (TBD: CHK - Seen in gene2go, but not gafs)
        """
        prt.write('QUALIFIERS:\n')
        for fld, cnt in cx.Counter(q for nt in associations for q in nt.Qualifier).most_common():
            prt.write('    {N:6,} {FLD}\n'.format(N=cnt, FLD=fld))

    @staticmethod
    def _get_annotations_dct(associations, options):
        """Return gene2go data for user-specified taxids."""
        # Simple associations
        id2gos = cx.defaultdict(set)
        b_geneid2gos = options.b_geneid2gos
        keep = options.keep
        for ntd in associations:
            # NOT: Used when gene is expected to have function F, but does NOT.
            # ND : GO function not seen after exhaustive annotation attempts to the gene.
            # if 'not' not in set(ntd.Qualifier) and ntd.Evidence_Code != 'ND':
            if keep(ntd.Qualifier, ntd.Evidence_Code):
                if b_geneid2gos:
                    id2gos[ntd.DB_ID].add(ntd.GO_ID)
                else:
                    id2gos[ntd.GO_ID].add(ntd.DB_ID)
        return dict(id2gos)

    @staticmethod
    def get_date_yyyymmdd(yyyymmdd):
        """Return datetime.date given string."""
        return date(int(yyyymmdd[:4]), int(yyyymmdd[4:6], base=10), int(yyyymmdd[6:], base=10))

    def hms(self, msg, tic=None, prt=sys.stdout):
        """Print elapsed time and message."""
        if tic is None:
            tic = self.tic
        hms = str(datetime.timedelta(seconds=(timeit.default_timer()-tic)))
        prt.write('{HMS}: {MSG}\n'.format(HMS=hms, MSG=msg))

    def chk_associations(self, fout_err=None):
        """Check that associations are in expected format."""
        pass


# Copyright (C) 2016-2019, DV Klopfenstein, H Tang. All rights reserved."