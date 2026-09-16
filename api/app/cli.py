import argparse

from app.config import get_settings
from app.database import engine
from app.importer import ImportBusyError, ImportValidationError, run_import


def main() -> None:
    parser = argparse.ArgumentParser(prog="brickline")
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import-data", help="import a CSV file or URL")
    importer.add_argument("source", nargs="?")
    importer.add_argument("--name")
    args = parser.parse_args()

    if args.command == "import-data":
        settings = get_settings()
        source = args.source or settings.import_source_url
        name = args.name or settings.import_source_name
        try:
            run = run_import(engine, source, name)
        except (ImportBusyError, ImportValidationError, OSError) as exc:
            parser.exit(1, f"import failed: {exc}\n")
        print(f"imported {run.imported_count} sets from {name}")


if __name__ == "__main__":
    main()
