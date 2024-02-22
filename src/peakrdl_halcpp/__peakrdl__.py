from typing import TYPE_CHECKING

from peakrdl.plugins.exporter import ExporterSubcommandPlugin  # pylint: disable=import-error

from .exporter import HalExporter

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode


class Exporter(ExporterSubcommandPlugin):
    """Generates C++ Hardware Abstraction Layer (HAL) libraries."""

    short_desc = 'Generates C++ Hardware Abstraction Layer (HAL) libraries.'
    long_desc = 'Generates C++ Hardware Abstraction Layer (HAL) libraries.'

    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        """Adds custom arguments to the plugin."""
        arg_group.add_argument(
            "--ext",
            nargs="*",
            help="List of addrmap modules that have implemented <name>_EXT class in \
                <name>_ext.h header file, used for extending functionality."
        )

        arg_group.add_argument(
            "--list-files",
            dest="list_files",
            default=False,
            action="store_true",
            help="Dont generate files, but instead just list the files that will be \
                generated, and external files that need to be included."
        )

        arg_group.add_argument(
            "--skip-buses",
            dest="skip_buses",
            default=False,
            action="store_true",
            help="If there is an addrmap containing only addrmaps, not registers, by \
                default it will be omitted in hierarchy, it is possible to keep it by \
                passing --keep-buses flag."
        )

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        """Plugin entry function."""
        hal = HalExporter()
        hal.export(
            node=top_node,
            outdir=options.output,
            list_files=options.list_files,
            ext_modules=options.ext,
            skip_buses=options.skip_buses,
        )
