import cProfile
import io
import pstats
from ocdb.api import new_api
from ocdb.cli import cli


_PROFILING_ON = True

if _PROFILING_ON:
    pr = cProfile.Profile()
    pr.enable()


def main(args=None):
    cli.main(args=args, obj=new_api())


if __name__ == '__main__':
    main()


if _PROFILING_ON:
    # noinspection PyUnboundLocalVariable
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
    ps.print_stats()
    print(s.getvalue())
