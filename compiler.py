from __future__ import annotations

from importlib import util
from pathlib import Path
import sys


def _bootstrap_package() -> None:
    package_dir = Path(__file__).with_name("compiler")
    spec = util.spec_from_file_location(
        "compiler",
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load compiler package")

    module = util.module_from_spec(spec)
    sys.modules["compiler"] = module
    spec.loader.exec_module(module)


def main() -> None:
    _bootstrap_package()
    from main import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
