from typing import TYPE_CHECKING

from systemrdl.node import FieldNode

from .halbase import HalBase

if TYPE_CHECKING:
    from .halreg import HalReg


class HalField(HalBase):
    """HAL wrapper class for PeakRDL FieldNode.

    Class methods:

    - :func:`get_template_line`
    - :func:`get_cls_tmpl_spec`
    """

    def __init__(self, node: FieldNode, parent: 'HalReg'):
        super().__init__(node, parent)

        # print(f'node addr_offset: {node.addr_offset}')
        self.enums = self.get_enums(node) # type: ignore

    @property
    def width(self) -> int:
        return self._node.width

    @property
    def cpp_access_type(self) -> str:
        out = ""
        if self._node.is_sw_readable and self._node.is_sw_writable:
            return "FieldRW"
        elif self._node.is_sw_writable and not self._node.is_sw_readable:
            return "FieldWO"
        elif self._node.is_sw_readable:
            return "FieldRO"
        else:
            raise ValueError (f'Node field access rights are not found \
                              {self._node.inst_name}')

    @property
    def addr_offset(self) -> int:
        assert False, "FieldNode has no offset"

    def get_template_line(self) -> str:
        assert False, "You should not create a class from a FieldNode"

    def get_cls_tmpl_params(self, just_tmpl=False) -> str:
        assert False, "You should not extend FieldNode classes"

    def get_enums(self, node):
        encode = node.get_property('encode')
        if encode is not None:
            enum_cls_name = encode.__name__
            print(f'Field {node.inst_name} has enum')
            print(f'Type of enum {type(encode)}')
            print(f'Type of enum.members {type(encode.members)}')
            print(f'enum.members {encode.members}')
            for k, v in encode.members.items():
                print(f'{k}: {v}')
                print(f'Enum members.name: {encode.members[k].name}')
                print(f'Enum members.value: {encode.members[k].value}')
                print(f'Enum members.rdl_desc: {encode.members[k].rdl_desc}')
            print('---------------------------------')
            for item in encode.members.items():
                print(f'item: {item}')
            print('---------------------------------')
            for idx, item in enumerate(encode.members.items()):
                print(f'item[{idx}]: {item}')
                print(f'Type of item[{idx}]: {type(item)}')


