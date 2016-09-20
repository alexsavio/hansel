#!python
import click

from .utils import (CONTEXT_SETTINGS,
                    CrumbPath,
                    echo_list,
                    check_not_none,)


# declare the CLI group
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('crumb', type=CrumbPath(), callback=check_not_none)
@click.option('-i', '--ignore', type=str, multiple=True,
              help='A global ignore fnmatch expression for the listing. '
                   'You can add as many of this argument as you want. '
                   'Example: ".*" or "*~"')
@click.option('-a', '--arg', type=str,
              help='Name of the argument in `crumb` to print the values from.'
                   'Will not print full paths, but only values for this '
                   'crumb argument.')
def ls(crumb, ignore, arg):
    """Uses hansel.Crumb to list all the possible values that match the
    given crumb path.

    Examples: \n
    crumb ls "/data/hansel/cobre/{sid:4*100}/{session}/{img}"\n
    crumb ls -i ".*" "/data/hansel/cobre/{sid}/{session}/{img:anat*}"\n
    crumb ls -a "sid" "/data/hansel/cobre/{sid}/{session}/{img:anat*}"\n
    """
    crumb._ignore = ignore
    if arg:
        echo_list(crumb[arg])
    else:
        echo_list(crumb.ls())


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('src_crumb', type=CrumbPath(), callback=check_not_none)
@click.argument('dst_crumb', type=CrumbPath(), callback=check_not_none)
@click.option('-l', '--link', is_flag=True, flag_value=True,
              help='Flag to indicate to whether make links instead of copying.')
@click.option('-q', '--quiet', is_flag=True, flag_value=True,
              help='Flag to remove verbose.')
@click.option('-e', '--exist_ok', is_flag=True, flag_value=True,
              help='Flag to allow overwriting destination path.')
@click.option('-i', '--ignore', type=str, multiple=True,
              help='A global ignore fnmatch expression for the listing. '
                   'You can add as many of this argument as you want. '
                   'Example: ".*" or "*~"')
def copy(src_crumb, dst_crumb, link, quiet, ignore, exist_ok):
    """Uses hansel.Crumb to copy one file tree to another file tree. The
    structure of the destination tree can be modified.

    Examples: \n
    crumb copy --link "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}" \n
    crumb copy "cobre/{sid}/{session}/{img:anat*}" "cobre_anat/{sid}/{img}" \n
    """
    from .. import crumb_copy

    if ignore:
        src_crumb._ignore = ignore
        dst_crumb._ignore = ignore

    crumb_copy(src_crumb, dst_crumb,
               make_links=link,
               exist_ok=exist_ok,
               verbose=(not quiet))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('crumb1', type=CrumbPath(), callback=check_not_none)
@click.argument('crumb2', type=CrumbPath(), callback=check_not_none)
@click.option('-o', '--on', type=str, multiple=True,
              help='Argument name to check for intersection. You can use this '
                   'argument more than once.')
@click.option('-a', '--arg', type=str,
              help='Will not print full paths, but only values for this '
                   'crumb argument.')
def intersect(crumb1, crumb2, on, arg):
    """Uses hansel.Crumb to copy one file tree to another file tree. The
    structure of the destination tree can be modified.

    Examples: \n
    crumb intersect --on "sid" "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"\n
    """
    from .. import intersection

    intersects = intersection(crumb1, crumb2, on=on)
    for values in intersects:
        click.echo(', '.join([arg[1] for arg in values]))
