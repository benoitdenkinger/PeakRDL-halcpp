from typing import List, Type, Dict, Union
import getpass
import datetime

from .halnode import HalAddrmapNode


class HalUtils():
    """
    HAL utility class.

    Class methods:

    - :func:`get_include_file`
    - :func:`has_extern`
    - :func:`get_extern`
    - :func:`generate_file_header`
    """

    def __init__(self, ext_modules: List[str]) -> None:
        #: List of modules (i.e., SystemRDL addrmap objects) with extended functionalities.
        self.ext_modules = ext_modules

    def get_include_file(self, halnode: HalAddrmapNode) -> str:
        """Returns the HAL node header file to include."""
        has_extern = self.has_extern(halnode)
        return halnode.inst_name_hal + "_ext.h" if has_extern else halnode.inst_name_hal + ".h"

    def has_extern(self, halnode: HalAddrmapNode) -> bool:
        """Returns True if the HAL node is listed as having extended functionalities."""
        if self.ext_modules is not None:
            if halnode.inst_name in self.ext_modules:
                return True
        return False

    def get_extern(self, halnode: HalAddrmapNode) -> str:
        """Return the HAL node instance name with the '_ext' suffix if the node is listed
        as having extended functionalities."""
        if self.has_extern(halnode):
            return halnode.inst_name_hal + '_ext'
        return halnode.inst_name_hal

    def generate_file_header(self) -> str:
        """Returns file header for generated files."""
        username = getpass.getuser()
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment = f"// Generated with PeakRD-halcpp : https://github.com/Risto97/PeakRDL-halcpp\n"
        comment += f"// By user: {username} at: {current_datetime}\n"
        return comment
