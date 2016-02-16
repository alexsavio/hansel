# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import pytest

import pandas as pd

from hansel.pandas import pandas_fill_crumbs
from hansel.utils  import valuesmap_to_dict

from test_utils import tmp_tree


def test_values_map_from_df(tmp_tree):
    tmp_crumb = tmp_tree[0]

    recs = tmp_crumb.values_map('image')

    adict = valuesmap_to_dict(recs)

    df1 = pd.DataFrame.from_records([dict(rec) for rec in recs])
    df2 = pd.DataFrame.from_dict(adict)
    assert all(df1 == df2)

    assert all(pd.DataFrame.from_dict   ([dict(rec) for rec in recs]) ==
               pd.DataFrame.from_records([dict(rec) for rec in recs]))


def test_pandas_fill_crumbs(tmp_tree):

    tmp_crumb = tmp_tree[0]

    recs = tmp_crumb.values_map('image')
    df = pd.DataFrame.from_dict(valuesmap_to_dict(recs))

    df_crumbs = list(pandas_fill_crumbs(df, tmp_crumb))
    uf_crumbs = tmp_crumb.unfold()

    assert set(df_crumbs) == set(uf_crumbs)
