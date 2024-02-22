#ifndef _ARCH_IO_H_
#define _ARCH_IO_H_

#include <cstdint>

/**
 * @brief A class representing memory I/O operations.
 *
 * This class provides static methods for reading and writing 32-bit values from/to memory.
 */
class MemIoNode
{
public:
    /**
     * @brief Read a 32-bit value from the specified memory address.
     *
     * @param addr The memory address from which to read.
     * @return uint32_t The value read from the memory address.
     */
    static inline uint32_t read32(uint32_t addr) { return *(volatile uint32_t *)addr; }

    /**
     * @brief Write a 32-bit value to the specified memory address.
     *
     * @param addr The memory address to which to write.
     * @param val The value to write to the memory address.
     */
    static inline void write32(uint32_t addr, uint32_t val) { *(volatile uint32_t *)addr = val; }
};

/**
 * @brief A class representing architecture-specific I/O operations.
 *
 * This class inherits from MemIoNode and can be used for architecture-specific I/O operations.
 */
class ArchIoNode : public MemIoNode
{
public:
    // No additional member functions or data members are defined in this class.
};

#endif // !_ARCH_IO_H_
