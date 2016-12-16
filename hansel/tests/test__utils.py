# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import pytest

import os.path as op
import tempfile
from   collections import Iterable, Sized
from   itertools import chain, product

from hansel._utils import (_yield_items,
                           _enum_items,
                           _depth_items,
                           _arg_names,
                           _depth_names,
                           _depth_names_regexes,
                           _build_path,
                           is_valid,
                           _first_txt,
                           _find_arg_depth,
                           _has_arg,
                           _check,
                           _get_path,
                           _is_crumb_arg,
                           _format_arg,
                           has_crumbs,
                           _split,
                           _makedirs,
                           _make_new_dirs,
                           _touch,
                           _split_exists,
                           _check_is_subset,
                          )


def test__yield_items():
    #for (literal_text, field_name, format_spec, conversion) in fmt.parse(crumb_path):
    # (txt, fld, fmt, conv)
    assert [('/data/', 'crumb', '', None), ('/file/', 'img', '', None)] == \
           list(_yield_items("/data/{crumb}/file/{img}"))

    assert [('/data/crumb/file/img', None, None, None)] == \
           list(_yield_items('/data/crumb/file/img'))
