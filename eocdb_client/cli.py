import json

import click

from eocdb_client.version import LICENSE_TEXT, VERSION


@click.command()
@click.argument('name', required=False)
@click.argument('value', required=False)
@click.pass_context
def conf(ctx, name, value):
    """
    Configuration management.
    Set configuration parameter NAME to VALUE, display configuration parameter NAME,
    or display all configuration parameters.
    """
    if name is not None and value is not None:
        ctx.obj.set_config_param(name, value, write=True)
    else:
        if name is not None:
            config = {name: ctx.obj.get_config_param(name)}
        else:
            config = ctx.obj.config
        print(json.dumps(config, indent=2))


@click.command(name='upl')
@click.argument('zipfile', metavar='<zipfile>')
@click.option('--affil', '-a', metavar='<affiliation>', default="no_affil")
@click.option('--project', '-p', metavar='<project>', default="no_project")
@click.option('--cruise', '-c', metavar='<cruise>', default="no_cruise")
@click.pass_context
def upload_datasets(ctx, zipfile, affil=None, project=None, cruise=None):
    """Upload multiple datasets using ZIP file <zipfile>. The file may also contain documentation files."""
    result = ctx.obj.upload_datasets(zipfile, affil=affil, project=project, cruise=cruise)
    if result:
        print(result)


@click.command(name='find')
@click.argument('expr', metavar='<expr>')
@click.pass_context
def find_datasets(ctx, expr):
    """Find datasets using query expression <expr>."""
    dataset_refs = ctx.obj.find_datasets(expr)
    if dataset_refs:
        print(dataset_refs)
    else:
        print('No results.')


@click.command(name="get")
@click.argument('id', metavar='<id>')
@click.pass_context
def get_dataset(ctx, expr):
    """Get dataset with given <id>."""
    dataset = ctx.obj.get_dataset(id)
    if dataset:
        print(dataset)
    else:
        print('No results.')


@click.command(name="add")
@click.argument('file', metavar='<file>')
@click.pass_context
def add_dataset(ctx, file):
    """Add dataset <file>."""
    ctx.obj.add_dataset(file)


# noinspection PyShadowingBuiltins
@click.command(name="del")
@click.argument('id', metavar='<id>')
@click.pass_context
def delete_dataset(ctx, id):
    """Delete dataset given by <id>."""
    ctx.obj.delete_dataset(id)


@click.command(name="upd")
@click.argument('file', metavar='<file>')
@click.pass_context
def update_dataset(ctx, file):
    """Update dataset <file>."""
    ctx.obj.update_dataset(file)


@click.command(name="val")
@click.argument('file', metavar='<file>')
@click.pass_context
def validate_dataset(ctx, file):
    """Validate dataset <file>."""
    ctx.obj.validate_dataset(file)


# noinspection PyShadowingBuiltins
@click.group()
@click.version_option(VERSION)
@click.option('--server_url', '-s', envvar='EOCDB_SERVER_URL', help='OC-DB Server URL.')
@click.option('--license', is_flag=True, is_eager=True, help='Show the license and exit.')
@click.pass_context
def cli(ctx, server_url, license):
    """
    EUMETSAT Ocean Color In-Situ Database Client.
    """
    if server_url is not None:
        ctx.obj.server_url = server_url
    if license:
        click.echo(LICENSE_TEXT)
        ctx.exit()


@click.group()
def ds():
    """
    Dataset management.
    """
    pass


@click.group()
def df():
    """
    Documentation files management.
    """
    pass


@click.group()
def user():
    """
    User management.
    """
    pass


cli.add_command(conf)
cli.add_command(ds)
cli.add_command(df)
cli.add_command(user)

ds.add_command(upload_datasets)
ds.add_command(find_datasets)
ds.add_command(get_dataset)
ds.add_command(add_dataset)
ds.add_command(delete_dataset)
ds.add_command(update_dataset)
ds.add_command(validate_dataset)
