from typing import Union, Any, Optional, Type
from abc import ABC, abstractmethod, abstractproperty

from systemrdl.node import RootNode, Node, AddrmapNode

class HalAddrmapNode(AddrmapNode):
    def __init__(self, node: AddrmapNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

    @property
    def is_top_node(self) -> bool:
        """Checks if this is the top node."""
        return self.parent == RootNode

    def get_template_line(self) -> str:
        if self.is_top_node:
            # Parent is set to void by default for the top node
            return "template <uint32_t BASE, typename PARENT_TYPE=void>"
        return "template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        return "<BASE, PARENT_TYPE>"

    # def get_addrmaps_recursive(self) -> List['HalAddrmapNode']:
    #     """Recursively fetch the HalAddrmap nodes into a list.

    #     Gets the AddrMapNode hierarchy of the SystemRDL description.
    #     Here is a pseudo-SystemRDL code example for an basic SoC design.

    #     ::

    #         addrmap mySoC {
    #             addrmap myMem0 @ 0x40000000
    #             addrmap mySubsystem @ 0x44000000 {
    #                 addrmap myPeriph0 @ 0x00001000
    #                 addrmap myPeriph1 @ 0x00002000
    #             }
    #             addrmap myMem1 @ 0x41000000
    #             ...
    #         }

    #     Called on the top node (i.e., mySoC) this function returns:

    #     [mySoC, myMem0, mySubsystem, myPeriph0, myPeriph1, myMem1]

    #     where each element is a HalAddrmap object. Only the top node
    #     insert its own reference (i.e., mySoC) at the beginning.

    #     Returns
    #     -------
    #     List[HalAddrmap]
    #         A list of all HalAddrmap nodes contained within this HalAddrmap node.
    #     """
    #     addrmaps = self.addrmaps.copy()
    #     for child in self.children():
    #         addrmaps.extend(c.get_addrmaps_recursive())
    #     # Top node insert its own reference, why?
    #     if self.is_top_node:
    #         addrmaps.insert(0, self)
    #     return addrmaps

# class HalNode(ABC):
#     @abstractproperty
#     def cpp_access_type(self) -> str:
#         """Node access type (read and/or write) property. It must be
#         overloaded by the child class.

#         Returns
#         -------
#         str
#             A string with the child class name followed by the access
#             rights. For example, a field node with read only access
#             would return 'FieldRO'.
#         """
#         pass
#     @abstractmethod
#     def get_template_line(self) -> str:
#         """Returns the node C++ template line as a string. This method
#         must be overloaded by the child class.

#         This C++ string template (e.g., 'template<type MYVAR, ...>')

#         Returns
#         -------
#         str
#             C++ string template (e.g., 'template<type MYVAR, ...>') of the
#             node type (e.g., reg, mem).
#         """
#         pass

#     @abstractmethod
#     def get_cls_tmpl_params(self) -> str:
#         """Returns the class template parameters. This method must be
#         overloaded by the child class.

#         The parameters correspond to the template parameters returned
#         by :func:`get_template_line`.

#         Returns
#         -------
#         str
#             C++ string template parameters.
#         """
#         pass
