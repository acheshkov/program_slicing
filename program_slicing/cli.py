__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

import argparse
import os

from program_slicing.decomposition import slicing

SLICE = "slice"

SOURCE = "source"

OUTPUT_OPT = "--output"
OUTPUT_OPT_SHORT = "-o"

URI_TYPE_STDIO = "s"
URI_TYPE_FILE = "f"
URI_TYPE_DIRECTORY = "d"
URI_TYPE_URL = "u"


def get_uri_type(uri: str) -> str:
    if uri is None:
        return URI_TYPE_STDIO
    if os.path.isfile(uri):
        return URI_TYPE_FILE
    if os.path.isdir(uri):
        return URI_TYPE_DIRECTORY
    if os.path.islink(uri):
        return URI_TYPE_URL
    if uri.startswith('http') or uri.startswith('ssh'):
        return URI_TYPE_URL
    if os.path.splitext(uri)[1] == '':
        return URI_TYPE_DIRECTORY
    return URI_TYPE_FILE


def get_uri_message(uri: str) -> str:
    if uri is None:
        return "stdio"
    return "current work directory" if (uri == "" or uri == ".") else ("'" + uri + "'")


def cli() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="", required=True)

    generate_data = subparsers.add_parser(
        SLICE,
        help="generate slice decomposition and save it to a specific folder or file")
    generate_data.add_argument(
        SOURCE,
        help="source folder, file or url")
    generate_data.add_argument(
        OUTPUT_OPT_SHORT,
        OUTPUT_OPT,
        help="output file or directory: depending on what you set as output, "
             "you will get folder full of slice decompositions or a single file with it. "
             "It uses stdout if not specified")

    args = parser.parse_args()
    source = os.path.normpath(args.source)
    source = "" if source is None else source
    source_type = get_uri_type(source)
    if source_type != URI_TYPE_URL and not source == "" and not os.path.exists(source):
        source_type = URI_TYPE_URL
    output_option = None if args.output is None else os.path.normpath(args.output)
    if args.command == SLICE:
        __check_slice(source, source_type, output_option, args)


def __check_slice(source: str, source_type: str, output_option: str, args: argparse.Namespace) -> None:
    if source_type == URI_TYPE_DIRECTORY:
        __check_slice_from_directory(source, output_option, args)

    elif source_type == URI_TYPE_FILE:
        __check_slice_from_file(source, output_option, args)

    else:
        print("Unsupported source '" + source + "'")


def __check_slice_from_file(source: str, output_option: str, args: argparse.Namespace) -> None:
    source_message = get_uri_message(source)
    output_message = get_uri_message(output_option)
    output_option_type = get_uri_type(output_option)
    if output_option_type == URI_TYPE_STDIO:
        print("Print all possible slice decompositions of " + source_message)
        slicing.decompose_file(source)

    elif output_option_type == URI_TYPE_DIRECTORY:
        print("Save to the " + output_message + " all the slice decompositions of " + source_message)
        print("Arguments combination is not yet supported: " + str(args))

    elif output_option_type == URI_TYPE_FILE:
        print("Unsupportable option: save slice decomposition of " + source_message + " to " + output_message)

    elif output_option_type == URI_TYPE_URL:
        print("Unsupportable option: send slice decomposition of " + source_message + " to " + output_option)

    else:
        print("Unsupported output: " + output_message)


def __check_slice_from_directory(source: str, output_option: str, args: argparse.Namespace) -> None:
    source_message = get_uri_message(source)
    output_message = get_uri_message(output_option)
    output_option_type = get_uri_type(output_option)
    if output_option_type == URI_TYPE_STDIO:
        print("Print all possible slice decompositions of files from " + source_message)
        print("Arguments combination is not yet supported: " + str(args))

    elif output_option_type == URI_TYPE_DIRECTORY:
        print("Save to the " + output_message + " all the slice decompositions of files from " + source_message)
        print("Arguments combination is not yet supported: " + str(args))

    elif output_option_type == URI_TYPE_FILE:
        print("Unsupportable option: save slice decomposition of files "
              "from the " + source_message + " to " + output_message)

    elif output_option_type == URI_TYPE_URL:
        print("Unsupportable option: send slice decomposition of files "
              "from the " + source_message + " to " + output_option)

    else:
        print("Unsupported output: " + output_message)


if __name__ == "__main__":
    cli()
