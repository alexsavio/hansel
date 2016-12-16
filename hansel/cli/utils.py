# -*- coding: utf-8 -*-
"""
Utilities for the CLI functions.
"""
from __future__ import print_function, division, unicode_literals, absolute_import

import os.path as path
import re

import click

from .. import Crumb


# different context options
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
UNKNOWN_OPTIONS = dict(allow_extra_args=True,
                       ignore_unknown_options=True)


# specification of existing ParamTypes
ExistingDirPath  = click.Path(exists=True, file_okay=False, resolve_path=True)
ExistingFilePath = click.Path(exists=True,  dir_okay=False, resolve_path=True)
UnexistingFilePath = click.Path(dir_okay=False, resolve_path=True)


# validators
def check_not_none(ctx, param, value):
    if value is None:
        raise click.BadParameter('got {}.'.format(value))
    return value


# declare custom click.ParamType
class RegularExpression(click.ParamType):
    name = 'regex'

    def convert(self, value, param, ctx):
        try:
            rex = re.compile(value, re.IGNORECASE)
        except ValueError:
            self.fail('%s is not a valid regular expression.' % value, param, ctx)
        else:
            return rex


class CrumbPath(click.ParamType):
    name = 'crumb'

    def convert(self, value, param, ctx):
        try:
            cr = Crumb(path.expanduser(value), ignore_list=['.*'])
        except ValueError:
            self.fail('%s is not a valid crumb path.' % value, param, ctx)
        else:
            return cr

# other utilities
def echo_list(alist):
    for i in alist:
        click.echo(i)


def _print_values_map_as_csv(list_of_lists):
    for values in list_of_lists:
        click.echo(','.join([item[1] for item in values]))
