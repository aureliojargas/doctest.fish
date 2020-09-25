import sys

from doctester import core

if __name__ == "__main__":
    parser = core.setup_cmdline_parser()
    parsed_args = parser.parse_args()

    passed = core.main(parsed_args)
    sys.exit(0 if passed else 1)
