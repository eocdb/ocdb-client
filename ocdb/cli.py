import sys
import json
from typing import Sequence, List, Optional

import click

from .api import JsonObj
from .version import VERSION, LICENSE_TEXT

sys.tracebacklimit = 0


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


@click.command(name='upload')
@click.argument('store_path', metavar='<store_path>')
@click.argument('dataset-files', metavar='<dataset-file> ...', nargs=-1)
@click.option('--doc-file', '-d', 'doc_files', metavar='<doc-file>', nargs=1,
              multiple=True,
              help="Labels all subsequent files as documentation files")
@click.option('--submission-id', '-s', 'submission_id', metavar='<submission-id>', nargs=1, help="Give submission ID")
@click.option('--publication-date', '-pd', 'publication_date', metavar='<publication-date>', nargs=1,
              help="set date for publication")
@click.option('--allow-publication', '-ap', 'allow_publication', metavar='<allow-publication>', is_flag=True,
              help="Specify whether you agree to publish the data")
@click.pass_context
def upload_submission(ctx, store_path: str, dataset_files: Sequence[str], doc_files: Sequence[str],
                      submission_id: str, publication_date: str, allow_publication: bool):
    """Upload multiple dataset and documentation files."""
    if not dataset_files:
        raise click.ClickException("At least a single <dataset-file> must be given.")
    if not submission_id:
        raise click.ClickException("Please give a submission ID.")
    if not store_path:
        raise click.ClickException("Please give a path. Format should be affiliation/cruise/experiment")

    validation_results = ctx.obj.upload_submission(store_path=store_path, dataset_files=dataset_files,
                                                   doc_files=doc_files, submission_id=submission_id,
                                                   publication_date=publication_date,
                                                   allow_publication=allow_publication)
    _dump_json(validation_results)


@click.command(name="download")
@click.option('--dataset-ids', '-ids', metavar='<dataset-ids>', help='Specify dataset IDs', multiple=True)
@click.option('--download-docs', '-docs', metavar='<docs>', help='Get docs, too', is_flag=True)
@click.option('--out-file', '-o', metavar='<out-file>', help='Specify name for the outfile (zip)')
@click.pass_context
def download_datasets(ctx, dataset_ids: List[str], download_docs: bool, out_file: str):
    """Download dataset files --dataset-ids <id> --download-docs [--out-file <out-file>]."""

    if not dataset_ids:
        raise click.ClickException("Please give at least one dataset-id.")

    result = ctx.obj.download_datasets_by_ids(dataset_ids, download_docs, out_file)
    print(result)


@click.command(name="get")
@click.option('--id', 'dataset_id', metavar='<id>',
              help='Dataset ID.')
@click.option('--path', '-p', 'dataset_path', metavar='<path>',
              help='Dataset path of the form affil/project/cruise/name.')
@click.pass_context
def get_dataset(ctx, dataset_id: str, dataset_path: str):
    """Get dataset with given <id> or <path>."""
    if (not dataset_id and not dataset_path) or (dataset_id and dataset_path):
        raise click.ClickException("Either <id> or <path> must be given.")
    if dataset_id:
        dataset = ctx.obj.get_dataset(dataset_id)
    else:
        dataset = ctx.obj.get_dataset_by_name(dataset_path)
    _dump_json(dataset)


@click.command(name='find')
@click.option('--expr', metavar='<expr>',
              help="Query expression")
@click.option('--query', metavar='<query>', type=str, multiple=True,
              help='Query the dataset attributes --query <attribute>=<value>. Possible attributes are: '
                   'path, submission_id, user_id, pgroup, pname, pmode')
@click.option('--offset', metavar='<offset>', type=int, default=1,
              help="Results offset. Offset of first result is 1.")
@click.option('--count', metavar='<count>', type=int, default=1000,
              help="Maximum number of results.")
@click.pass_context
def find_datasets(ctx, expr, offset, count, query):
    """Find datasets using query expression <expr>."""

    if not expr and not query:
        raise click.ClickException("Please give either an <expr> or a <query>.")

    kwargs = {'expr': expr, 'offset': offset, 'count': count}

    for q in query:
        buffer = q.split('=')
        if len(buffer) == 2:
            buffer = q.split('=')
            kwargs[buffer[0]] = buffer[1]
        else:
            raise click.ClickException("Please use syntax --query field1=value1 --query field2=value2")

    dataset_refs = ctx.obj.find_datasets(**kwargs)
    _dump_json(dataset_refs)


@click.command(name="list")
@click.argument('path', metavar='<path>')
@click.pass_context
def list_datasets(ctx, path):
    """List datasets in <path>."""

    if not path:
        raise click.ClickException("Please give a <path>.")

    dataset = ctx.obj.list_datasets_in_path(path)
    _dump_json(dataset)


# noinspection PyShadowingBuiltins
@click.command(name="del")
@click.argument('id', metavar='<id>')
@click.pass_context
def delete_dataset(ctx, id):
    """Delete dataset given by <id>."""
    if not id:
        raise click.ClickException("Please give an <id>.")
    ctx.obj.delete_dataset(id)


@click.command(name="val")
@click.argument('file', metavar='<file name>', required=True)
@click.pass_context
def validate_submission_file(ctx, file):
    """Validate submission <file> before upload."""
    validation_result = ctx.obj.validate_submission_file(file)
    _dump_json(validation_result)


@click.command(name="get-by-sb")
@click.argument('submission-id', metavar='<submission-id>', required=True)
@click.pass_context
def get_datasets_by_submission(ctx, submission_id):
    """Get datasets by submission <submission_id>"""
    result = ctx.obj.get_datasets_by_submission(submission_id=submission_id)
    _dump_json(result)


@click.command(name="del-by-sb")
@click.argument('submission-id', metavar='<submission-id>', required=True)
@click.pass_context
def delete_datasets_by_submission(ctx, submission_id):
    """Delete datasets by <submission_id>"""
    result = ctx.obj.delete_datasets_by_submission(submission_id=submission_id)
    _dump_json(result)


@click.command(name="get")
@click.argument('submission-id', metavar='<submission-id>', required=True)
@click.pass_context
def get_submission(ctx, submission_id: str):
    """Get submission <submission_id>."""
    result = ctx.obj.get_submission(submission_id)
    _dump_json(result)


@click.command(name="user")
@click.argument('user-name', metavar='<user-name>', default=None, required=False)
@click.pass_context
def get_submissions_for_user(ctx, user_name: Optional[str]):
    """Get submissions for user <user_name>."""
    result = ctx.obj.get_submissions_for_user(user_name)
    _dump_json(result)


@click.command(name="delete")
@click.argument('submission-id', metavar='<submission-id>', required=True)
@click.pass_context
def delete_submission(ctx, submission_id: str):
    """Delete submission <submission_id>."""
    result = ctx.obj.delete_submission(submission_id)
    _dump_json(result)


@click.command(name="status")
@click.option('--submission-id', '-s', metavar='<submission-id>', help='Specify submission ID', required=True)
@click.option('--status', '-st', metavar='<status>', help='Specify new status', required=True)
@click.pass_context
def update_submission_status(ctx, submission_id: str, status: str):
    """Update submission status --submission-id <submission_id> --status <status>."""
    result = ctx.obj.update_submission_status(submission_id, status)
    _dump_json(result)


@click.command(name="download")
@click.option('--submission-id', '-s', metavar='<submission-id>', help='Specify submission ID', required=True)
@click.option('--index', '-i', metavar='<index>', help='Specify submission file index', required=True)
@click.option('--out-file', '-o', metavar='<out-file>', help='Specify name for the outfile (zip)')
@click.pass_context
def download_submission_file(ctx, submission_id: str, index: int, out_file: str):
    """Get submission file --submission_id <submission_id> --index <index> [--out-file <name>]."""
    result = ctx.obj.download_submission_file(submission_id, index, out_file)
    print(result)


@click.command(name="get")
@click.option('--submission-id', '-s', metavar='<submission-id>', help='Specify submission ID', required=True)
@click.option('--index', '-s', metavar='<index>', help='Specify submission file index', required=True)
@click.pass_context
def get_submission_file(ctx, submission_id: str, index: int):
    """Get submission file --submission_id <submission_id> --index <index>."""
    result = ctx.obj.get_submission_file(submission_id, index)
    print(result)


@click.command(name='upload')
@click.option('--file', metavar='<submission-file>', help="Give submission file to re-upload", required=True)
@click.option('--submission-id', '-s', 'submission_id', metavar='<submission-id>', help="Give submission ID",
              required=True)
@click.option('--index', '-s', metavar='<index>', help='Specify submission file index', required=True)
@click.pass_context
def upload_submission_file(ctx, submission_id: str, index: int, file: str):
    """Upload multiple dataset and documentation files."""
    validation_results = ctx.obj.upload_submission_file(submission_id, index, file)
    _dump_json(validation_results)


@click.command(name="lic")
def show_license():
    """
    Show license and exit.
    """
    click.echo(LICENSE_TEXT)


# noinspection PyShadowingBuiltins
@click.group()
@click.version_option(VERSION)
@click.option('--server', 'server_url', metavar='<url>', envvar='OCDB_SERVER_URL', help='OCDB Server URL.')
@click.pass_context
def cli(ctx, server_url):
    """
    EUMETSAT Ocean Color In-Situ Database Client.
    """
    if server_url is not None:
        ctx.obj.server_url = server_url


@click.command(name="add")
@click.option('--username', '-u', metavar='<username>', help='Username', required=True)
@click.option('--password', '-p', metavar='<password>', help='Password', required=True)
@click.option('--first-name', '-fn', metavar='<first_name>', help='First Name', default='')
@click.option('--last-name', '-ln', metavar='<last_name>', help='Last Name', default='')
@click.option('--email', '-em', metavar='<email>', help='Email', required=True)
@click.option('--phone', '-ph', metavar='<phone>', help='Phone', default='')
@click.option('--roles', '-r', metavar='<roles>', help='Roles', multiple=True, required=True)
@click.pass_context
def add_user(ctx, username: str, password: str, first_name: str, last_name: str, email: str, phone: str,
             roles: Sequence[str]):
    """Add a user"""
    result = ctx.obj.add_user(username=username, password=password, first_name=first_name,
                              last_name=last_name, email=email, phone=phone, roles=roles)
    _dump_json(result)


@click.command(name="update")
@click.option('--username', '-u', metavar='<username>', help='Username', required=True)
@click.option('--key', '-k', metavar='<key>', help='Key (e.g. name)', required=True)
@click.option('--value', '-v', metavar='<value>', help='Value for the field. Can be username, password, first_name, '
                                                       'last_name, email, phone, roles', required=True)
@click.pass_context
def update_user(ctx, username: str, key: str, value: str):
    """Update an existing user"""
    result = ctx.obj.update_user(username, key, value)
    _dump_json(result)


@click.command(name="pwd")
@click.option('--username', '-u', metavar='<username>', help='Username', prompt=True)
@click.option('--password', '-p', metavar='<password>', help='New Password',
              prompt=True, hide_input=True, confirmation_prompt=True)
@click.pass_context
def change_login(ctx, username: str, password: str):
    """Set the password for an existing user"""
    result = ctx.obj.change_user_login(username=username, password=None, new_password=password)
    _dump_json(result)


@click.command(name="ownpwd")
@click.option('--old-password', '-op', metavar='<old-password>', help='Old Password',
              prompt=True, hide_input=True)
@click.option('--password', '-p', metavar='<password>', help='New Password',
              prompt=True, hide_input=True, confirmation_prompt=True)
@click.pass_context
def change_own_login(ctx, old_password: str, password: str):
    """Set the password for an existing user"""
    result = ctx.obj.change_user_login(username=None, password=old_password, new_password=password)
    _dump_json(result)


@click.command(name="login")
@click.option('--username', '-u', metavar='<username>', help='Username', prompt=True)
@click.option('--password', '-p', metavar='<password>', help='Password', prompt=True, hide_input=True)
@click.pass_context
def login_user(ctx, username: str, password: str):
    """Login a user"""
    result = ctx.obj.login_user(username, password)
    _dump_json(result)


@click.command(name="whoami")
@click.pass_context
def whoami_user(ctx):
    """Who am I"""
    result = ctx.obj.whoami_user()
    _dump_json(result)


@click.command(name="list")
@click.pass_context
def list_user(ctx):
    """Who am I"""
    result = ctx.obj.list_user()
    _dump_json(result)


@click.command(name="logout")
@click.pass_context
def logout_user(ctx):
    """Log out current user if logged in."""
    result = ctx.obj.logout_user()
    _dump_json(result)


@click.command(name="get")
@click.argument('username', metavar='<username>', required=True)
@click.pass_context
def get_user(ctx, username: str):
    """Get user <username>."""
    result = ctx.obj.get_user(username)
    _dump_json(result)


@click.command(name="delete")
@click.argument('username', metavar='<username>', required=True)
@click.pass_context
def delete_user(ctx, username: str):
    """Delete user by <username>."""
    result = ctx.obj.delete_user(username)
    _dump_json(result)


@click.group()
def ds():
    """
    Dataset management.
    """


@click.group()
def sbm():
    """
    Submission management.
    """


@click.group()
def sbmfile():
    """
    Submission management.
    """


@click.group()
def df():
    """
    Documentation files management.
    """


@click.group()
def user():
    """
    User management.
    """


cli.add_command(conf)
cli.add_command(ds)
# cli.add_command(df)
cli.add_command(sbm)
cli.add_command(sbmfile)
cli.add_command(user)
cli.add_command(show_license)

ds.add_command(find_datasets)
ds.add_command(download_datasets)
ds.add_command(get_dataset)
# ds.add_command(add_dataset)
# ds.add_command(delete_dataset)
# ds.add_command(update_dataset)
# ds.add_command(list_datasets)
ds.add_command(delete_dataset)
ds.add_command(list_datasets)
ds.add_command(get_datasets_by_submission)
ds.add_command(delete_datasets_by_submission)

sbm.add_command(update_submission_status)
sbm.add_command(upload_submission)
sbm.add_command(get_submission)
sbm.add_command(get_submissions_for_user)
sbm.add_command(delete_submission)

sbmfile.add_command(download_submission_file)
sbmfile.add_command(upload_submission_file)

user.add_command(add_user)
user.add_command(update_user)
user.add_command(change_own_login)
user.add_command(change_login)
user.add_command(get_user)
user.add_command(delete_user)
user.add_command(whoami_user)
user.add_command(list_user)
user.add_command(login_user)
user.add_command(logout_user)
