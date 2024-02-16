from typing import List, Type, Dict, Union
import getpass
import datetime

from systemrdl.node import AddrmapNode
from systemrdl import RDLListener, RDLWalker

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

class MyListener(RDLListener):
    def __init__(self, module_extended: List = [str]):
        # Init the RDLListener class
        super().__init__()

    def generate_hal(self, node: AddrmapNode):

        print("+++++++++++++++++++++++++++++++")
        RDLWalker().walk(node, self)
        print("+++++++++++++++++++++++++++++++")

        return node

    def enter_Addrmap(self, node):
        print("Entering addrmap", node.get_path())

    def exit_Addrmap(self, node):
        print("Exiting addrmap", node.get_path())

    def enter_Reg(self, node):
        print("Entering register", node.get_path())

    def exit_Reg(self, node):
        print("Exiting register", node.get_path())

    def enter_Field(self, node):
        print("Entering field", node.get_path())

    def exit_Field(self, node):
        print("Exiting field", node.get_path())

def build_hierarchy_new(node: AddrmapNode) -> AddrmapNode:

        print("+++++++++++++++++++++++++++++++")
        RDLWalker().walk(node, MyListener())
        print("+++++++++++++++++++++++++++++++")

        return node
