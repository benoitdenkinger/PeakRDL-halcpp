from typing import Union, Any, Optional, Type
from abc import ABC, abstractmethod, abstractproperty

from systemrdl.node import Node, AddrmapNode


class HalBase(ABC):
    """Base abstract class for all the different HAL nodes (Addrmap, Reg, Mem, and Field).

    .. inheritance-diagram:: peakrdl_halcpp.haladdrmap
                             peakrdl_halcpp.halreg
                             peakrdl_halcpp.halmem
                             peakrdl_halcpp.halfield
                             peakrdl_halcpp.halregfile
        :top-classes: peakrdl_halcpp.halbase.HalBase
        :parts: 1

    Class methods:

    - :func:`get_docstring`
    - :func:`get_owning_addrmapnode`
    - :func:`get_property`
    - :func:`get_parent`
    - :func:`get_template_line`
    - :func:`get_cls_tmpl_params`
    """

    def __init__(self, node: Node, parent: Union['HalBase', None]):
        self._node = node
        self._parent = parent
        # The bus offset is an extra address offset added to a subgroup of component
        # when creating a addressmap containing only addressmap nodes (i.e., no register).
        # By default, this intermediate addressmap component is removed by this plugin and
        # its address is added to this bus offset variable.
        self._bus_offset = 0

    @property
    def is_top_node(self) -> bool:
        """Checks if this is the top node."""
        return self._parent == None

    @property
    def addr_offset(self) -> int:
        return self._bus_offset + self._node.address_offset

    @property
    def orig_type_name(self) -> str:
        """Returns the node original type name (not extended with parameter values)."""
        return self._node.orig_type_name

    @property
    def inst_name(self) -> str:
        """Returns the node instance name."""
        # Top node returns a value (same than type_name and orig_type_name)
        # even without an instance name.
        return self._node.inst_name

    @property
    def type_name(self) -> str:
        """Returns the node type name extended with parameter values. If the type
        has no parameter, this value is equal to orig_type_name. If the declaration
        is anonymous (i.e., direct instantiation without type specification), this
        value is equal to inst_name.
        """
        return self.orig_type_name

    @property
    def is_array(self) -> bool:
        """Returns True if the node is an array."""
        return self._node.is_array


    @abstractproperty
    def cpp_access_type(self) -> str:
        """Node access type (read and/or write) property. It must be
        overloaded by the child class.

        Returns
        -------
        str
            A string with the child class name followed by the access
            rights. For example, a field node with read only access
            would return 'FieldRO'.
        """
        pass

    def get_docstring(self) -> str:
        """Converts the node description into a C++ multi-line comment."""
        desc = "/*\n"
        if self._node.get_property('desc') is not None:
            for l in self._node.get_property('desc').splitlines():
                desc = desc + " * " + l + "\n"
            return desc + " */"
        return ""

    def get_property(self, prop_name: str) -> Any:
        """Returns the SystemRDL node property."""
        return self._node.get_property(prop_name)

    def get_owning_addrmapnode(self) -> Optional[AddrmapNode]:
        """Returns the AddrmapNode (system-rdl class) owning this one."""
        return self._node.owning_addrmap

    # def get_owning_halnode(self, owning_type: Type['HalBase'], halnode: Optional['HalBase'] = None) -> Optional[HalBase]:
    #     """Returns the HalAddrmapNode (halcpp class) owning this one.

    #     Parameters
    #     ----------
    #     owning_type: HalBase
    #         Owning class type, e.g., HalAddrmap, HalRegfile.
    #     halnode: Optional['HalBase']
    #         Base halnode from which to search. By default its this one.
    #     """
    #     # If this node is the first caller, start with this one.
    #     # Otherwise we are in a recursive search and use the given halnode.
    #     if halnode is None:
    #         halnode = self

    #     # Return this node if it corresponds to the searched one
    #     if isinstance(halnode, owning_type):
    #         halnode_owner = self
    #     # If top node is reached return None
    #     elif self.is_top_node:
    #         halnode_owner = None
    #     # Otherwise recursively search for it by passing the parent
    #     else:
    #         parent_node = self.get_parent()
    #         halnode_owner = self.get_owning_halnode(owning_type, parent_node)

    #     return halnode_owner

    def get_parent(self) -> Union['HalBase', None]:
        """Returns this node parent."""
        return self._parent

    @abstractmethod
    def get_template_line(self) -> str:
        """Returns the node C++ template line as a string. This method
        must be overloaded by the child class.

        This C++ string template (e.g., 'template<type MYVAR, ...>')

        Returns
        -------
        str
            C++ string template (e.g., 'template<type MYVAR, ...>') of the
            node type (e.g., reg, mem).
        """
        pass

    @abstractmethod
    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameters. This method must be
        overloaded by the child class.

        The parameters correspond to the template parameters returned
        by :func:`get_template_line`.

        Returns
        -------
        str
            C++ string template parameters.
        """
        pass
