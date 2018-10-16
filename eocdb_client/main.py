from eocdb_client.api import new_api
from eocdb_client.cli import cli


def main(args=None):
    cli.main(args=args, obj=new_api())


if __name__ == '__main__':
    main()
