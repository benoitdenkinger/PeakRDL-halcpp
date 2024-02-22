from typing import Optional, Iterator
import itertools

from systemrdl.node import Node, RootNode, AddrmapNode, MemNode, RegfileNode, RegNode, FieldNode, SignalNode,AddressableNode

class HalBaseNode(Node):
    """HAL node base class. This class inherits from the systemrdl Node class."""

    def __iter__(self):
        # Make this class iterable
        yield self

    @property
    def inst_name_hal(self) -> str:
        """Return the node name with the '_hal' suffix."""
        return super().inst_name.lower() + "_hal"

    @property
    def is_bus(self) -> bool:
        """Returns True if the HAL node is considered a bus (i.e., addrmap containing only addrmaps)."""
        return False

    def get_docstring(self) -> str:
        """Converts the node description into a C++ multi-line comment."""
        desc = "/*\n"
        if self.get_property('desc') is not None:
            for l in self.get_property('desc').splitlines():
                desc = desc + " * " + l + "\n"
            return desc + " */"
        return ""

    @staticmethod
    def _halfactory(inst: Node, env: 'RDLEnvironment', parent: Optional['Node']=None) -> Optional['Node']:
        """HAL node factory method adapted from systemrdl Node class."""
        if isinstance(inst, FieldNode):
            return HalFieldNode(inst)
        elif isinstance(inst, RegNode):
            return HalRegNode(inst)
        elif isinstance(inst, RegfileNode):
            return HalRegfileNode(inst)
        elif isinstance(inst, AddrmapNode):
            return HalAddrmapNode(inst)
        elif isinstance(inst, MemNode):
            return HalMemNode(inst)
        elif isinstance(inst, SignalNode):
            # Signals are not supported by this plugin
            return None
        else:
            print(f'ERROR: inst type {type(inst)} is not recognized')
            raise RuntimeError

    def halunrolled(self) -> Iterator['Node']:
        """HAL node unrolling method adapted from systemrdl Node class."""
        cls = type(self)
        if isinstance(self, AddressableNode) and self.is_array: # pylint: disable=no-member
            # Is an array. Yield a Node object for each instance
            range_list = [range(n) for n in self.array_dimensions] # pylint: disable=no-member
            for idxs in itertools.product(*range_list):
                N = cls(self)
                N.current_idx = idxs # type: ignore
                yield N
        else:
            # Not an array. Nothing to unroll
            yield cls(self.inst, self.env, self.parent)

    def _halchildren(self, unroll: bool=False, skip_not_present: bool=True, bus_offset: int=0) -> Iterator['Node']:
        """HAL children generator method adapted from systemrdl Node class."""
        for child in self.children():
            if skip_not_present:
                if not child.get_property('ispresent'):
                    # ispresent was explicitly set to False. Skip it
                    continue

            if unroll and isinstance(child, AddressableNode) and child.is_array:
                assert child.array_dimensions is not None
                # Unroll the array
                range_list = [range(n) for n in child.array_dimensions]
                for idxs in itertools.product(*range_list):
                    N = HalBaseNode._halfactory(child, self.env, self)
                    if N is None:
                        # This check is needed to skip Signal components (not supported)
                        continue
                    else:
                        N.current_idx = idxs  # type: ignore # pylint: disable=attribute-defined-outside-init
                        N.bus_offset = bus_offset
                        yield N
            else:
                N = HalBaseNode._halfactory(child, self.env, self)
                # This check is needed to skip Signal components (not supported)
                if N is None:
                    continue
                else:
                    N.bus_offset = bus_offset
                    yield N

    def children_of_type(self, children_type : 'Node'=Node, unroll: bool=False, skip_not_present: bool=True, skip_buses: bool=False, bus_offset: int=0) -> Iterator['Node']:
        for child in self._halchildren(unroll, skip_not_present, bus_offset):
            if isinstance(child, children_type):
                child_bus_offset = 0
                if skip_buses and child.is_bus:
                    child_bus_offset = bus_offset + child.address_offset
                    yield from child.children_of_type(children_type, unroll, skip_not_present, skip_buses, child_bus_offset)
                else:
                    yield child

    def haldescendants(self, descendants_type: 'Node'=Node, unroll: bool=False, skip_not_present: bool=True, in_post_order: bool=False, skip_buses: bool=False, bus_offset: int=0) -> Iterator['Node']:
        """HAL node descedant generator adapted from systemrdl Node class."""
        for child in self._halchildren(unroll, skip_not_present, bus_offset):
            if isinstance(child, descendants_type):
                child_bus_offset = 0
                if skip_buses and self.is_bus:
                    child_bus_offset = bus_offset + child.address_offset

                if in_post_order:
                    yield from child.haldescendants(descendants_type, unroll, skip_not_present, in_post_order, skip_buses, child_bus_offset)

                if not (skip_buses and child.is_bus):
                    yield child

                if not in_post_order:
                    yield from child.haldescendants(descendants_type, unroll, skip_not_present, in_post_order, skip_buses, child_bus_offset)


class HalFieldNode(HalBaseNode, FieldNode):
    def __init__(self, node: FieldNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

    @property
    def address_offset(self) -> int:
        # FieldNode does not have an address but to avoid extra check it returns 0
        return 0

    @property
    def cpp_access_type(self) -> str:
        """C++ access right template selection."""
        if self.is_sw_readable and self.is_sw_writable:
            return "FieldRW"
        elif self.is_sw_writable and not self.is_sw_readable:
            return "FieldWO"
        elif self.is_sw_readable:
            return "FieldRO"
        else:
            raise ValueError (f'Node field access rights are not found \
                              {self.inst.inst_name}')

    def get_enums(self):
        """Returns the enumeration(s) of a FieldNode.

        Inside an addrmap node, all enumerations must have a different name.
        The jinja template used to create the C++ header is filtering enumeration
        with already existing name.
        """
        encode = self.get_property('encode')
        if encode is not None:
            enum_cls_name = encode.type_name
            enum_strings = []
            enum_values = []
            enum_desc = []
            for k in encode.members:
                enum_strings.append(encode.members[k].name)
                enum_values.append(encode.members[k].value)
                enum_desc.append(encode.members[k].rdl_desc)

            const_width = max(enum_values).bit_length()

            return True, enum_cls_name, enum_strings, enum_values, enum_desc, const_width

        return False, None, None, None, None, None



class HalRegNode(HalBaseNode, RegNode):
    def __init__(self, node: RegNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        self.bus_offset = 0

    @property
    def cpp_access_type(self):
        """C++ access right template selection."""
        if self.has_sw_readable and self.has_sw_writable:
            return "RegRW"
        elif self.has_sw_writable and not self.has_sw_readable:
            return "RegWO"
        elif self.has_sw_readable:
            return "RegRO"
        assert False

    @property
    def address_offset(self) -> int:
        """Property adapted from systemrdl RegNode class to HalRegNode class."""
        if self.is_array and self.current_idx is None:
            return self.bus_offset + next(self.halunrolled()).address_offset # type: ignore
        else:
            return self.bus_offset + super().address_offset

    @property
    def width(self) -> int:
        return max([c.high for c in self.children_of_type(HalFieldNode)]) + 1

    def get_template_line(self) -> str:
        """Returns the class template string."""
        return f"template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, WIDTH, PARENT_TYPE>"


class HalRegfileNode(HalBaseNode, RegfileNode):
    def __init__(self, node: RegfileNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        self.bus_offset = 0

    @property
    def cpp_access_type(self):
        """C++ access right template selection.

        For RegfileNodes, the access rights are selected at lower
        levels (e.g., registers).
        """
        return "RegfileNode"

    @property
    def address_offset(self) -> int:
        """Property adapted from systemrdl RegNode class to HalRegNode class."""
        if self.is_array and self.current_idx is None:
            return self.bus_offset + next(self.halunrolled()).address_offset # type: ignore
        else:
            return self.bus_offset + super().address_offset

    def get_template_line(self) -> str:
        """Returns the class template string."""
        return f"template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, PARENT_TYPE>"


class HalMemNode(HalBaseNode, MemNode):
    def __init__(self, node: MemNode):
        # Use the system-RDL MemNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        self.bus_offset = 0

        # Memory component instantiation is limited for simplicity
        if self.parent is not None:
            for c in self.parent.children():
                if isinstance(c, AddressableNode):
                    assert c.inst == self.inst, (f"Addrmaps with anything else than "
                                             "one memory node is currently not allowed, "
                                             "it could be easily added")

    @property
    def address_offset(self) -> int:
        """Property adapted HalRegNode class."""
        return self.bus_offset + super().address_offset

    def get_template_line(self) -> str:
        """Returns the class template string."""
        return f"template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, SIZE, PARENT_TYPE>"


class HalAddrmapNode(HalBaseNode, AddrmapNode):
    def __init__(self, node: AddrmapNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)
        #: The bus offset is used for address offset correction when the --skip-buses option is used
        self.bus_offset = 0

    @property
    def is_top_node(self) -> bool:
        """Checks if this is the top node."""
        return isinstance(self.parent, RootNode)

    @property
    def address_offset(self) -> int:
        """Property adapted HalRegNode class."""
        return self.bus_offset + super().address_offset

    @property
    def is_bus(self) -> bool:
        """Check if addrmap contains only addrmap"""
        for child in self._halchildren():
            if not isinstance(child, HalAddrmapNode):
                return False
        return True

    def get_template_line(self) -> str:
        """Returns the class template string."""
        if self.is_top_node:
            # Parent is set to void by default for the top node
            return "template <uint32_t BASE, typename PARENT_TYPE=void>"
        return "template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the class template parameter string.

        These parameters must match the the template returned by :func:`get_template_line`.
        """
        return "<BASE, PARENT_TYPE>"

