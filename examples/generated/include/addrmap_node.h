#ifndef _ADDRMAP_NODE_H_
#define _ADDRMAP_NODE_H_

#include "arch_io.h"
#include <cstdint>

/**
 * @brief A class template representing an address map node.
 *
 * @tparam BASE The base relative address of the address map node.
 * @tparam PARENT_TYPE The parent type of the address map node.
 */
template <uint32_t BASE, typename PARENT_TYPE = void>
class AddrmapNode
{
public:
    /**
     * @brief Get the absolute address of the address map node.
     */
    static constexpr uint32_t get_abs_addr() { return PARENT_TYPE().get_abs_addr() + BASE; }

    /**
     * @brief Get the value at a specified address within the address map node.
     */
    static inline uint32_t get(const uint32_t addr) { return PARENT_TYPE::get(addr + BASE); }

    /**
     * @brief Set the value at a specified address within the address map node.
     */
    static inline void set(const uint32_t addr, uint32_t val)
    {
        PARENT_TYPE::set(addr + BASE, val);
    }
};

/**
 * @brief Specialization for the top hierarchy address map node.
 *
 * The top node does not have a parent. Instead, it inherits ArchIoNode,
 * which implements memory access for the architecture.
 *
 * @tparam BASE The base address of the top hierarchy address map node.
 */
template <uint32_t BASE>
class AddrmapNode<BASE, void> : public ArchIoNode
{
public:
    /**
     * @brief Get the absolute address of the top hierarchy address map node.
     */
    static constexpr uint32_t get_abs_addr() { return BASE; }

    /**
     * @brief Set the value at a specified address within the top hierarchy address map node.
     */
    static inline void set(uint32_t addr, uint32_t val)
    {
        ArchIoNode::write32(addr + BASE, val);
    }

    /**
     * @brief Get the value at a specified address within the top hierarchy address map node.
     */
    static inline uint32_t get(uint32_t addr) { return ArchIoNode::read32(addr + BASE); }
};

#endif // !_ADDRMAP_NODE_H_
