#ifndef RTW_HEADER_AbstractFuelControl_M1_acc_private_h_
#define RTW_HEADER_AbstractFuelControl_M1_acc_private_h_
#include "rtwtypes.h"
#include "multiword_types.h"
#include "zero_crossing_types.h"
#include "AbstractFuelControl_M1_acc.h"
#if !defined(ss_VALIDATE_MEMORY)
#define ss_VALIDATE_MEMORY(S, ptr)     if(!(ptr)) {\
    ssSetErrorStatus(S, RT_MEMORY_ALLOCATION_ERROR);\
    }
#endif
#if !defined(rt_FREE)
#if !defined(_WIN32)
#define rt_FREE(ptr)     if((ptr) != (NULL)) {\
    free((ptr));\
    (ptr) = (NULL);\
    }
#else
#define rt_FREE(ptr)     if((ptr) != (NULL)) {\
    free((void *)(ptr));\
    (ptr) = (NULL);\
    }
#endif
#endif
#ifndef __RTW_UTFREE__
extern void * utMalloc ( size_t ) ; extern void utFree ( void * ) ;
#endif
boolean_T AbstractFuelControl_M1_acc_rt_TDelayUpdateTailOrGrowBuf ( int_T *
bufSzPtr , int_T * tailPtr , int_T * headPtr , int_T * lastPtr , real_T
tMinusDelay , real_T * * uBufPtr , boolean_T isfixedbuf , boolean_T
istransportdelay , int_T * maxNewBufSzPtr ) ; real_T
AbstractFuelControl_M1_acc_rt_VTDelayfindtDInterpolate ( real_T x , real_T *
uBuf , int_T bufSz , int_T head , int_T tail , int_T * pLast , real_T t ,
real_T tStart , boolean_T discrete , boolean_T minorStepAndTAtLastMajorOutput
, real_T initOutput , real_T * appliedDelay ) ; extern real_T look2_binlxpw (
real_T u0 , real_T u1 , const real_T bp0 [ ] , const real_T bp1 [ ] , const
real_T table [ ] , const uint32_T maxIndex [ ] , uint32_T stride ) ;
#endif
