import click

from eocdb_client.api import Api, DefaultConfigStore


@click.command(help='Set configuration parameter NAME to VALUE, '
                    'display configuration parameter NAME, '
                    'or display all configuration parameters')
@click.argument('name', required=False)
@click.argument('value', required=False)
@click.pass_context
def conf(ctx, name, value):
    if name is not None and value is not None:
        ctx.obj.set_config_param(name, value, write=True)
    elif name is not None:
        print(f'{name} = {ctx.obj.get_config_param(name, "")}')
    else:
        print(ctx.obj.config)


@click.command(help='Query measurement records using query expression <expr>')
@click.argument('expr', metavar='<expr>')
@click.pass_context
def query(ctx, expr):
    measurements = ctx.obj.query_measurements(expr)
    if measurements:
        print(measurements)
    else:
        print('No results.')


@click.command(help='Add records of measurement data file <file>')
@click.argument('file', metavar='<file>')
@click.pass_context
def add(ctx, file):
    ctx.obj.add_measurements(file)


@click.command(help='Remove measurement record <id>')
@click.argument('id', metavar='<id>')
@click.pass_context
def remove(ctx, id):
    ctx.obj.remove_measurements(id)


@click.group()
@click.option('--server_url', '-s', envvar='EOCDB_SERVER_URL', help='OC-DB Server URL.')
@click.pass_context
def cli(ctx, server_url):
    """
    EUMETSAT Ocean Color In-Situ Database Client.
    """
    if server_url is not None:
        ctx.obj.server_url = server_url


cli.add_command(conf)
cli.add_command(query)
cli.add_command(add)
cli.add_command(remove)


def main():
    cli(obj=Api(config_store=DefaultConfigStore()))


if __name__ == '__main__':
    main()
