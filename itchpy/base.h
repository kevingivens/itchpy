#ifndef ITCHPY_BASE_H_
#  define ITCHPY_BASE_H_

#if !defined(ITCHPY_ASSERT)
#include <assert.h>
#define ITCHPY_ASSERT assert
#elif defined(ITCHPY_ASSERT_INCLUDE)
// Include file with forward declaration
#include ITCHPY_ASSERT_INCLUDE
#endif

/// @file
namespace itchpy {

template<typename T> T EndianSwap(T t) {
  #if defined(_MSC_VER)
    #define ITCHPY_BYTESWAP16 _byteswap_ushort
    #define ITCHPY_BYTESWAP32 _byteswap_ulong
    #define ITCHPY_BYTESWAP64 _byteswap_uint64
  #elif defined(__ICCARM__)
    #define ITCHPY_BYTESWAP16 __REV16
    #define ITCHPY_BYTESWAP32 __REV
    #define ITCHPY_BYTESWAP64(x) \
       ((__REV(static_cast<uint32_t>(x >> 32U))) | (static_cast<uint64_t>(__REV(static_cast<uint32_t>(x)))) << 32U)
  #else
    #if defined(__GNUC__) && __GNUC__ * 100 + __GNUC_MINOR__ < 408 && !defined(__clang__)
      // __builtin_bswap16 was missing prior to GCC 4.8.
      #define ITCHPY_BYTESWAP16(x) \
        static_cast<uint16_t>(__builtin_bswap32(static_cast<uint32_t>(x) << 16))
    #else
      #define ITCHPY_BYTESWAP16 __builtin_bswap16
    #endif
    #define ITCHPY_BYTESWAP32 __builtin_bswap32
    #define ITCHPY_BYTESWAP64 __builtin_bswap64
  #endif
  if (sizeof(T) == 1) {   // Compile-time if-then's.
    return t;
  } else if (sizeof(T) == 2) {
    union { T t; uint16_t i; } u = { t };
    u.i = ITCHPY_BYTESWAP16(u.i);
    return u.t;
  } else if (sizeof(T) == 4) {
    union { T t; uint32_t i; } u = { t };
    u.i = ITCHPY_BYTESWAP32(u.i);
    return u.t;
  } else if (sizeof(T) == 8) {
    union { T t; uint64_t i; } u = { t };
    u.i = ITCHPY_BYTESWAP64(u.i);
    return u.t;
  } else {
    ITCHPY_ASSERT(0);
    return t;
  }
}
}  // namespace itchpy
#endif  // ITCHPY_BASE_H_