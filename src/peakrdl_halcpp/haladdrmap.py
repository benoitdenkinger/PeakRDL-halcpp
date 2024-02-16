from typing import List

from systemrdl.node import AddrmapNode, RegNode, RootNode, MemNode, RegfileNode

from .halbase import HalBase
from .halreg import HalReg, HalArrReg
from .halregfile import HalRegfile, HalArrRegfile
from .halmem import HalMem


class HalAddrmap(HalBase):
    """HAL wrapper class for PeakRDL AddrmapNode.

    Class methods:
    - :func:`get_regs`
    - :func:`get_mems`
    - :func:`get_addrmaps`
    - :func:`get_regfiles`
    - :func:`remove_buses`
    - :func:`is_bus`
    - :func:`get_regfiles_regs`
    - :func:`get_template_line`
    - :func:`get_cls_tmpl_spec`
    - :func:`get_addrmaps_recursive`
    """

    def __init__(self,
                 node: AddrmapNode,
                 parent: 'HalAddrmap|None' = None,
                 bus_offset: int = 0
                 ):
        super().__init__(node, parent)

        # Does it have to be a parameter (now only modified by remove_buses function)?
        self.bus_offset = bus_offset

        # Check that top level HAL has no parent but RootNode
        assert (self._parent == None) == isinstance(
            self._node.parent, RootNode)

        # Traverse all the node hierarchy and extract of the different nodes:
        # RegNode -> HalReg or HalArrReg
        self.regs = self.get_regs()
        # Regfile -> HalRegfile or HalArrRegfile
        self.regfiles = self.get_regfiles()
        # MemNode -> HalMem
        self.mems = self.get_mems()
        # AddrMapNode -> HalAddrMap
        self.addrmaps = self.get_addrmaps()
        # This will be populated when the HAL file is generated
        self.enums = {}  # type: ignore

    @property
    def is_top_node(self) -> bool:
        """Check if this is the top node."""
        return self._parent == None

    # @property
    # def inst_name(self) -> str:
    #     """Return the node name with the '_hal' suffix"""
    #     return self.inst_name + "_hal"

    @property
    def cpp_access_type(self) -> str:
        assert False, "cpp_access_type not defined (is it needed?)"

    @property
    def addr_offset(self) -> int:
        """Returns the node address offset relative to its parent."""
        return self.bus_offset + self._node.address_offset

    def get_regs(self) -> List[HalReg]:
        """Traverses the node hierarchy and extracts the RegNodes and the
        array of RegNodes.

        Returns
        -------
        List[HalReg]
            List of RegNode objects each encapsulated in a HalReg (or HalArrReg) object.
        """
        regs = []
        for c in self._node.children():
            if isinstance(c, RegNode):
                reg = HalArrReg(c, self) if c.is_array else HalReg(c, self)
                regs.append(reg)
        return regs

    def get_mems(self) -> List[HalMem]:
        """Traverses the node hierarchy and extracts the MemNodes.

        Returns
        -------
        List[HalMem]
            List of MemNode objects each encapsulated in a HalMem object.
        """
        return [HalMem(c, self) for c in self._node.children() if isinstance(c, MemNode)]

    def get_addrmaps(self) -> List['HalAddrmap']:
        """Traverses the node hierarchy and extracts the AddrmapNode.

        Returns
        -------
        List[HalAddrmap]
            List of AddrmapNode objects each encapsulated in a HalAddrmap object.
        """
        return [HalAddrmap(c, self) for c in self._node.children() if isinstance(c, AddrmapNode)]

    def get_regfiles(self) -> List[HalRegfile]:
        """Traverses the node hierarchy and extracts the RegfileNodes and the
        array of RegfileNodes.

        Returns
        -------
        List[HalRegfile]
            List of RegfileNode objects each encapsulated in a HalRegfile (or HalArrRegfile) object.
        """
        regfiles: List[HalRegfile] = []
        for c in self._node.children():
            if isinstance(c, RegfileNode):
                if c.is_array:
                    regfile = HalArrRegfile(c, self)
                else:
                    regfile = HalRegfile(c, self)  # type: ignore

                regfiles.append(regfile)

        return regfiles

    def remove_buses(self):
        """Removes buses (i.e., addrmaps containing only addrmaps).

        The address offset of the current AddrMapNode is added to each of
        its child AddrMapNodes and the parent node of the current AddrMapNode is
        passed to its child AddrMapNodes.
        """
        remove_list = []
        for c in self.addrmaps:
            c.remove_buses()
            if c.is_bus():
                # Traverse the child AddrMapNodes and add to them the address
                # offset of the current AddrMapNode and update their parent
                for subc in c.addrmaps:
                    subc.bus_offset += c.addr_offset
                    subc._parent = self
                remove_list.append(c)
                # Extend the addrmaps list with the removed node one
                self.addrmaps.extend(c.addrmaps)

        [self.addrmaps.remove(c) for c in remove_list]

    def is_bus(self) -> bool:
        """Checks if the addrmap is a bus.

        Returns
        -------
        bool
            Returns True if the addrmap is a bus (i.e., addrmaps containing only addrmaps).
        """
        if len(self.regs) == 0 and len(self.mems) == 0 and len(self.regfiles) == 0:
            return True
        return False

    def get_regfiles_regs(self) -> List[HalReg]:
        """Extracts the registers from the regfiles.

        Returns
        -------
            List[HalReg]
                List of registers (HalReg) contained in the node regfiles.
        """
        regs = []
        for regfile in self.regfiles:
            regs.extend(regfile.regs)
        return regs

    def get_template_line(self) -> str:
        """Returns the HAL C++ template for AddrmapNode class.

        Returns
        -------
            str
                C++ template structure for AddrmapNode class.
        """
        if self.is_top_node:
            # Parent is set to void by default for the top node
            return "template <uint32_t BASE, typename PARENT_TYPE=void>"
        return "template <uint32_t BASE, typename PARENT_TYPE>"

    def get_cls_tmpl_params(self) -> str:
        """Returns the HAL template parameters for class object reference.

        The structure must matched the template returned by :func:`get_template_line`.

        Returns
        -------
            str
                C++ template parameters.
        """
        return "<BASE, PARENT_TYPE>"

    def get_addrmaps_recursive(self) -> List['HalAddrmap']:
        """Recursively fetch the HalAddrmap nodes into a list.

        Gets the AddrMapNode hierarchy of the SystemRDL description.
        Here is a pseudo-SystemRDL code example for an basic SoC design.

        ::

            addrmap mySoC {
                addrmap myMem0 @ 0x40000000
                addrmap mySubsystem @ 0x44000000 {
                    addrmap myPeriph0 @ 0x00001000
                    addrmap myPeriph1 @ 0x00002000
                }
                addrmap myMem1 @ 0x41000000
                ...
            }

        Called on the top node (i.e., mySoC) this function returns:

        [mySoC, myMem0, mySubsystem, myPeriph0, myPeriph1, myMem1]

        where each element is a HalAddrmap object. Only the top node
        insert its own reference (i.e., mySoC) at the beginning.

        Returns
        -------
        List[HalAddrmap]
            A list of all HalAddrmap nodes contained within this HalAddrmap node.
        """
        addrmaps = self.addrmaps.copy()
        for c in self.addrmaps:
            addrmaps.extend(c.get_addrmaps_recursive())
        # Top node insert its own reference, why?
        if self.is_top_node:
            addrmaps.insert(0, self)
        return addrmaps
