#include "AbstractFuelControl_M1_acc.h"
#include "mwmathutil.h"
#include <float.h>
#include "rtwtypes.h"
#include "AbstractFuelControl_M1_acc_private.h"
#include "multiword_types.h"
#include "simstruc_types.h"
#include <stdio.h>
#include "slexec_vm_simstruct_bridge.h"
#include "slexec_vm_zc_functions.h"
#include "slexec_vm_lookup_functions.h"
#include "slsv_diagnostic_codegen_c_api.h"
#include "simtarget/slSimTgtMdlrefSfcnBridge.h"
#include "simstruc.h"
#include "fixedpoint.h"
#define CodeFormat S-Function
#define AccDefine1 Accelerator_S-Function
#include "simtarget/slAccSfcnBridge.h"
#ifndef __RTW_UTFREE__  
extern void * utMalloc ( size_t ) ; extern void utFree ( void * ) ;
#endif
boolean_T AbstractFuelControl_M1_acc_rt_TDelayUpdateTailOrGrowBuf ( int_T *
bufSzPtr , int_T * tailPtr , int_T * headPtr , int_T * lastPtr , real_T
tMinusDelay , real_T * * uBufPtr , boolean_T isfixedbuf , boolean_T
istransportdelay , int_T * maxNewBufSzPtr ) { int_T testIdx ; int_T tail = *
tailPtr ; int_T bufSz = * bufSzPtr ; real_T * tBuf = * uBufPtr + bufSz ;
real_T * xBuf = ( NULL ) ; int_T numBuffer = 2 ; if ( istransportdelay ) {
numBuffer = 3 ; xBuf = * uBufPtr + 2 * bufSz ; } testIdx = ( tail < ( bufSz -
1 ) ) ? ( tail + 1 ) : 0 ; if ( ( tMinusDelay <= tBuf [ testIdx ] ) && !
isfixedbuf ) { int_T j ; real_T * tempT ; real_T * tempU ; real_T * tempX = (
NULL ) ; real_T * uBuf = * uBufPtr ; int_T newBufSz = bufSz + 1024 ; if (
newBufSz > * maxNewBufSzPtr ) { * maxNewBufSzPtr = newBufSz ; } tempU = (
real_T * ) utMalloc ( numBuffer * newBufSz * sizeof ( real_T ) ) ; if ( tempU
== ( NULL ) ) { return ( false ) ; } tempT = tempU + newBufSz ; if (
istransportdelay ) tempX = tempT + newBufSz ; for ( j = tail ; j < bufSz ; j
++ ) { tempT [ j - tail ] = tBuf [ j ] ; tempU [ j - tail ] = uBuf [ j ] ; if
( istransportdelay ) tempX [ j - tail ] = xBuf [ j ] ; } for ( j = 0 ; j <
tail ; j ++ ) { tempT [ j + bufSz - tail ] = tBuf [ j ] ; tempU [ j + bufSz -
tail ] = uBuf [ j ] ; if ( istransportdelay ) tempX [ j + bufSz - tail ] =
xBuf [ j ] ; } if ( * lastPtr > tail ) { * lastPtr -= tail ; } else { *
lastPtr += ( bufSz - tail ) ; } * tailPtr = 0 ; * headPtr = bufSz ; utFree (
uBuf ) ; * bufSzPtr = newBufSz ; * uBufPtr = tempU ; } else { * tailPtr =
testIdx ; } return ( true ) ; } real_T
AbstractFuelControl_M1_acc_rt_VTDelayfindtDInterpolate ( real_T x , real_T *
uBuf , int_T bufSz , int_T head , int_T tail , int_T * pLast , real_T t ,
real_T tStart , boolean_T discrete , boolean_T minorStepAndTAtLastMajorOutput
, real_T initOutput , real_T * appliedDelay ) { int_T n , k ; real_T f ;
int_T kp1 ; real_T tminustD , tL , tR , uD , uL , uR , fU ; real_T * tBuf =
uBuf + bufSz ; real_T * xBuf = uBuf + 2 * bufSz ; if (
minorStepAndTAtLastMajorOutput ) { if ( * pLast == head ) { * pLast = ( *
pLast == 0 ) ? bufSz - 1 : * pLast - 1 ; } head = ( head == 0 ) ? bufSz - 1 :
head - 1 ; } if ( x <= 1 ) { return initOutput ; } k = * pLast ; n = 0 ; for
( ; ; ) { n ++ ; if ( n > bufSz ) break ; if ( x - xBuf [ k ] > 1.0 ) { if (
k == head ) { int_T km1 ; f = ( x - 1.0 - xBuf [ k ] ) / ( x - xBuf [ k ] ) ;
tminustD = ( 1.0 - f ) * tBuf [ k ] + f * t ; km1 = k - 1 ; if ( km1 < 0 )
km1 = bufSz - 1 ; tL = tBuf [ km1 ] ; tR = tBuf [ k ] ; uL = uBuf [ km1 ] ;
uR = uBuf [ k ] ; break ; } kp1 = k + 1 ; if ( kp1 == bufSz ) kp1 = 0 ; if (
x - xBuf [ kp1 ] <= 1.0 ) { f = ( x - 1.0 - xBuf [ k ] ) / ( xBuf [ kp1 ] -
xBuf [ k ] ) ; tL = tBuf [ k ] ; tR = tBuf [ kp1 ] ; uL = uBuf [ k ] ; uR =
uBuf [ kp1 ] ; tminustD = ( 1.0 - f ) * tL + f * tR ; break ; } k = kp1 ; }
else { if ( k == tail ) { f = ( x - 1.0 ) / xBuf [ k ] ; if ( discrete ) {
return ( uBuf [ tail ] ) ; } kp1 = k + 1 ; if ( kp1 == bufSz ) kp1 = 0 ;
tminustD = ( 1 - f ) * tStart + f * tBuf [ k ] ; tL = tBuf [ k ] ; tR = tBuf
[ kp1 ] ; uL = uBuf [ k ] ; uR = uBuf [ kp1 ] ; break ; } k = k - 1 ; if ( k
< 0 ) k = bufSz - 1 ; } } * pLast = k ; if ( tR == tL ) { fU = 1.0 ; } else {
fU = ( tminustD - tL ) / ( tR - tL ) ; } if ( discrete ) { uD = ( fU > ( 1.0
- fU ) ) ? uR : uL ; } else { uD = ( 1.0 - fU ) * uL + fU * uR ; } *
appliedDelay = t - tminustD ; return uD ; } real_T look2_binlxpw ( real_T u0
, real_T u1 , const real_T bp0 [ ] , const real_T bp1 [ ] , const real_T
table [ ] , const uint32_T maxIndex [ ] , uint32_T stride ) { real_T
fractions [ 2 ] ; real_T frac ; real_T yL_0d0 ; real_T yL_0d1 ; uint32_T
bpIndices [ 2 ] ; uint32_T bpIdx ; uint32_T iLeft ; uint32_T iRght ; if ( u0
<= bp0 [ 0U ] ) { iLeft = 0U ; frac = ( u0 - bp0 [ 0U ] ) / ( bp0 [ 1U ] -
bp0 [ 0U ] ) ; } else if ( u0 < bp0 [ maxIndex [ 0U ] ] ) { bpIdx = maxIndex
[ 0U ] >> 1U ; iLeft = 0U ; iRght = maxIndex [ 0U ] ; while ( iRght - iLeft >
1U ) { if ( u0 < bp0 [ bpIdx ] ) { iRght = bpIdx ; } else { iLeft = bpIdx ; }
bpIdx = ( iRght + iLeft ) >> 1U ; } frac = ( u0 - bp0 [ iLeft ] ) / ( bp0 [
iLeft + 1U ] - bp0 [ iLeft ] ) ; } else { iLeft = maxIndex [ 0U ] - 1U ; frac
= ( u0 - bp0 [ maxIndex [ 0U ] - 1U ] ) / ( bp0 [ maxIndex [ 0U ] ] - bp0 [
maxIndex [ 0U ] - 1U ] ) ; } fractions [ 0U ] = frac ; bpIndices [ 0U ] =
iLeft ; if ( u1 <= bp1 [ 0U ] ) { iLeft = 0U ; frac = ( u1 - bp1 [ 0U ] ) / (
bp1 [ 1U ] - bp1 [ 0U ] ) ; } else if ( u1 < bp1 [ maxIndex [ 1U ] ] ) {
bpIdx = maxIndex [ 1U ] >> 1U ; iLeft = 0U ; iRght = maxIndex [ 1U ] ; while
( iRght - iLeft > 1U ) { if ( u1 < bp1 [ bpIdx ] ) { iRght = bpIdx ; } else {
iLeft = bpIdx ; } bpIdx = ( iRght + iLeft ) >> 1U ; } frac = ( u1 - bp1 [
iLeft ] ) / ( bp1 [ iLeft + 1U ] - bp1 [ iLeft ] ) ; } else { iLeft =
maxIndex [ 1U ] - 1U ; frac = ( u1 - bp1 [ maxIndex [ 1U ] - 1U ] ) / ( bp1 [
maxIndex [ 1U ] ] - bp1 [ maxIndex [ 1U ] - 1U ] ) ; } bpIdx = iLeft * stride
+ bpIndices [ 0U ] ; yL_0d0 = table [ bpIdx ] ; yL_0d0 += ( table [ bpIdx +
1U ] - yL_0d0 ) * fractions [ 0U ] ; bpIdx += stride ; yL_0d1 = table [ bpIdx
] ; return ( ( ( table [ bpIdx + 1U ] - yL_0d1 ) * fractions [ 0U ] + yL_0d1
) - yL_0d0 ) * frac + yL_0d0 ; } void rt_ssGetBlockPath ( SimStruct * S ,
int_T sysIdx , int_T blkIdx , char_T * * path ) { _ssGetBlockPath ( S ,
sysIdx , blkIdx , path ) ; } void rt_ssSet_slErrMsg ( void * S , void * diag
) { SimStruct * castedS = ( SimStruct * ) S ; if ( !
_ssIsErrorStatusAslErrMsg ( castedS ) ) { _ssSet_slErrMsg ( castedS , diag )
; } else { _ssDiscardDiagnostic ( castedS , diag ) ; } } void
rt_ssReportDiagnosticAsWarning ( void * S , void * diag ) {
_ssReportDiagnosticAsWarning ( ( SimStruct * ) S , diag ) ; } void
rt_ssReportDiagnosticAsInfo ( void * S , void * diag ) {
_ssReportDiagnosticAsInfo ( ( SimStruct * ) S , diag ) ; } static void
mdlOutputs ( SimStruct * S , int_T tid ) { B_AbstractFuelControl_M1_T * _rtB
; DW_AbstractFuelControl_M1_T * _rtDW ; P_AbstractFuelControl_M1_T * _rtP ;
PrevZCX_AbstractFuelControl_M1_T * _rtZCE ; X_AbstractFuelControl_M1_T * _rtX
; real_T ratio ; real_T rtb_B_13_0_0 ; real_T rtb_B_15_13_0 ; int32_T isHit ;
real32_T rtb_B_10_0_0 ; real32_T rtb_B_4_0_0 ; uint32_T numCycles ; int8_T
rtAction ; int8_T rtPrevAction ; boolean_T rtb_B_10_3_0 ; ZCEventType zcEvent
; _rtDW = ( ( DW_AbstractFuelControl_M1_T * ) ssGetRootDWork ( S ) ) ; _rtZCE
= ( ( PrevZCX_AbstractFuelControl_M1_T * ) _ssGetPrevZCSigState ( S ) ) ;
_rtX = ( ( X_AbstractFuelControl_M1_T * ) ssGetContStates ( S ) ) ; _rtP = (
( P_AbstractFuelControl_M1_T * ) ssGetModelRtp ( S ) ) ; _rtB = ( (
B_AbstractFuelControl_M1_T * ) _ssGetModelBlockIO ( S ) ) ; _rtB -> B_15_0_0
= _rtX -> Integrator_CSTATE_m ; _rtB -> B_15_1_0 = _rtP -> P_8 * _rtB ->
B_15_0_0 ; _rtB -> B_15_2_0 = 0.0 ; _rtB -> B_15_2_0 += _rtP -> P_10 * _rtX
-> Throttledelay_CSTATE ; _rtB -> B_15_3_0 = _rtB -> B_15_2_0 + _rtB ->
B_15_2_0_c ; if ( ssIsModeUpdateTimeStep ( S ) ) { _rtDW -> theta090_MODE =
_rtB -> B_15_3_0 >= _rtP -> P_11 ? 1 : _rtB -> B_15_3_0 > _rtP -> P_12 ? 0 :
- 1 ; } _rtB -> B_15_4_0 = _rtDW -> theta090_MODE == 1 ? _rtP -> P_11 : _rtDW
-> theta090_MODE == - 1 ? _rtP -> P_12 : _rtB -> B_15_3_0 ;
ssCallAccelRunBlock ( S , 15 , 5 , SS_CALL_MDL_OUTPUTS ) ; if (
ssIsModeUpdateTimeStep ( S ) ) { _rtDW -> EngineSpeed9001100_MODE = ( (
ExternalUPtrs_AbstractFuelControl_M1_T * ) ssGetU ( S ) ) -> EngineSpeed >=
_rtP -> P_13 ? 1 : ( ( ExternalUPtrs_AbstractFuelControl_M1_T * ) ssGetU ( S
) ) -> EngineSpeed > _rtP -> P_14 ? 0 : - 1 ; } _rtB -> B_15_6_0 = _rtDW ->
EngineSpeed9001100_MODE == 1 ? _rtP -> P_13 : _rtDW ->
EngineSpeed9001100_MODE == - 1 ? _rtP -> P_14 : ( (
ExternalUPtrs_AbstractFuelControl_M1_T * ) ssGetU ( S ) ) -> EngineSpeed ;
_rtB -> B_15_7_0 = _rtP -> P_15 * _rtB -> B_15_6_0 ; isHit = ssIsSampleHit (
S , 1 , 0 ) ; if ( isHit != 0 ) { _rtDW -> AFSensorFaultInjection_MODE = (
ssGetTaskTime ( S , 1 ) >= _rtP -> P_16 ) ; if ( _rtDW ->
AFSensorFaultInjection_MODE == 1 ) { _rtB -> B_15_8_0 = _rtP -> P_18 ; } else
{ _rtB -> B_15_8_0 = _rtP -> P_17 ; } } if ( _rtB -> B_15_8_0 >= _rtP -> P_19
) { _rtB -> B_15_9_0 = _rtB -> B_15_3_0_b ; } else { _rtB -> B_15_9_0 = _rtB
-> B_15_1_0 ; } _rtB -> B_15_10_0 = _rtP -> P_20 * _rtB -> B_15_9_0 ; _rtB ->
B_15_11_0 = ( real32_T ) _rtB -> B_15_7_0 ; _rtB -> B_15_12_0 = ( real32_T )
_rtB -> B_15_4_0 ; _rtB -> B_15_14_0 = _rtX -> p00543bar_CSTATE ; _rtB ->
B_15_15_0 = _rtB -> B_15_14_0 / _rtB -> B_15_1_0_k ; _rtB -> B_15_16_0 = 1.0
/ _rtB -> B_15_14_0 * _rtB -> B_15_1_0_k ; if ( ssIsModeUpdateTimeStep ( S )
) { _rtB -> B_15_17_0 = _rtB -> B_15_15_0 ; _rtDW -> MinMax_MODE = 0 ; if ( (
_rtB -> B_15_15_0 != _rtB -> B_15_15_0 ) || ( _rtB -> B_15_16_0 < _rtB ->
B_15_15_0 ) ) { _rtB -> B_15_17_0 = _rtB -> B_15_16_0 ; _rtDW -> MinMax_MODE
= 1 ; } _rtDW -> Switch_Mode = ( _rtB -> B_15_17_0 >= _rtP -> P_22 ) ; } else
{ _rtB -> B_15_17_0 = _rtB -> B_15_15_0 ; if ( _rtDW -> MinMax_MODE == 1 ) {
_rtB -> B_15_17_0 = _rtB -> B_15_16_0 ; } } if ( _rtDW -> Switch_Mode ) {
ratio = _rtB -> B_15_17_0 - _rtB -> B_15_17_0 * _rtB -> B_15_17_0 ; if (
ratio < 0.0 ) { ratio = - muDoubleScalarSqrt ( - ratio ) ; } else { ratio =
muDoubleScalarSqrt ( ratio ) ; } _rtB -> B_14_0_0 = 2.0 * ratio ; _rtB ->
B_15_19_0 = _rtB -> B_14_0_0 ; } else { _rtB -> B_15_19_0 = _rtB ->
B_15_4_0_p ; } _rtB -> B_15_20_0 = _rtB -> B_15_1_0_k - _rtB -> B_15_14_0 ;
isHit = ssIsSampleHit ( S , 1 , 0 ) ; if ( isHit != 0 ) { if ( _rtB ->
B_15_20_0 > 0.0 ) { _rtDW -> flowdirection_MODE = 1 ; } else if ( _rtB ->
B_15_20_0 < 0.0 ) { _rtDW -> flowdirection_MODE = - 1 ; } else { _rtDW ->
flowdirection_MODE = 0 ; } _rtB -> B_15_21_0 = _rtDW -> flowdirection_MODE ;
} _rtB -> B_15_22_0 = ( ( ( 2.821 - 0.05231 * _rtB -> B_15_4_0 ) + 0.10299 *
_rtB -> B_15_4_0 * _rtB -> B_15_4_0 ) - 0.00063 * _rtB -> B_15_4_0 * _rtB ->
B_15_4_0 * _rtB -> B_15_4_0 ) * _rtB -> B_15_19_0 * _rtB -> B_15_21_0 ; _rtB
-> B_15_23_0 = _rtP -> P_23 * _rtB -> B_15_22_0 ; _rtB -> B_15_24_0 = (
real32_T ) _rtB -> B_15_23_0 ; _rtB -> B_15_25_0 = ( real32_T ) _rtB ->
B_15_10_0 ; isHit = ssIsSampleHit ( S , 1 , 0 ) ; if ( isHit != 0 ) { _rtDW
-> Pwon_MODE = ( ssGetTaskTime ( S , 1 ) >= _rtP -> P_0 ) ; if ( _rtDW ->
Pwon_MODE == 1 ) { rtb_B_13_0_0 = _rtP -> P_2 ; } else { rtb_B_13_0_0 = _rtP
-> P_1 ; } } isHit = ssIsSampleHit ( S , 2 , 0 ) ; if ( isHit != 0 ) {
rtb_B_15_13_0 = ssGetTaskTime ( S , 2 ) ; if ( ssGetTNextWasAdjusted ( S , 2
) != 0 ) { _rtDW -> nextTime = _ssGetVarNextHitTime ( S , 0 ) ; } if ( _rtDW
-> justEnabled != 0 ) { _rtDW -> justEnabled = 0 ; if ( rtb_B_15_13_0 >= _rtP
-> P_6 ) { ratio = ( rtb_B_15_13_0 - _rtP -> P_6 ) / _rtP -> P_4 ; numCycles
= ( uint32_T ) muDoubleScalarFloor ( ratio ) ; if ( muDoubleScalarAbs ( (
real_T ) ( numCycles + 1U ) - ratio ) < DBL_EPSILON * ratio ) { numCycles ++
; } _rtDW -> numCompleteCycles = numCycles ; ratio = ( ( real_T ) numCycles *
_rtP -> P_4 + _rtP -> P_6 ) + _rtP -> P_5 * _rtP -> P_4 / 100.0 ; if (
rtb_B_15_13_0 < ratio ) { _rtDW -> currentValue = 1 ; _rtDW -> nextTime =
ratio ; } else { _rtDW -> currentValue = 0 ; _rtDW -> nextTime = ( real_T ) (
numCycles + 1U ) * _rtP -> P_4 + _rtP -> P_6 ; } } else { _rtDW ->
numCompleteCycles = _rtP -> P_6 != 0.0 ? - 1 : 0 ; _rtDW -> currentValue = 0
; _rtDW -> nextTime = _rtP -> P_6 ; } } else if ( _rtDW -> nextTime <=
rtb_B_15_13_0 ) { if ( _rtDW -> currentValue == 1 ) { _rtDW -> currentValue =
0 ; _rtDW -> nextTime = ( real_T ) ( _rtDW -> numCompleteCycles + 1LL ) *
_rtP -> P_4 + _rtP -> P_6 ; } else { _rtDW -> numCompleteCycles ++ ; _rtDW ->
currentValue = 1 ; _rtDW -> nextTime = ( _rtP -> P_5 * _rtP -> P_4 * 0.01 + (
real_T ) _rtDW -> numCompleteCycles * _rtP -> P_4 ) + _rtP -> P_6 ; } }
_ssSetVarNextHitTime ( S , 0 , _rtDW -> nextTime ) ; if ( _rtDW ->
currentValue == 1 ) { _rtB -> B_13_1_0 = _rtP -> P_3 ; } else { _rtB ->
B_13_1_0 = 0.0 ; } } _rtDW -> engine_speed = _rtB -> B_15_11_0 ;
vm_WriteLocalDSMNoIdx ( S , _rtDW -> dsmIdx_f , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/DataStoreWrite"
, 0 ) ; _rtDW -> throttle_angle = _rtB -> B_15_12_0 ; vm_WriteLocalDSMNoIdx (
S , _rtDW -> dsmIdx_m , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/DataStoreWrite3"
, 0 ) ; _rtDW -> throttle_flow = _rtB -> B_15_24_0 ; vm_WriteLocalDSMNoIdx (
S , _rtDW -> dsmIdx_h , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/DataStoreWrite1"
, 0 ) ; _rtDW -> airbyfuel_meas = _rtB -> B_15_25_0 ; vm_WriteLocalDSMNoIdx (
S , _rtDW -> dsmIdx_ha , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/DataStoreWrite2"
, 0 ) ; isHit = ssIsSampleHit ( S , 1 , 0 ) ; if ( ( isHit != 0 ) &&
ssIsModeUpdateTimeStep ( S ) ) { zcEvent = rt_ZCFcn ( RISING_ZERO_CROSSING ,
& _rtZCE -> fuel_controller_pwon_Trig_ZCE , rtb_B_13_0_0 ) ; if ( zcEvent !=
NO_ZCEVENT ) { _rtDW -> controller_mode = ( _rtP -> P_87 != 0.0F ) ;
vm_WriteLocalDSMNoIdx ( S , _rtDW -> dsmIdx_l , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_pwon/DataStoreWrite1"
, 0 ) ; _rtDW -> commanded_fuel = _rtP -> P_88 ; vm_WriteLocalDSMNoIdx ( S ,
_rtDW -> dsmIdx , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_pwon/DataStoreWrite"
, 0 ) ; if ( ssIsMajorTimeStep ( S ) != 0 ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ;
ssSetContTimeOutputInconsistentWithStateAtMajorStep ( S ) ; } _rtDW ->
airbyfuel_ref = _rtP -> P_89 ; vm_WriteLocalDSMNoIdx ( S , _rtDW -> dsmIdx_e
, ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_pwon/DataStoreWrite2"
, 0 ) ; if ( ssIsMajorTimeStep ( S ) != 0 ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ;
ssSetContTimeOutputInconsistentWithStateAtMajorStep ( S ) ; } _rtDW ->
fuel_controller_pwon_SubsysRanBC = 4 ; } zcEvent = rt_ZCFcn (
RISING_ZERO_CROSSING , & _rtZCE -> fuel_controller_mode_10ms_Trig_ZCE , _rtB
-> B_13_1_0 ) ; if ( zcEvent != NO_ZCEVENT ) { vm_ReadLocalDSMNoIdx ( S ,
_rtDW -> dsmIdx_ha , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_mode_10ms/DataStoreRead2"
, 0 ) ; isHit = ssIsSampleHit ( S , 1 , 0 ) ; if ( isHit != 0 ) { _rtB ->
B_9_2_0 = ( ( _rtDW -> airbyfuel_meas <= _rtB -> B_9_0_0 ) || _rtDW ->
UnitDelay_DSTATE ) ; } _rtB -> B_7_2_0 = _rtDW -> UnitDelay2_DSTATE + _rtP ->
P_82 ; _rtB -> B_7_6_0 = ( ( _rtB -> B_7_2_0 >= _rtP -> P_83 ) || _rtDW ->
UnitDelay1_DSTATE_e ) ; rtb_B_10_3_0 = ! _rtB -> B_7_6_0 ;
vm_ReadLocalDSMNoIdx ( S , _rtDW -> dsmIdx_m , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_mode_10ms/DataStoreRead4"
, 0 ) ; isHit = ssIsSampleHit ( S , 1 , 0 ) ; if ( isHit != 0 ) { if ( _rtDW
-> UnitDelay1_DSTATE_a ) { rtb_B_4_0_0 = _rtB -> B_8_0_0 ; } else {
rtb_B_4_0_0 = _rtB -> B_8_2_0 ; } _rtB -> B_8_2_0_f = ( _rtDW ->
throttle_angle >= rtb_B_4_0_0 ) ; } _rtDW -> controller_mode = ( _rtB ->
B_9_2_0 || rtb_B_10_3_0 || _rtB -> B_8_2_0_f ) ; vm_WriteLocalDSMNoIdx ( S ,
_rtDW -> dsmIdx_l , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_mode_10ms/DataStoreWrite"
, 0 ) ; if ( _rtB -> B_7_6_0 && _rtB -> B_8_2_0_f ) { _rtDW -> airbyfuel_ref
= _rtP -> P_79 ; } else { _rtDW -> airbyfuel_ref = _rtP -> P_80 ; }
vm_WriteLocalDSMNoIdx ( S , _rtDW -> dsmIdx_e , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_mode_10ms/DataStoreWrite1"
, 0 ) ; if ( ssIsMajorTimeStep ( S ) != 0 ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ;
ssSetContTimeOutputInconsistentWithStateAtMajorStep ( S ) ; } isHit =
ssIsSampleHit ( S , 1 , 0 ) ; if ( isHit != 0 ) { _rtDW -> UnitDelay_DSTATE =
_rtB -> B_9_2_0 ; } _rtDW -> UnitDelay2_DSTATE = _rtB -> B_7_2_0 ; _rtDW ->
UnitDelay1_DSTATE_e = _rtB -> B_7_6_0 ; isHit = ssIsSampleHit ( S , 1 , 0 ) ;
if ( isHit != 0 ) { _rtDW -> UnitDelay1_DSTATE_a = _rtB -> B_8_2_0_f ; }
_rtDW -> fuel_controller_mode_10ms_SubsysRanBC = 4 ; } zcEvent = rt_ZCFcn (
RISING_ZERO_CROSSING , & _rtZCE -> fuel_controller_10ms_Trig_ZCE , _rtB ->
B_13_1_0 ) ; if ( zcEvent != NO_ZCEVENT ) { vm_ReadLocalDSMNoIdx ( S , _rtDW
-> dsmIdx_h , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_10ms/DataStoreRead"
, 0 ) ; rtb_B_4_0_0 = _rtDW -> throttle_flow ; vm_ReadLocalDSMNoIdx ( S ,
_rtDW -> dsmIdx_f , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_10ms/DataStoreRead1"
, 0 ) ; rtb_B_10_0_0 = ( ( _rtDW -> UnitDelay1_DSTATE_d * _rtDW ->
engine_speed * _rtP -> P_66 + _rtP -> P_65 ) + _rtDW -> UnitDelay1_DSTATE_d *
_rtDW -> UnitDelay1_DSTATE_d * _rtDW -> engine_speed * _rtP -> P_67 ) + _rtDW
-> engine_speed * _rtDW -> engine_speed * _rtDW -> UnitDelay1_DSTATE_d * _rtP
-> P_68 ; _rtB -> B_1_13_0 = ( rtb_B_4_0_0 - rtb_B_10_0_0 ) * _rtP -> P_70 *
_rtP -> P_64 + _rtDW -> UnitDelay1_DSTATE_d ; vm_ReadLocalDSMNoIdx ( S ,
_rtDW -> dsmIdx_e , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_10ms/DataStoreRead4"
, 0 ) ; rtb_B_4_0_0 = _rtDW -> airbyfuel_ref ; rtb_B_10_0_0 /= _rtDW ->
airbyfuel_ref ; vm_ReadLocalDSMNoIdx ( S , _rtDW -> dsmIdx_l , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_10ms/DataStoreRead3"
, 0 ) ; rtb_B_10_3_0 = _rtDW -> controller_mode ; vm_ReadLocalDSMNoIdx ( S ,
_rtDW -> dsmIdx_ha , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_10ms/DataStoreRead2"
, 0 ) ; _rtB -> B_4_8_0 = ! rtb_B_10_3_0 ; if ( _rtB -> B_4_8_0 ) {
rtb_B_4_0_0 = _rtDW -> airbyfuel_meas - rtb_B_4_0_0 ; _rtB -> B_2_6_0 = _rtP
-> P_73 * rtb_B_4_0_0 * _rtP -> P_71 + _rtDW -> UnitDelay1_DSTATE ; _rtB ->
B_2_7_0 = _rtP -> P_72 * rtb_B_4_0_0 + _rtB -> B_2_6_0 ; _rtDW ->
feedback_PI_controller_SubsysRanBC = 4 ; } if ( rtb_B_10_3_0 ) { rtb_B_4_0_0
= _rtB -> B_4_1_0 ; } else { rtb_B_4_0_0 = _rtB -> B_4_0_0 + _rtB -> B_2_7_0
; if ( rtb_B_4_0_0 > _rtP -> P_62 ) { rtb_B_4_0_0 = _rtP -> P_62 ; } else if
( rtb_B_4_0_0 < _rtP -> P_63 ) { rtb_B_4_0_0 = _rtP -> P_63 ; } } rtb_B_4_0_0
*= rtb_B_10_0_0 ; if ( rtb_B_4_0_0 > _rtP -> P_75 ) { _rtDW -> commanded_fuel
= _rtP -> P_75 ; } else if ( rtb_B_4_0_0 < _rtP -> P_76 ) { _rtDW ->
commanded_fuel = _rtP -> P_76 ; } else { _rtDW -> commanded_fuel =
rtb_B_4_0_0 ; } vm_WriteLocalDSMNoIdx ( S , _rtDW -> dsmIdx , ( char_T * )
 "AbstractFuelControl_M1/Model 1/AF_Controller/fuel_controller/fuel_controller_10ms/DataStoreWrite"
, 0 ) ; if ( ssIsMajorTimeStep ( S ) != 0 ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ;
ssSetContTimeOutputInconsistentWithStateAtMajorStep ( S ) ; } _rtDW ->
UnitDelay1_DSTATE_d = _rtB -> B_1_13_0 ; if ( _rtB -> B_4_8_0 ) { _rtDW ->
UnitDelay1_DSTATE = _rtB -> B_2_6_0 ; } _rtDW ->
fuel_controller_10ms_SubsysRanBC = 4 ; } } vm_ReadLocalDSMNoIdx ( S , _rtDW
-> dsmIdx , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/DataStoreRead" , 0 ) ; _rtB ->
B_13_3_0 = _rtDW -> commanded_fuel ; vm_ReadLocalDSMNoIdx ( S , _rtDW ->
dsmIdx_l , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/DataStoreRead1" , 0 ) ; _rtB ->
B_13_4_0 = _rtDW -> controller_mode ; vm_ReadLocalDSMNoIdx ( S , _rtDW ->
dsmIdx_e , ( char_T * )
"AbstractFuelControl_M1/Model 1/AF_Controller/DataStoreRead2" , 0 ) ; _rtB ->
B_13_5_0 = _rtDW -> airbyfuel_ref ; _rtB -> B_15_27_0 = _rtX ->
Integrator_CSTATE_h ; _rtB -> B_15_28_0 = _rtB -> B_15_27_0 - _rtB ->
B_15_0_0 ; _rtB -> B_15_29_0 = _rtP -> P_25 * _rtB -> B_15_28_0 ; _rtB ->
B_15_31_0 = ( ( ( 0.08979 * _rtB -> B_15_14_0 * _rtB -> B_15_7_0 + - 0.366 )
- 0.0337 * _rtB -> B_15_7_0 * _rtB -> B_15_14_0 * _rtB -> B_15_14_0 ) +
0.0001 * _rtB -> B_15_14_0 * _rtB -> B_15_7_0 * _rtB -> B_15_7_0 ) * _rtP ->
P_96 ; _rtB -> B_15_32_0 = _rtP -> P_26 * _rtB -> B_15_7_0 ; _rtB ->
B_15_33_0 = _rtB -> B_15_31_0 / _rtB -> B_15_7_0 ; _rtB -> B_15_34_0 = _rtP
-> P_27 * _rtB -> B_15_33_0 ; _rtB -> B_15_36_0 = _rtP -> P_31 *
look2_binlxpw ( _rtB -> B_15_32_0 , _rtB -> B_15_34_0 , _rtP -> P_29 , _rtP
-> P_30 , _rtP -> P_28 , _rtP -> P_97 , 5U ) ; _rtB -> B_15_37_0 = _rtB ->
B_13_3_0 ; _rtB -> B_15_38_0 = _rtP -> P_32 * _rtB -> B_15_37_0 ; _rtB ->
B_15_39_0 = _rtB -> B_15_36_0 * _rtB -> B_15_38_0 ; _rtB -> B_15_40_0 = _rtX
-> Integrator_CSTATE_c ; _rtB -> B_15_42_0 = _rtP -> P_37 * look2_binlxpw (
_rtB -> B_15_32_0 , _rtB -> B_15_34_0 , _rtP -> P_35 , _rtP -> P_36 , _rtP ->
P_34 , _rtP -> P_98 , 5U ) ; _rtB -> B_15_43_0 = _rtB -> B_15_40_0 / _rtB ->
B_15_42_0 ; _rtB -> B_15_44_0 = _rtB -> B_15_39_0 + _rtB -> B_15_43_0 ; _rtB
-> B_15_45_0 = _rtB -> B_15_31_0 / _rtB -> B_15_44_0 ; { real_T * * uBuffer =
( real_T * * ) & _rtDW -> fuelsystemtransportdelay_PWORK . TUbufferPtrs [ 0 ]
; real_T simTime = ssGetT ( S ) ; real_T appliedDelay ; _rtB -> B_15_46_0 =
AbstractFuelControl_M1_acc_rt_VTDelayfindtDInterpolate ( ( (
X_AbstractFuelControl_M1_T * ) ssGetContStates ( S ) ) ->
fuelsystemtransportdelay_CSTATE , * uBuffer , _rtDW ->
fuelsystemtransportdelay_IWORK . CircularBufSize , _rtDW ->
fuelsystemtransportdelay_IWORK . Head , _rtDW ->
fuelsystemtransportdelay_IWORK . Tail , & _rtDW ->
fuelsystemtransportdelay_IWORK . Last , simTime , 0.0 , 0 , ( boolean_T ) (
ssIsMinorTimeStep ( S ) && ( ( * uBuffer + _rtDW ->
fuelsystemtransportdelay_IWORK . CircularBufSize ) [ _rtDW ->
fuelsystemtransportdelay_IWORK . Head ] == ssGetT ( S ) ) ) , _rtP -> P_39 ,
& appliedDelay ) ; } _rtB -> B_15_47_0 = _rtB -> B_15_46_0 - _rtB ->
B_15_27_0 ; _rtB -> B_15_48_0 = _rtP -> P_40 * _rtB -> B_15_47_0 ; _rtB ->
B_15_49_0 = _rtP -> P_41 * _rtB -> B_15_7_0 ; _rtB -> B_15_50_0 =
look2_binlxpw ( _rtB -> B_15_49_0 , _rtB -> B_15_34_0 , _rtP -> P_43 , _rtP
-> P_44 , _rtP -> P_42 , _rtP -> P_99 , 5U ) ; _rtB -> B_15_51_0 = _rtB ->
B_15_22_0 - _rtB -> B_15_31_0 ; _rtB -> B_15_52_0 = _rtP -> P_45 * _rtB ->
B_15_51_0 ; _rtB -> B_15_53_0 = _rtP -> P_46 * _rtB -> B_15_36_0 ; _rtB ->
B_15_54_0 = _rtB -> B_15_53_0 + _rtB -> B_15_5_0 ; _rtB -> B_15_55_0 = _rtB
-> B_15_38_0 * _rtB -> B_15_54_0 ; _rtB -> B_15_56_0 = _rtB -> B_15_55_0 -
_rtB -> B_15_43_0 ; _rtB -> B_19_0_0 = _rtB -> B_13_5_0 ; isHit =
ssIsSampleHit ( S , 1 , 0 ) ; if ( isHit != 0 ) { _rtDW -> MeasureOn_MODE = (
ssGetTaskTime ( S , 1 ) >= _rtP -> P_58 ) ; if ( _rtDW -> MeasureOn_MODE == 1
) { ratio = _rtP -> P_60 ; } else { ratio = _rtP -> P_59 ; } _rtB -> B_19_3_0
= ( ratio > _rtB -> B_19_2_0 ) ; if ( ssIsModeUpdateTimeStep ( S ) ) { if (
_rtB -> B_19_3_0 ) { if ( ! _rtDW -> CalcuateError_MODE ) { if (
ssGetTaskTime ( S , 1 ) != ssGetTStart ( S ) ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; } ( (
XDis_AbstractFuelControl_M1_T * ) ssGetContStateDisabled ( S ) ) ->
Integrator_CSTATE = 0 ; _rtDW -> CalcuateError_MODE = true ; } } else { if (
ssGetTaskTime ( S , 1 ) == ssGetTStart ( S ) ) { ( (
XDis_AbstractFuelControl_M1_T * ) ssGetContStateDisabled ( S ) ) ->
Integrator_CSTATE = 1 ; } if ( _rtDW -> CalcuateError_MODE ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; ( (
XDis_AbstractFuelControl_M1_T * ) ssGetContStateDisabled ( S ) ) ->
Integrator_CSTATE = 1 ; switch ( _rtDW -> SwitchCase_ActiveSubsystem ) { case
0 : ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; break ; case 1 :
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; ( (
XDis_AbstractFuelControl_M1_T * ) ssGetContStateDisabled ( S ) ) ->
Integrator_CSTATE = 1 ; break ; case 2 : break ; } _rtDW ->
SwitchCase_ActiveSubsystem = - 1 ; _rtDW -> CalcuateError_MODE = false ; } }
} } if ( _rtDW -> CalcuateError_MODE ) { rtPrevAction = _rtDW ->
SwitchCase_ActiveSubsystem ; if ( ssIsModeUpdateTimeStep ( S ) ) { switch (
_rtB -> B_19_0_0_c ) { case 1 : rtAction = 0 ; break ; case 2 : rtAction = 1
; break ; default : rtAction = 2 ; break ; } _rtDW ->
SwitchCase_ActiveSubsystem = rtAction ; } else { rtAction = _rtDW ->
SwitchCase_ActiveSubsystem ; } if ( rtPrevAction != rtAction ) { switch (
rtPrevAction ) { case 0 : ssSetBlockStateForSolverChangedAtMajorStep ( S ) ;
break ; case 1 : ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; ( (
XDis_AbstractFuelControl_M1_T * ) ssGetContStateDisabled ( S ) ) ->
Integrator_CSTATE = 1 ; break ; case 2 : break ; } } switch ( rtAction ) {
case 0 : if ( rtAction != rtPrevAction ) { if ( ssGetTaskTime ( S , 0 ) !=
ssGetTStart ( S ) ) { ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; } }
_rtB -> B_16_0_0 = _rtB -> B_15_1_0 / _rtB -> B_19_0_0 ; _rtB -> B_16_1_0 =
_rtB -> B_16_0_0 - _rtB -> B_16_0_0_c ; if ( ssIsModeUpdateTimeStep ( S ) ) {
srUpdateBC ( _rtDW -> overundershoot_SubsysRanBC ) ; } break ; case 1 : if (
rtAction != rtPrevAction ) { if ( ssGetTaskTime ( S , 0 ) != ssGetTStart ( S
) ) { ssSetBlockStateForSolverChangedAtMajorStep ( S ) ; } ( (
XDis_AbstractFuelControl_M1_T * ) ssGetContStateDisabled ( S ) ) ->
Integrator_CSTATE = 0 ; } _rtB -> B_17_0_0 = _rtX -> Integrator_CSTATE ; _rtB
-> B_17_1_0 = _rtB -> B_17_0_0 / _rtB -> B_17_0_0_m ; _rtB -> B_17_2_0 = _rtB
-> B_15_1_0 - _rtB -> B_19_0_0 ; isHit = ssIsSampleHit ( S , 1 , 0 ) ; if (
isHit != 0 ) { _rtDW -> MeasureOn_MODE_c = ( ssGetTaskTime ( S , 1 ) >= _rtP
-> P_54 ) ; if ( _rtDW -> MeasureOn_MODE_c == 1 ) { _rtB -> B_17_4_0 = _rtP
-> P_56 ; } else { _rtB -> B_17_4_0 = _rtP -> P_55 ; } } _rtB -> B_17_5_0 =
_rtB -> B_17_2_0 * _rtB -> B_17_2_0 * _rtB -> B_17_4_0 ; if (
ssIsMajorTimeStep ( S ) != 0 ) { if ( _rtDW -> Sqrt_DWORK1 != 0 ) {
ssSetBlockStateForSolverChangedAtMajorStep ( S ) ;
ssSetContTimeOutputInconsistentWithStateAtMajorStep ( S ) ; _rtDW ->
Sqrt_DWORK1 = 0 ; } _rtB -> B_17_6_0 = muDoubleScalarSqrt ( _rtB -> B_17_1_0
) ; } else { if ( _rtB -> B_17_1_0 < 0.0 ) { _rtB -> B_17_6_0 = -
muDoubleScalarSqrt ( muDoubleScalarAbs ( _rtB -> B_17_1_0 ) ) ; } else { _rtB
-> B_17_6_0 = muDoubleScalarSqrt ( _rtB -> B_17_1_0 ) ; } if ( _rtB ->
B_17_1_0 < 0.0 ) { _rtDW -> Sqrt_DWORK1 = 1 ; } } if ( ssIsModeUpdateTimeStep
( S ) ) { srUpdateBC ( _rtDW -> RMSerror_SubsysRanBC ) ; } break ; case 2 :
break ; } if ( _rtB -> B_19_0_0_c == 1 ) { _rtB -> B_18_3_0 = _rtB ->
B_16_1_0 ; } else { _rtB -> B_18_3_0 = _rtB -> B_17_6_0 ; } if (
ssIsModeUpdateTimeStep ( S ) ) { srUpdateBC ( _rtDW ->
CalcuateError_SubsysRanBC ) ; } } ssCallAccelRunBlock ( S , 20 , 2 ,
SS_CALL_MDL_OUTPUTS ) ; _rtB -> B_20_3_0 = _rtB -> B_13_4_0 ;
ssCallAccelRunBlock ( S , 20 , 4 , SS_CALL_MDL_OUTPUTS ) ;
ssCallAccelRunBlock ( S , 20 , 5 , SS_CALL_MDL_OUTPUTS ) ;
ssCallAccelRunBlock ( S , 20 , 6 , SS_CALL_MDL_OUTPUTS ) ; UNUSED_PARAMETER (
tid ) ; } static void mdlOutputsTID3 ( SimStruct * S , int_T tid ) {
B_AbstractFuelControl_M1_T * _rtB ; DW_AbstractFuelControl_M1_T * _rtDW ;
P_AbstractFuelControl_M1_T * _rtP ; _rtDW = ( ( DW_AbstractFuelControl_M1_T *
) ssGetRootDWork ( S ) ) ; _rtP = ( ( P_AbstractFuelControl_M1_T * )
ssGetModelRtp ( S ) ) ; _rtB = ( ( B_AbstractFuelControl_M1_T * )
_ssGetModelBlockIO ( S ) ) ; _rtB -> B_8_0_0 = _rtP -> P_84 ; _rtB -> B_8_2_0
= _rtB -> B_8_0_0 + _rtP -> P_85 ; _rtB -> B_9_0_0 = _rtP -> P_86 ; _rtB ->
B_4_0_0 = _rtP -> P_77 ; _rtB -> B_4_1_0 = _rtP -> P_78 ; _rtB -> B_15_1_0_k
= _rtP -> P_47 ; _rtB -> B_15_2_0_c = _rtP -> P_48 ; _rtB -> B_15_3_0_b =
_rtP -> P_49 ; _rtB -> B_15_4_0_p = _rtP -> P_50 ; _rtB -> B_15_5_0 = _rtP ->
P_51 ; _rtB -> B_19_0_0_c = _rtP -> P_104 ; _rtB -> B_16_0_0_c = _rtP -> P_52
; _rtB -> B_17_0_0_m = _rtP -> P_57 ; if ( ssIsModeUpdateTimeStep ( S ) ) {
srUpdateBC ( _rtDW -> CalcuateError_SubsysRanBC ) ; } _rtB -> B_19_2_0 = _rtP
-> P_61 ; UNUSED_PARAMETER ( tid ) ; }
#define MDL_UPDATE
static void mdlUpdate ( SimStruct * S , int_T tid ) {
B_AbstractFuelControl_M1_T * _rtB ; DW_AbstractFuelControl_M1_T * _rtDW ;
P_AbstractFuelControl_M1_T * _rtP ; _rtDW = ( ( DW_AbstractFuelControl_M1_T *
) ssGetRootDWork ( S ) ) ; _rtP = ( ( P_AbstractFuelControl_M1_T * )
ssGetModelRtp ( S ) ) ; _rtB = ( ( B_AbstractFuelControl_M1_T * )
_ssGetModelBlockIO ( S ) ) ; { real_T * * uBuffer = ( real_T * * ) & _rtDW ->
fuelsystemtransportdelay_PWORK . TUbufferPtrs [ 0 ] ; real_T simTime = ssGetT
( S ) ; _rtDW -> fuelsystemtransportdelay_IWORK . Head = ( ( _rtDW ->
fuelsystemtransportdelay_IWORK . Head < ( _rtDW ->
fuelsystemtransportdelay_IWORK . CircularBufSize - 1 ) ) ? ( _rtDW ->
fuelsystemtransportdelay_IWORK . Head + 1 ) : 0 ) ; if ( _rtDW ->
fuelsystemtransportdelay_IWORK . Head == _rtDW ->
fuelsystemtransportdelay_IWORK . Tail ) { if ( !
AbstractFuelControl_M1_acc_rt_TDelayUpdateTailOrGrowBuf ( & _rtDW ->
fuelsystemtransportdelay_IWORK . CircularBufSize , & _rtDW ->
fuelsystemtransportdelay_IWORK . Tail , & _rtDW ->
fuelsystemtransportdelay_IWORK . Head , & _rtDW ->
fuelsystemtransportdelay_IWORK . Last , simTime - _rtP -> P_38 , uBuffer , (
boolean_T ) 0 , ( boolean_T ) 1 , & _rtDW -> fuelsystemtransportdelay_IWORK .
MaxNewBufSize ) ) { ssSetErrorStatus ( S , "vtdelay memory allocation error"
) ; return ; } } ( * uBuffer + _rtDW -> fuelsystemtransportdelay_IWORK .
CircularBufSize ) [ _rtDW -> fuelsystemtransportdelay_IWORK . Head ] =
simTime ; ( * uBuffer + 2 * _rtDW -> fuelsystemtransportdelay_IWORK .
CircularBufSize ) [ _rtDW -> fuelsystemtransportdelay_IWORK . Head ] = ( (
X_AbstractFuelControl_M1_T * ) ssGetContStates ( S ) ) ->
fuelsystemtransportdelay_CSTATE ; ( * uBuffer ) [ _rtDW ->
fuelsystemtransportdelay_IWORK . Head ] = _rtB -> B_15_45_0 ; }
UNUSED_PARAMETER ( tid ) ; }
#define MDL_UPDATE
static void mdlUpdateTID3 ( SimStruct * S , int_T tid ) { UNUSED_PARAMETER (
tid ) ; }
#define MDL_DERIVATIVES
static void mdlDerivatives ( SimStruct * S ) { B_AbstractFuelControl_M1_T *
_rtB ; DW_AbstractFuelControl_M1_T * _rtDW ; P_AbstractFuelControl_M1_T *
_rtP ; XDot_AbstractFuelControl_M1_T * _rtXdot ; X_AbstractFuelControl_M1_T *
_rtX ; _rtDW = ( ( DW_AbstractFuelControl_M1_T * ) ssGetRootDWork ( S ) ) ;
_rtXdot = ( ( XDot_AbstractFuelControl_M1_T * ) ssGetdX ( S ) ) ; _rtX = ( (
X_AbstractFuelControl_M1_T * ) ssGetContStates ( S ) ) ; _rtP = ( (
P_AbstractFuelControl_M1_T * ) ssGetModelRtp ( S ) ) ; _rtB = ( (
B_AbstractFuelControl_M1_T * ) _ssGetModelBlockIO ( S ) ) ; _rtXdot ->
Integrator_CSTATE_m = _rtB -> B_15_29_0 ; _rtXdot -> Throttledelay_CSTATE =
0.0 ; _rtXdot -> Throttledelay_CSTATE += _rtP -> P_9 * _rtX ->
Throttledelay_CSTATE ; _rtXdot -> Throttledelay_CSTATE += ( (
ExternalUPtrs_AbstractFuelControl_M1_T * ) ssGetU ( S ) ) -> PedalAngle ;
_rtXdot -> p00543bar_CSTATE = _rtB -> B_15_52_0 ; _rtXdot ->
Integrator_CSTATE_h = _rtB -> B_15_48_0 ; _rtXdot -> Integrator_CSTATE_c =
_rtB -> B_15_56_0 ; { real_T instantDelay ; instantDelay = _rtB -> B_15_50_0
; if ( instantDelay > _rtP -> P_38 ) { instantDelay = _rtP -> P_38 ; } if (
instantDelay < 0.0 ) { ( ( XDot_AbstractFuelControl_M1_T * ) ssGetdX ( S ) )
-> fuelsystemtransportdelay_CSTATE = 0 ; } else { ( (
XDot_AbstractFuelControl_M1_T * ) ssGetdX ( S ) ) ->
fuelsystemtransportdelay_CSTATE = 1.0 / instantDelay ; } } if ( _rtDW ->
CalcuateError_MODE ) { ( ( XDot_AbstractFuelControl_M1_T * ) ssGetdX ( S ) )
-> Integrator_CSTATE = 0.0 ; if ( _rtDW -> SwitchCase_ActiveSubsystem == 1 )
{ _rtXdot -> Integrator_CSTATE = _rtB -> B_17_5_0 ; } } else { ( (
XDot_AbstractFuelControl_M1_T * ) ssGetdX ( S ) ) -> Integrator_CSTATE = 0.0
; } }
#define MDL_ZERO_CROSSINGS
static void mdlZeroCrossings ( SimStruct * S ) { B_AbstractFuelControl_M1_T *
_rtB ; DW_AbstractFuelControl_M1_T * _rtDW ; P_AbstractFuelControl_M1_T *
_rtP ; ZCV_AbstractFuelControl_M1_T * _rtZCSV ; _rtDW = ( (
DW_AbstractFuelControl_M1_T * ) ssGetRootDWork ( S ) ) ; _rtZCSV = ( (
ZCV_AbstractFuelControl_M1_T * ) ssGetSolverZcSignalVector ( S ) ) ; _rtP = (
( P_AbstractFuelControl_M1_T * ) ssGetModelRtp ( S ) ) ; _rtB = ( (
B_AbstractFuelControl_M1_T * ) _ssGetModelBlockIO ( S ) ) ; _rtZCSV ->
theta090_UprLim_ZC = _rtB -> B_15_3_0 - _rtP -> P_11 ; _rtZCSV ->
theta090_LwrLim_ZC = _rtB -> B_15_3_0 - _rtP -> P_12 ; _rtZCSV ->
EngineSpeed9001100_UprLim_ZC = ( ( ExternalUPtrs_AbstractFuelControl_M1_T * )
ssGetU ( S ) ) -> EngineSpeed - _rtP -> P_13 ; _rtZCSV ->
EngineSpeed9001100_LwrLim_ZC = ( ( ExternalUPtrs_AbstractFuelControl_M1_T * )
ssGetU ( S ) ) -> EngineSpeed - _rtP -> P_14 ; _rtZCSV ->
AFSensorFaultInjection_StepTime_ZC = ssGetT ( S ) - _rtP -> P_16 ; if ( (
_rtB -> B_15_16_0 != _rtB -> B_15_16_0 ) || ( _rtB -> B_15_15_0 < _rtB ->
B_15_16_0 ) ) { if ( _rtDW -> MinMax_MODE == 0 ) { _rtZCSV ->
MinMax_MinmaxInput_ZC = _rtB -> B_15_15_0 - _rtB -> B_15_15_0 ; } else {
_rtZCSV -> MinMax_MinmaxInput_ZC = _rtB -> B_15_15_0 - _rtB -> B_15_16_0 ; }
} else if ( _rtDW -> MinMax_MODE == 0 ) { _rtZCSV -> MinMax_MinmaxInput_ZC =
_rtB -> B_15_16_0 - _rtB -> B_15_15_0 ; } else { _rtZCSV ->
MinMax_MinmaxInput_ZC = _rtB -> B_15_16_0 - _rtB -> B_15_16_0 ; } _rtZCSV ->
Switch_SwitchCond_ZC = _rtB -> B_15_17_0 - _rtP -> P_22 ; _rtZCSV ->
flowdirection_Input_ZC = _rtB -> B_15_20_0 ; _rtZCSV -> Pwon_StepTime_ZC =
ssGetT ( S ) - _rtP -> P_0 ; _rtZCSV -> MeasureOn_StepTime_ZC = ssGetT ( S )
- _rtP -> P_58 ; if ( _rtDW -> CalcuateError_MODE ) { { ( (
ZCV_AbstractFuelControl_M1_T * ) ssGetSolverZcSignalVector ( S ) ) ->
MeasureOn_StepTime_ZC_n = 0.0 ; } if ( _rtDW -> SwitchCase_ActiveSubsystem ==
1 ) { _rtZCSV -> MeasureOn_StepTime_ZC_n = ssGetT ( S ) - _rtP -> P_54 ; } }
else { { ( ( ZCV_AbstractFuelControl_M1_T * ) ssGetSolverZcSignalVector ( S )
) -> MeasureOn_StepTime_ZC_n = 0.0 ; } } } static void mdlInitializeSizes (
SimStruct * S ) { ssSetChecksumVal ( S , 0 , 1695209762U ) ; ssSetChecksumVal
( S , 1 , 1459460708U ) ; ssSetChecksumVal ( S , 2 , 3312372564U ) ;
ssSetChecksumVal ( S , 3 , 1612273060U ) ; { mxArray * slVerStructMat = (
NULL ) ; mxArray * slStrMat = mxCreateString ( "simulink" ) ; char slVerChar
[ 10 ] ; int status = mexCallMATLAB ( 1 , & slVerStructMat , 1 , & slStrMat ,
"ver" ) ; if ( status == 0 ) { mxArray * slVerMat = mxGetField (
slVerStructMat , 0 , "Version" ) ; if ( slVerMat == ( NULL ) ) { status = 1 ;
} else { status = mxGetString ( slVerMat , slVerChar , 10 ) ; } }
mxDestroyArray ( slStrMat ) ; mxDestroyArray ( slVerStructMat ) ; if ( (
status == 1 ) || ( strcmp ( slVerChar , "10.5" ) != 0 ) ) { return ; } }
ssSetOptions ( S , SS_OPTION_EXCEPTION_FREE_CODE ) ; if ( ssGetSizeofDWork (
S ) != sizeof ( DW_AbstractFuelControl_M1_T ) ) { ssSetErrorStatus ( S ,
"Unexpected error: Internal DWork sizes do "
"not match for accelerator mex file." ) ; } if ( ssGetSizeofGlobalBlockIO ( S
) != sizeof ( B_AbstractFuelControl_M1_T ) ) { ssSetErrorStatus ( S ,
"Unexpected error: Internal BlockIO sizes do "
"not match for accelerator mex file." ) ; } if ( ssGetSizeofU ( S ) != sizeof
( ExternalUPtrs_AbstractFuelControl_M1_T ) ) { static char msg [ 256 ] ;
sprintf ( msg , "Unexpected error: Internal ExternalInputs sizes do "
"not match for accelerator mex file." ) ; ssSetErrorStatus ( S , msg ) ; } if
( ssGetSizeofY ( S ) != sizeof ( ExtY_AbstractFuelControl_M1_T ) ) { static
char msg [ 256 ] ; sprintf ( msg ,
"Unexpected error: Internal ExternalOutputs sizes do "
"not match for accelerator mex file." ) ; } { int ssSizeofParams ;
ssGetSizeofParams ( S , & ssSizeofParams ) ; if ( ssSizeofParams != sizeof (
P_AbstractFuelControl_M1_T ) ) { static char msg [ 256 ] ; sprintf ( msg ,
"Unexpected error: Internal Parameters sizes do "
"not match for accelerator mex file." ) ; } } _ssSetModelRtp ( S , ( real_T *
) & AbstractFuelControl_M1_rtDefaultP ) ; rt_InitInfAndNaN ( sizeof ( real_T
) ) ; ( ( P_AbstractFuelControl_M1_T * ) ssGetModelRtp ( S ) ) -> P_62 =
rtInfF ; } static void mdlInitializeSampleTimes ( SimStruct * S ) {
slAccRegPrmChangeFcn ( S , mdlOutputsTID3 ) ; } static void mdlTerminate (
SimStruct * S ) { }
#include "simulink.c"
