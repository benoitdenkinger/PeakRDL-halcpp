from systemrdl import RDLCompiler
from peakrdl_halcpp import HalExporter

rdlc = RDLCompiler()
rdlc.compile_file("atxmega_spi.rdl")

root = rdlc.elaborate()
top_gen = root.children(unroll=True)

top = None
for top in top_gen:
    top = top
assert top is not None

exporter = HalExporter()

exporter.export(
        nodes=top,
        outdir="generated",
        )

