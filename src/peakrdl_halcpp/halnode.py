from typing import Union, Any, Optional, Type, Iterator
from abc import ABC, abstractmethod, abstractproperty
import itertools
import inspect

from systemrdl.node import Node, RootNode, AddrmapNode, MemNode, RegfileNode, RegNode, FieldNode, AddressableNode
from systemrdl.component import Component, AddressableComponent, Signal, Field, Reg, Regfile, Mem, Addrmap

class HalBaseNode(Node):
    # This class should not have any init function
    # This class can inherit from Node and the derived class from this one inherit from advanced node (e.g., AddrmapNode)
    # because only Node class has an init function. If not, not sure this would work

    def __iter__(self):
        yield self

    @property
    def inst_name_hal(self) -> str:
        """Return the node name with the '_hal' suffix"""
        return super().inst_name.lower() + "_hal"

    def get_docstring(self) -> str:
        """Converts the node description into a C++ multi-line comment."""
        desc = "/*\n"
        if self.get_property('desc') is not None:
            for l in self.get_property('desc').splitlines():
                desc = desc + " * " + l + "\n"
            return desc + " */"
        return ""

    @staticmethod
    def _factory(inst: Component, env: 'RDLEnvironment', parent: Optional['Node']=None) -> Optional['Node']:

        if isinstance(inst, Field):
            return HalFieldNode(FieldNode(inst, env, parent))
        elif isinstance(inst, Reg):
            return HalRegNode(RegNode(inst, env, parent))
        elif isinstance(inst, Regfile):
            return HalRegfileNode(RegfileNode(inst, env, parent))
        elif isinstance(inst, Addrmap):
            return HalAddrmapNode(AddrmapNode(inst, env, parent))
        elif isinstance(inst, Mem):
            return HalMemNode(MemNode(inst, env, parent))
        elif isinstance(inst, Signal):
            # Signals are not supported by this plugin
            return None
        else:
            raise RuntimeError

    def unrolled(self) -> Iterator['Node']:
        cls = type(self.super())
        print('++++++++++++++ unrolled() ++++++++++++++')
        print(cls)
        if isinstance(self, AddressableNode) and self.is_array: # pylint: disable=no-member
            print('It is an array from unrolled()')
            # Is an array. Yield a Node object for each instance
            range_list = [range(n) for n in self.array_dimensions] # pylint: disable=no-member
            for idxs in itertools.product(*range_list):
                N = cls(self.inst, self.env, self.parent)
                N.current_idx = idxs # type: ignore
                yield N
        else:
            # not an array. Nothing to unroll
            print('Not an array from unrolled()')
            yield cls(self.inst, self.env, self.parent)

    def children(self, unroll: bool=False, skip_not_present: bool=True) -> Iterator['Node']:
        print('++++++++++++++ children() ++++++++++++++ ')
        for child_inst in self.inst.children:
            print(child_inst)
            if hasattr(child_inst, 'is_array'):
                print(f'Is this an array? {child_inst.is_array}')
            else:
                print('This node does not have is_array property')
            if skip_not_present:
                # Check if property ispresent == False
                if not child_inst.properties.get('ispresent', True):
                    # ispresent was explicitly set to False. Skip it
                    continue

            if unroll and isinstance(child_inst, AddressableComponent) and child_inst.is_array:
                assert child_inst.array_dimensions is not None
                # Unroll the array
                range_list = [range(n) for n in child_inst.array_dimensions]
                for idxs in itertools.product(*range_list):
                    N = HalBaseNode._factory(child_inst, self.env, self)
                    # This check is needed to skip Signal components  (not supported)
                    if N is None:
                        print('Signal detected and avoided')
                        continue
                    else:
                        N.current_idx = idxs  # type: ignore # pylint: disable=attribute-defined-outside-init
                        yield N
            else:
                N = HalBaseNode._factory(child_inst, self.env, self)
                # This check is needed to skip Signal components (not supported)
                if N is None:
                    continue
                else:
                    yield N

    def children_of_type(self, children_type : 'Node', unroll: bool=False, skip_not_present: bool=True) -> Iterator['Node']:
        for child in self.children(unroll, skip_not_present):
            if isinstance(child, children_type):
                yield child

    def descendants(self, unroll: bool=False, skip_not_present: bool=True, in_post_order: bool=False) -> Iterator['Node']:
        for child in self.children(unroll, skip_not_present):
            if in_post_order:
                yield from child.descendants(unroll, skip_not_present, in_post_order)

            yield child

            if not in_post_order:
                yield from child.descendants(unroll, skip_not_present, in_post_order)

    def descendants_of_type(self, descendants_type : 'Node', unroll: bool=False, skip_not_present: bool=True, in_post_order: bool=False) -> Iterator['Node']:

        for child in self.descendants(unroll, skip_not_present):
            if isinstance(child, descendants_type):
                if in_post_order:
                    yield from child.descendants_of_type(descendants_type, unroll, skip_not_present, in_post_order)

                yield child

                if not in_post_order:
                    yield from child.descendants_of_type(descendants_type, unroll, skip_not_present, in_post_order)


class HalFieldNode(FieldNode):
    def __init__(self, node: FieldNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)
        # TODO add as a parameter?
        self.bus_offset = 0

    @property
    def cpp_access_type(self) -> str:
        if self.is_sw_readable and self.is_sw_writable:
            return "FieldRW"
        elif self.is_sw_writable and not self.is_sw_readable:
            return "FieldWO"
        elif self.is_sw_readable:
            return "FieldRO"
        else:
            raise ValueError (f'Node field access rights are not found \
                              {self.inst.inst_name}')

    @property
    def address_offset(self) -> int:
        return self.bus_offset + super().address_offset

    def get_enums(self):
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
        # TODO add as a parameter?
        self.bus_offset = 0

    @property
    def cpp_access_type(self):
        if self.has_sw_readable and self.has_sw_writable:
            return "RegRW"
        elif self.has_sw_writable and not self.has_sw_readable:
            return "RegWO"
        elif self.has_sw_readable:
            return "RegRO"
        assert False

    @property
    def address_offset(self) -> int:
        offset = self.bus_offset
        print('++++++++ HalRegNode address_offset call ++++++++')
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # print('caller name:', calframe[1][3])
        # stack = inspect.stack()
        # print("Call stack leading up to some_method():")
        # print(*stack, sep='\n')
        print(f'Node {type(self.inst)}')
        print(f'is_array: {self.is_array}')
        if self.is_array:
            for inst in self.unrolled():
                print('Loop over the array')
                print(inst)
                # offset += inst.address_offset
        else:
            print('No loop, not an array')
            # offset += super().address_offset
        print(f'address_offset: {offset}')
        return offset
        # if self.is_array:
        #     return self.bus_offset + next(self.unrolled()).address_offset # type: ignore
        # else:
        #     return self.bus_offset + super().address_offset

    @property
    def width(self) -> int:
        return max([c.high for c in self.children_of_type(HalFieldNode)]) + 1

    def get_template_line(self) -> str:
        return f"template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        return "<BASE, WIDTH, PARENT_TYPE>"


class HalRegfileNode(HalBaseNode, RegfileNode):
    def __init__(self, node: RegfileNode):
        # Use the system-RDL AddrmapNode class initialization
        super().__init__(node.inst, node.env, node.parent)
        # TODO add as a parameter?
        self.bus_offset = 0

    @property
    def cpp_access_type(self):
        return "RegfileNode"

    @property
    def address_offset(self) -> int:
        return self.bus_offset + super().address_offset

    def get_template_line(self) -> str:
        return f"template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        return "<BASE, PARENT_TYPE>"


class HalMemNode(HalBaseNode, MemNode):
    def __init__(self, node: MemNode):
        # Use the system-RDL MemNode class initialization
        super().__init__(node.inst, node.env, node.parent)

        # # Can this be removed?
        # if self.parent is not None:
        #     for c in self.parent.children():
        #         if isinstance(c, AddressableNode):
        #             assert c == self.inst, (f"Addrmaps with anything else than "
        #                                      "one memory node is currently not allowed, "
        #                                      "it could be easily added")

    def get_template_line(self) -> str:
        return f"template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        return "<BASE, SIZE, PARENT_TYPE>"


class HalAddrmapNode(HalBaseNode, AddrmapNode):
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
