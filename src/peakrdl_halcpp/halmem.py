from typing import TYPE_CHECKING

from systemrdl.node import MemNode, AddressableNode

from .halbase import HalBase

if TYPE_CHECKING:
    from .haladdrmap import HalAddrmap


class HalMem(HalBase):
    """HAL wrapper class for PeakRDL MemNode."""

    def __init__(self,
                 node: MemNode,
                 parent: 'HalAddrmap',
                 bus_offset: int = 0,
                 ):
        super().__init__(node, parent)

        self.bus_offset = bus_offset

        parent_node = self.get_parent()

        # Can this be removed?
        if parent_node is not None:
            for c in parent_node._node.children():
                if isinstance(c, AddressableNode):
                    assert c == self._node, (f"Addrmaps with anything else than "
                                             "one memory node is currently not allowed, "
                                             "it could be easily added")

    def get_template_line(self) -> str:
        return f"template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>"

    @property
    def cpp_access_type(self) -> str:
        assert False, "cpp_access_type should not be called on HalMem class"

    def get_cls_tmpl_params(self) -> str:
        return "<BASE, SIZE, PARENT_TYPE>"

