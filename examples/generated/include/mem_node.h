#ifndef _MEM_NODE_H_
#define _MEM_NODE_H_

#include <stdint.h>
#include <type_traits>

namespace halcpp
{

    /**
     * @brief A class template representing a memory node.
     *
     * @tparam BASE The base relative address of the memory node.
     * @tparam SIZE The size (in bytes) of the memory node.
     * @tparam PARENT_TYPE The parent type of the memory node.
     */
    template <uint32_t BASE, uint32_t SIZE, typename PARENT_TYPE>
    class MemNode
    {
    public:
        static constexpr uint32_t base = BASE;
        static constexpr uint32_t size = SIZE;

        /**
         * @brief Get the value at a specified address.
         */
        inline uint32_t get(const uint32_t addr) { return PARENT_TYPE::get(addr + BASE); }

        /**
         * @brief Set the value at a specified address.
         */
        inline void set(const uint32_t addr, uint32_t val) { PARENT_TYPE::set(addr + BASE, val); }

        /**
         * @brief Get the absolute address of the memory node.
         */
        static constexpr uint32_t get_abs_addr() { return PARENT_TYPE().get_abs_addr() + BASE; }

        /**
         * @brief Get the size (in bytes) of the memory node.
         */
        constexpr uint32_t get_size() { return SIZE; }
    };
}

#endif // !_MEM_NODE_H_
