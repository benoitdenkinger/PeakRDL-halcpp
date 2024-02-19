from typing import List, Type, Dict, Union
import getpass
import datetime

from systemrdl.node import AddrmapNode

from .halnode import HalBaseNode, HalAddrmapNode, HalFieldNode

# def get_owning_haladdrmap(self, node: HalBase) -> Union[HalBase, HalAddrmapNode]:
#     """Returns the HalAddrmapNode object enclosing this node."""
#     parent_node = node.get_parent()
#     if isinstance(parent_node, HalAddrmapNode):
#         return parent_node
#     elif parent_node is not None:
#         return self.get_owning_haladdrmap(parent_node)
#     else:
#         raise ValueError(f'No HalAddrmapNode parent found in the hierarchy.')


class HalUtils():
    """
    HAL utility class.

    Class methods:

    - :func:`get_include_file`
    - :func:`has_extern`
    - :func:`get_extern`
    - :func:`get_unique_type_nodes`
    - :func:`generate_file_header`
    - :func:`build_hierarchy`
    """

    def __init__(self, ext_modules: List[str]) -> None:
        """Initializes the ext_modules variable with a list of external
        modules implementing extended functionalities (e.g., a read_gpio_port()
        function) to be included to the HAL.

        Parameters
        ----------
        ext_modules: List[str]
            List of modules (i.e., SystemRDL addrmap objects) with extended functionalities.
        """
        self.ext_modules = ext_modules

    def get_include_file(self, halnode: HalAddrmapNode) -> str:
        """Returns the HAL node base header file or the extended header file
        if the later exists.
        """
        has_extern = self.has_extern(halnode)
        return halnode.inst_name_hal + "_ext.h" if has_extern else halnode.inst_name_hal + ".h"

    def has_extern(self, halnode: HalAddrmapNode) -> bool:
        """Returns True if the HAL node is listed as having extended functionalities."""

        if self.ext_modules is not None:
            # print(f"{halnode.type_name} in {self.ext_modules}?")
            if halnode.inst_name in self.ext_modules:
                return True
        return False

    def get_extern(self, halnode: HalAddrmapNode) -> str:
        """Return the ??? name of the HAL node."""
        if self.has_extern(halnode):
            return halnode.inst_name
        return halnode.inst_name_hal

    # def get_unique_type_nodes(self, halnode_lst: List[HalBaseNode]):
    #     """Uniquify a node list"""
    #     # Is this really necessary? You cannot have two nodes with the same name at the
    #     # same hierarchy level -> peakRDL throws an error
    #     # But you can have multiple instances of a certain type
    #     return list({halnode.type_name: halnode for halnode in halnode_lst}.values())

    def generate_file_header(self) -> str:
        """Returns file header for generated files."""
        username = getpass.getuser()
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment = f"// Generated with PeakRD-halcpp : https://github.com/Risto97/PeakRDL-halcpp\n"
        comment += f"// By user: {username} at: {current_datetime}\n"
        return comment

