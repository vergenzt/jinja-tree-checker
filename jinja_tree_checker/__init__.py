from argparse import ArgumentParser
import importlib
from pathlib import Path
import sys
import tomllib
from typing import Iterable

from tree_sitter import Language, Parser, Query, QueryCursor
from tree_sitter_jinja2 import JINJA2_LANGUAGE


def parse_args(argv=sys.argv):
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default="pyproject.toml",
        help="Path to config file or pyproject.toml",
    )
    args = parser.parse_args(argv)
    return args


def main():
    args = parse_args()
    config = tomllib.load(args.config.read_bytes())
    if args.config.name == "pyproject.toml":
        config = config.get("tool", {}).get("jinja-tree-checker")

    jinja_parser = Parser(JINJA2_LANGUAGE)

    target_lang_name = config["tree-sitter-grammar"]
    target_lang_mod = importlib.import_module(f"tree_sitter_{target_lang_name}")
    target_lang = Language(target_lang_mod.language())
    target_lang_parser = Parser(target_lang)

    files: Iterable[Path] = (file for glob in config["files"] for file in args.config.parent.glob(glob))

    for file in files:
        jinja_tree = jinja_parser.parse(file.read_bytes())

        jinja_query = Query(
            JINJA2_LANGUAGE,
            f"""
            (_text @injection.content
                (#set! injection.language "{target_lang_name}")
            )
            """,
        )
        jinja_cursor = QueryCursor(jinja_query)
        jinja_texts = jinja_cursor.captures(jinja_tree.root_node)
        breakpoint()
