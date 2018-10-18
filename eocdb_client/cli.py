import json
from typing import Sequence

import click

from .api import JsonObj
from .version import LICENSE_TEXT, VERSION


def _dump_json(obj: JsonObj):
    print(json.dumps(obj, indent=2))


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
        _dump_json(config)


@click.command(name='upl')
@click.argument('path', metavar='<path>')
@click.argument('dataset_files', metavar='<dataset-file> ...', nargs=-1, type=click.UNPROCESSED)
@click.option('--doc-file', '-d', 'doc_files', metavar='<doc-file>', nargs=1,
              multiple=True,
              help="Labels all subsequent files as documentation files")
@click.pass_context
def upload_datasets(ctx, path: str, dataset_files: Sequence[str], doc_files: Sequence[str]):
    """Upload multiple dataset and documentation files."""
    if not dataset_files:
        raise click.ClickException("At least a single <dataset-file> must be given.")
    validation_results = ctx.obj.upload_datasets(path, dataset_files, doc_files)
    _dump_json(validation_results)


@click.command(name='find')
@click.argument('expr', metavar='<expr>')
@click.pass_context
def find_datasets(ctx, expr):
    """Find datasets using query expression <expr>."""
    dataset_refs = ctx.obj.find_datasets(expr)
    _dump_json(dataset_refs)


@click.command(name="get")
@click.option('--id', metavar='<id>', help='Dataset ID.')
@click.option('--path', metavar='<path>', help='Dataset path into the store of the form affil/project/cruise/name.')
@click.pass_context
def get_dataset(ctx, id: str, path: str):
    """Get dataset with given <id> or <path>."""
    if (not id and not path) or (id and path):
        raise click.ClickException("Either <id> or <path> must be given.")
    if id:
        dataset = ctx.obj.get_dataset(id)
    else:
        dataset = ctx.obj.get_dataset_by_name(path)
    _dump_json(dataset)


@click.command(name="list")
@click.argument('path', metavar='<path>')
@click.pass_context
def list_datasets(ctx, path):
    """List datasets in <path>."""
    dataset = ctx.obj.list_datasets_in_path(path)
    _dump_json(dataset)


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
    validation_result = ctx.obj.validate_dataset(file)
    _dump_json(validation_result)


# noinspection PyShadowingBuiltins
@click.group()
@click.version_option(VERSION)
@click.option('--server', 'server_url', metavar='<url>', envvar='EOCDB_SERVER_URL', help='OC-DB Server URL.')
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
