import click

from eocdb_client.api import Api


@click.command(help='Set configuration parameter <name> to <value>')
@click.argument('name', metavar='<name>')
@click.argument('value', metavar='<value>')
@click.pass_context
def config(ctx, name, value):
    Api().config(name, value)


@click.command(help='Query measurement records using query expression <expr>')
@click.argument('expr', metavar='<expr>')
@click.pass_context
def query(ctx, expr):
    Api(server_url=ctx.obj['server_url']).query(expr)


@click.command(help='Add records of measurement data file <file>')
@click.argument('file', metavar='<file>')
@click.pass_context
def add(ctx, file):
    Api(server_url=ctx.obj['server_url']).add(file)


@click.command(help='Remove measurement record <id>')
@click.argument('id', metavar='<id>')
@click.pass_context
def remove(ctx, id):
    Api(server_url=ctx.obj['server_url']).remove(id)


@click.group()
@click.option('--server', '-s', envvar='EOCDB_SERVER_URL', help='Server URL')
@click.pass_context
def cli(ctx, server):
    """
    EUMETSAT Ocean Color In-Situ Database Client.
    """
    ctx.obj['server_url'] = server


cli.add_command(config)
cli.add_command(query)
cli.add_command(add)
cli.add_command(remove)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
