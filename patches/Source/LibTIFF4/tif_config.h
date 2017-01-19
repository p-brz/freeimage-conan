#ifndef TIF_CONFIG_H
#define TIF_CONFIG_H

/* Define to 1 if you have the <assert.h> header file. */
#ifndef NO_ASSERT_H
#define HAVE_ASSERT_H 1
#endif

/* Define to 1 if you have the <fcntl.h> header file. */
#ifndef NO_FCNTL_H
#define HAVE_FCNTL_H 1
#endif

/* Define as 0 or 1 according to the floating point format suported by the
   machine */
#ifndef NO_IEEEFP
#define HAVE_IEEEFP 1
#endif

/* Define to 1 if you have the <string.h> header file. */
#ifndef NO_STRING_H
#define HAVE_STRING_H 1
#endif

/* Define to 1 if you have the <sys/types.h> header file. */
#ifndef NO_SYS_TYPES_H
#define HAVE_SYS_TYPES_H 1
#endif

/* Define to 1 if you have the <io.h> header file. */
#ifndef NO_IO_H
#define HAVE_IO_H 1
#endif

/* Define to 1 if you have the <search.h> header file. */
#ifndef NO_SEARCH_H
#define HAVE_SEARCH_H 1
#endif

/* Define to 1 if you have the `setmode' function. */
#ifndef NO_SETMODE
#define HAVE_SETMODE 1
#endif

/* Define to 1 if you have the `memmove' function. */
#ifndef NO_MEMMOVE
#define HAVE_MEMMOVE 1
#endif

/* Define to 1 if you have the `memset' function. */
#ifndef NO_MEMSET
#define HAVE_MEMSET 1
#endif

/* Signed 32-bit type formatter */
#define TIFF_INT32_FORMAT "%d"

/* Unsigned 32-bit type formatter */
#define TIFF_UINT32_FORMAT "%u"

/* Signed 64-bit type formatter */
#define TIFF_INT64_FORMAT "%ld"

/* Unsigned 64-bit type formatter */
#define TIFF_UINT64_FORMAT "%lu"

/* Pointer difference type formatter */
#define TIFF_PTRDIFF_FORMAT "%ld"

/* Signed size type formatter */
#define TIFF_SSIZE_FORMAT "%ld"

/* 
-----------------------------------------------------------------------
Byte order
-----------------------------------------------------------------------
*/

/*
Define WORDS_BIGENDIAN to 1 if your processor stores words with the most
significant byte first (like Motorola and SPARC, unlike Intel).
Some versions of gcc may have BYTE_ORDER or __BYTE_ORDER defined
If your big endian system isn't being detected, add an OS specific check
*/
#if (defined(BYTE_ORDER) && BYTE_ORDER==BIG_ENDIAN) || \
	(defined(__BYTE_ORDER) && __BYTE_ORDER==__BIG_ENDIAN) || \
	defined(__BIG_ENDIAN__)
/* Set the native cpu bit order (FILLORDER_LSB2MSB or FILLORDER_MSB2LSB) */
#define HOST_FILLORDER FILLORDER_MSB2LSB
/* Native cpu byte order: 1 if big-endian (Motorola) or 0 if little-endian (Intel) */
#define WORDS_BIGENDIAN 1
/* Native cpu byte order: 1 if big-endian (Motorola) or 0 if little-endian (Intel) */
#define HOST_BIGENDIAN 1
#else
/* Set the native cpu bit order (FILLORDER_LSB2MSB or FILLORDER_MSB2LSB) */
#define HOST_FILLORDER FILLORDER_LSB2MSB
/* Native cpu byte order: 1 if big-endian (Motorola) or 0 if little-endian (Intel) */
#undef WORDS_BIGENDIAN
/* Native cpu byte order: 1 if big-endian (Motorola) or 0 if little-endian (Intel) */
#undef HOST_BIGENDIAN
#endif // BYTE_ORDER

#ifdef _WIN32
#define snprintf _snprintf
#define lfind _lfind
#endif // _WIN32

/* Define to `__inline__' or `__inline' if that's what the C compiler
   calls it, or to nothing if 'inline' is not supported under any name.  */
#ifndef __cplusplus
# ifndef inline
#  define inline __inline
# endif
#endif


#endif // TIF_CONFIG_H
