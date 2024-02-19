// Generated with PeakRD-halcpp : https://github.com/Risto97/PeakRDL-halcpp
// By user: risto at: 2023-08-03 09:18:43

#ifndef __ATXMEGA_SPI_HAL_H_
#define __ATXMEGA_SPI_HAL_H_

#include <stdint.h>
#include "include/halcpp_base.h"
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wundefined-var-template"
#endif

namespace atxmega_spi_nm
{

    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class CTRL : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        static halcpp::FieldRW<0, 1, CTRL<BASE, WIDTH, PARENT_TYPE>> PRESCALER;
        static halcpp::FieldRW<2, 3, CTRL<BASE, WIDTH, PARENT_TYPE>> MODE;
        static halcpp::FieldRW<4, 4, CTRL<BASE, WIDTH, PARENT_TYPE>> MASTER;
        static halcpp::FieldRW<5, 5, CTRL<BASE, WIDTH, PARENT_TYPE>> DORD;
        static halcpp::FieldRW<6, 6, CTRL<BASE, WIDTH, PARENT_TYPE>> ENABLE;
        static halcpp::FieldRW<7, 7, CTRL<BASE, WIDTH, PARENT_TYPE>> CLK2X;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };

    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class INTCTRL : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        static halcpp::FieldRW<0, 1, INTCTRL<BASE, WIDTH, PARENT_TYPE>> INTLVL;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };

    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class STATUS : public halcpp::RegRO<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        static halcpp::FieldRO<6, 6, STATUS<BASE, WIDTH, PARENT_TYPE>> WRCOL;
        static halcpp::FieldRO<7, 7, STATUS<BASE, WIDTH, PARENT_TYPE>> IF;
    };

    /*
     * The DATA register is used for sending and receiving data.
     * Writing to the register initiates the data transmission, and the byte
     * written to the register will be shifted out on the SPI output line.
     * Reading the register causes the shift register receive buffer to be read,
     * returning the last byte successfully received
     */
    template <uint32_t BASE, uint32_t WIDTH, typename PARENT_TYPE>
    class DATA : public halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>
    {
    public:
        static halcpp::FieldWO<0, 7, DATA<BASE, WIDTH, PARENT_TYPE>> WDATA;
        static halcpp::FieldRO<0, 7, DATA<BASE, WIDTH, PARENT_TYPE>> RDATA;

        using halcpp::RegRW<BASE, WIDTH, PARENT_TYPE>::operator=;
    };

}

/*
 * Register description of Atmel XMEGA AU's SPI controller
 * Transcribed from original manual as an example exercise:
 * http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-8331-8-and-16-bit-AVR-Microcontroller-XMEGA-AU_Manual.pdf
 */
template <uint32_t BASE, typename PARENT_TYPE = void>
class ATXMEGA_SPI_HAL : public AddrmapNode<BASE, PARENT_TYPE>
{
public:
    static atxmega_spi_nm::CTRL<0x0, 8, ATXMEGA_SPI_HAL<BASE, PARENT_TYPE>> CTRL;
    static atxmega_spi_nm::INTCTRL<0x1, 2, ATXMEGA_SPI_HAL<BASE, PARENT_TYPE>> INTCTRL;
    static atxmega_spi_nm::STATUS<0x2, 8, ATXMEGA_SPI_HAL<BASE, PARENT_TYPE>> STATUS;
    static atxmega_spi_nm::DATA<0x3, 8, ATXMEGA_SPI_HAL<BASE, PARENT_TYPE>> DATA;
};

#endif