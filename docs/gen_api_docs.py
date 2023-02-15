"""
Generate API reference pages; based on the recipe by the `mkdocstrings` plugin.
"""

from pathlib import Path
import mkdocs_gen_files

SRC_PATH: Path = Path(__file__).parent.parent/"src"
HERE = Path(__file__).parent

nav = mkdocs_gen_files.Nav()

for path in sorted(SRC_PATH.rglob("*.py")):
    module_path = path.relative_to(SRC_PATH).with_suffix("")
    module_name = module_path.name
    
    if not module_name[0] == "_":
        doc_path = path.relative_to(SRC_PATH).with_suffix(".md")
        full_doc_path = Path("api")/doc_path

        parts = tuple(module_path.parts)
        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("api/modules.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())