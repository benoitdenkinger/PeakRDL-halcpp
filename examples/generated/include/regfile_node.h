#ifndef _REGFILE_NODE_H_
#define _REGFILE_NODE_H_

#include <cstdint>

namespace halcpp
{

    /**
     * @brief A class template representing a register file node.
     *
     * @tparam BASE The base relative address of the register file node.
     * @tparam PARENT_TYPE The parent type of the register file node.
     */
    template <uint32_t BASE, typename PARENT_TYPE>
    class RegfileNode
    {
    public:
        /**
         * @brief Get the absolute address of the register file node.
         */
        static constexpr uint32_t get_abs_addr() { return PARENT_TYPE().get_abs_addr() + BASE; }

        /**
         * @brief Get the value at a specified address within the register file node.
         */
        static inline uint32_t get(const uint32_t addr) { return PARENT_TYPE::get(addr + BASE); }

        /**
         * @brief Set the value at a specified address within the register file node.
         */
        static inline void set(const uint32_t addr, uint32_t val)
        {
            PARENT_TYPE::set(addr + BASE, val);
        }
    };

};

#endif // !_REGFILE_NODE_H_
