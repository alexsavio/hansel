#!python
import click

from .utils import (CONTEXT_SETTINGS,
                    CrumbPath,
                    echo_list,
                    _print_values_map_as_csv,
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
    """List all the possible values that match the given crumb path.

    Examples: \n
    crumb ls "/data/hansel/cobre/{sid:4*100}/{session}/{img}"\n
    crumb ls -i ".*" "/data/hansel/cobre/{sid}/{session}/{img:anat*}"\n
    crumb ls -a "sid" "/data/hansel/cobre/{sid}/{session}/{img:anat*}"\n
    """
    if not crumb.isabs():
        crumb = crumb.abspath()

    crumb._ignore = ignore
    if arg:
        lst = crumb[arg]
    else:
        lst = crumb.ls()

    if not lst:
        exit(-1)

    echo_list(lst)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('src_crumb', type=CrumbPath(), callback=check_not_none)
@click.argument('dst_crumb', type=CrumbPath(), callback=check_not_none)
@click.option('-q', '--quiet', is_flag=True, flag_value=True,
              help='Flag to remove verbose.')
@click.option('-e', '--exist_ok', is_flag=True, flag_value=True,
              help='Flag to allow overwriting destination path.')
@click.option('-i', '--ignore', type=str, multiple=True,
              help='A global ignore fnmatch expression for the listing. '
                   'You can add as many of this argument as you want. '
                   'Example: ".*" or "*~"')
def copy(src_crumb, dst_crumb, quiet, ignore, exist_ok):
    """Copy one file tree to another file tree. The
    structure of the destination tree can be modified.

    Examples: \n
    crumb copy "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}" \n
    crumb copy "cobre/{sid}/{session}/{img:anat*}" "cobre_anat/{sid}/{img}" \n
    """
    from .. import crumb_copy

    if ignore:
        src_crumb._ignore = ignore
        dst_crumb._ignore = ignore

    if not src_crumb.ls():
        click.echo('Could not find any file that matched {}.'.format(src_crumb))
        exit(-1)

    crumb_copy(src_crumb, dst_crumb,
               exist_ok=exist_ok,
               verbose=(not quiet))



@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('src_crumb', type=CrumbPath(), callback=check_not_none)
@click.argument('dst_crumb', type=CrumbPath(), callback=check_not_none)
@click.option('-q', '--quiet', is_flag=True, flag_value=True,
              help='Flag to remove verbose.')
@click.option('-e', '--exist_ok', is_flag=True, flag_value=True,
              help='Flag to allow overwriting destination path.')
@click.option('-i', '--ignore', type=str, multiple=True,
              help='A global ignore fnmatch expression for the listing. '
                   'You can add as many of this argument as you want. '
                   'Example: ".*" or "*~"')
def link(src_crumb, dst_crumb, quiet, ignore, exist_ok):
    """Link one file tree to another file tree. The
    structure of the destination tree can be modified.
    Only the leaf nodes will be linked, the folder structure above will be
    created.

    Examples: \n
    crumb link "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}" \n
    crumb link "cobre/{sid}/{session}/{img:anat*}" "cobre_anat/{sid}/{img}" \n
    """
    from .. import crumb_link

    if ignore:
        src_crumb._ignore = ignore
        dst_crumb._ignore = ignore

    if not src_crumb.ls():
        click.echo('Could not find any file that matched {}.'.format(src_crumb))
        exit(-1)

    crumb_link(src_crumb, dst_crumb,
               exist_ok=exist_ok,
               verbose=(not quiet))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('crumb1', type=CrumbPath(), callback=check_not_none)
@click.argument('crumb2', type=CrumbPath(), callback=check_not_none)
@click.option('-o', '--on', type=str, multiple=True,
              help='Argument name to check for intersection. You can use this '
                   'argument more than once.')
@click.option('-b', '--base', type=click.Choice(['1', '2']), default='0',
              help='1 or 2, to indicate `crumb1` or `crumb2` as a base crumb2 '
                   'to print the results')
def intersect(crumb1, crumb2, on, base):
    """Return the intersection between crumb1 and crumb2 on a given argument.

    Will not print full paths, but only values for the crumb arguments in `on`.
    Unless you specify the crumb you want to use as a base with the `base`
    argument.

    Examples: \n
    crumb intersect --on "sid" "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"\n
    """
    from .. import intersection

    values = intersection(crumb1, crumb2, on=on)
    if base == '0':
        _print_values_map_as_csv(values)
    else:
        if base == '1':
            base_crumb = crumb1
        else:
            base_crumb = crumb2

        echo_list(base_crumb.build_paths(values))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('crumb1', type=CrumbPath(), callback=check_not_none)
@click.argument('crumb2', type=CrumbPath(), callback=check_not_none)
@click.option('-o', '--on', type=str, multiple=True,
              help='Argument name to check for intersection. You can use this '
                   'argument more than once.')
@click.option('-b', '--base', type=click.Choice(['1', '2']), default='0',
              help='1 or 2, to indicate `crumb1` or `crumb2` as a base crumb2 '
                   'to print the results')
def diff(crumb1, crumb2, on, base):
    """Return the difference crumb1 - crumb2 on a given argument.

    Will not print full paths, but only values for the crumb arguments in `on`.
    Unless you specify the crumb you want to use as a base with the `base`
    argument.

    Examples: \n
    crumb diff --on "sid" "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"\n
    """
    from .. import difference

    values = difference(crumb1, crumb2, on=on)
    if base == '0':
        _print_values_map_as_csv(values)
    else:
        if base == '1':
            base_crumb = crumb1
        else:
            base_crumb = crumb2

        echo_list(base_crumb.build_paths(values))
