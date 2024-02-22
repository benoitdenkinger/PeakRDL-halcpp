#ifndef _ARRAY_NODES_H__
#define _ARRAY_NODES_H__

#include <type_traits>
#include <cstdint>
#include <utility>
#include <array>
#include "halcpp_utils.h"

namespace halcpp
{

    // Credit for this solution goes to https://www.reddit.com/user/IyeOnline/

    /**
     * @brief Maps the given index value to the corresponding index within a specified range.
     *
     * @tparam IDX The index value to map.
     * @tparam DIM The dimension size.
     * @return constexpr uint32_t The mapped index value.
     */
    template <int32_t IDX, uint32_t DIM>
    constexpr uint32_t map_index()
    {
        return IDX == -1 ? DIM - 1 : IDX;
    }

    /**
     * @brief Calculates the linear index given a multidimensional index and dimensions.
     *
     * @tparam STRIDE The stride value.
     * @tparam N_DIM The number of dimensions.
     * @param nd_index The multidimensional index.
     * @param dimensions The dimensions array.
     * @return constexpr uint32_t The calculated linear index.
     */
    template <uint32_t STRIDE, std::size_t N_DIM>
    constexpr uint32_t linear_index(std::array<uint32_t, N_DIM> nd_index, std::array<uint32_t, N_DIM> dimensions)
    {
        uint32_t result = 0;
        uint32_t product = 1;
        for (std::size_t i = 0; i < N_DIM; ++i)
        {
            result += nd_index[N_DIM - i - 1] * STRIDE * product;
            product *= dimensions[N_DIM - i - 1];
        }
        return result;
    }

    /**
     * @brief Checks if the given index is valid for a given size.
     *
     * @param index The index value.
     * @param size The size.
     * @return constexpr bool Returns true if the index is valid, otherwise false.
     */
    constexpr bool valid_index(int32_t index, uint32_t size)
    {
        return index >= -1 && index < static_cast<int32_t>(size);
    }

    /**
     * @brief A class representing an array of register nodes.
     *
     * @tparam REG_T The type of register node template.
     * @tparam BASE The base relative address.
     * @tparam WIDTH The width of the register.
     * @tparam STRIDE The stride value.
     * @tparam PARENT_TYPE The parent type.
     * @tparam Extents The extents of the array dimensions.
     */
    template <template <uint32_t B, uint32_t W, typename P> typename REG_T,
              uint32_t BASE, uint32_t WIDTH, uint32_t STRIDE, typename PARENT_TYPE, uint32_t... Extents>
    class RegArrayNode
    {
    private:
        static constexpr uint32_t Dimensions = sizeof...(Extents);
        static_assert(Dimensions > 0);

    public:
        static constexpr uint32_t stride = STRIDE;

        /**
         * @brief Returns the register node at the specified indices.
         *
         * @tparam Indices The indices for each dimension.
         * @return auto The register node.
         */
        template <int32_t... Indices>
        auto at()
        {
            // Ensure that the number of provided indices matches the number of dimensions
            static_assert(sizeof...(Indices) == Dimensions);
            // Ensure that all provided indices are valid for their respective dimensions
            static_assert((valid_index(Indices, Extents) && ...));

            // Calculate the offset based on the provided indices and dimensions
            constexpr uint32_t offset = BASE + linear_index<STRIDE>(std::array{map_index<Indices, Extents>()...},
                                                                    std::array{Extents...});
            // Return the register node at the calculated offset
            return REG_T<offset, WIDTH, PARENT_TYPE>();
        }

        /**
         * @brief Gets the size of the specified dimension.
         *
         * @tparam IDX The index of the dimension.
         * @return constexpr uint32_t The size of the dimension.
         */
        template <uint32_t IDX>
        constexpr uint32_t get_dim()
        {
            static_assert(IDX < Dimensions, "Index out of bounds");

            constexpr std::array<uint32_t, Dimensions> dimensions_array = {Extents...};
            return dimensions_array[IDX];
        }
    };

    /**
     * @brief A class representing an array of register file nodes.
     *
     * @tparam REGFILE_T The type of register file node template.
     * @tparam BASE The base address.
     * @tparam STRIDE The stride value.
     * @tparam PARENT_TYPE The parent type.
     * @tparam Extents The extents of the array dimensions.
     */
    template <template <uint32_t B, typename P> typename REGFILE_T,
              uint32_t BASE, uint32_t STRIDE, typename PARENT_TYPE, uint32_t... Extents>
    class RegfileArrayNode
    {
    private:
        static constexpr uint32_t Dimensions = sizeof...(Extents);
        static_assert(Dimensions > 0);

    public:
        static constexpr uint32_t stride = STRIDE;

        /**
         * @brief Returns the register file node at the specified indices.
         *
         * @tparam Indices The indices for each dimension.
         * @return auto The register file node.
         */
        template <int32_t... Indices>
        auto at()
        {
            // Ensure that the number of provided indices matches the number of dimensions
            static_assert(sizeof...(Indices) == Dimensions);
            // Ensure that all provided indices are valid for their respective dimensions
            static_assert((valid_index(Indices, Extents) && ...));
            // Calculate the offset based on the provided indices and dimensions
            constexpr uint32_t offset = BASE + linear_index<STRIDE>(std::array{map_index<Indices, Extents>()...},
                                                                    std::array{Extents...});
            // Return the register file node at the calculated offset
            return REGFILE_T<offset, PARENT_TYPE>();
        }

        /**
         * @brief Gets the size of the specified dimension.
         *
         * @tparam IDX The index of the dimension.
         * @return constexpr uint32_t The size of the dimension.
         */
        template <uint32_t IDX>
        constexpr uint32_t get_dim()
        {
            static_assert(IDX < Dimensions, "Index out of bounds");

            constexpr std::array<uint32_t, Dimensions> dimensions_array = {Extents...};
            return dimensions_array[IDX];
        }
    };

    namespace __halcpp_utils
    {

        /**
         * @brief Helper function for iterating over integer sequences.
         *
         * @tparam T The type of integer.
         * @tparam inds The integer sequence.
         * @tparam F The function to apply to each integer.
         * @param f The function to apply.
         */
        template <class T, T... inds, class F>
        constexpr void loop(std::integer_sequence<T, inds...>, F &&f)
        {
            (f(std::integral_constant<T, inds>{}), ...);
        }

    }

    /**
     * @brief Function for iterating over integer sequences.
     *
     * @tparam T The type of integer.
     * @tparam count The number of integers in the sequence.
     * @tparam F The function to apply to each integer.
     * @param f The function to apply.
     */
    template <class T, T count, class F>
    constexpr void loop(F &&f)
    {
        __halcpp_utils::loop(std::make_integer_sequence<T, count>{}, std::forward<F>(f));
    }

}

#endif // !_ARRAY_NODES_H__
