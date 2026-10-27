# B3h source 복구·소비 경계

## 실제 수행

`rec_bianchi@ea89c97abeb7a663a813f00e9aadddaf0b32a6a9`에서 원문 9개,
총 98,149 bytes를 공개 raw URL로 복구했다. 모든 원문은 이번 GitHub tree/file
응답의 Git blob SHA1과 일치한다. 각 경로·URL·size·SHA256·Git blob은
`RECOVERY_MANIFEST.json`에 있다. 새 과학 계산, 기존 campaign 재실행,
원격 mutation은 수행하지 않았다.

## 판정

실제 native scalar Ly-alpha incoming departure와 native atomic source owner는
복구되었다. 유한 photon donor cell/face, spectral/angular/time support,
volume/clock 및 그 support와 native line face 사이의 관계는 미공급이다.
상태는 `PARTIAL_SOURCE_BOUND / INPUT_DEPENDENT_FINITE_SUPPORT`다.

`Dfplus_Lya` 자체가 없다는 판정은 부정확하다. 실제 저장된 값은
`7.6643364422337378e-15`다. 그러나 이 scalar를 finite photon inventory,
anisotropic directional incident field 또는 coupled macro endpoint로
동일시할 수는 없다.

## 1. Source convention 두 가지

Native LINE02 source는 native Wien departure를 사용한다.

```text
r0 = LYA_FACT * H / (nH * x1s)
b0 = 3 * x1s * Dfplus_Lya
native pair: Trr[1,1] += r0; sr[1] += r0*b0
x2p = xr_p + 3*x1s*exp(-E21/TR)
```

Native convention으로 occupation을 표시한다면 reference는
`exp(-E21/TR)`다. 원문 decimal departure 자체와 reference convention을
함께 보존하는 것이 가장 작은 소비 계약이다.

별도 LINE01 frozen contract는

```text
standalone total f_plus = 1/expm1(E21/TR) + Dfplus_Lya
```

를 명시한다. 이 Planck/stimulated standalone model은 같은 contract에서
native source-identical replay와 구별한다. 따라서 두 값을 계산할 경우
이름·source owner·유효범위를 각각 기록해야 한다. Planck 식을 native
source의 조용한 대체로 사용하지 않는다.

근거:

- `research/rec_line_native_owner_20261023/FROZEN_CONTRACT.md`, §2–3.
- `research/rec_line_source_20261023/FROZEN_CONTRACT.md`, §1–2.
- `research/rec_line_native_owner_20261023/code/native_line_owner.py`.

## 2. 실제 snapshot과 원자 소유권

`inputs/STORED_NATIVE_LYA_STATE.json`은 source CSV에서 decimal 문자열을
변환 없이 추출한 원자료다. z=1099.9986525171403, prefix=5127,
nH_cm3=250.18675437302318, H_sInv=4.9696512229238343e-14,
TR_eV_rescaled=0.25882399309326415, fsR=meR=1이다.

원문은 `angular_distribution=NOT_STORED`를 명시한다. Scalar source snapshot의
방향 확장은 별도 fixture/closure이며 실제 관측 방향장으로 분류하지 않는다.

LINE02의 exclusive replacement는 위 직접 loss/source pair만 포함한다.
Beta, 2s/2p mixing, two-photon/Raman, virtual diffusion, Trv/Tvr/Tvv,
기존 history와 다른 source는 보존된다. Native source active 상태에서
detached LINE01을 더하면 duplicate owner다.

Native saved source ledger의 instantaneous number/energy rate는 재사용할 수
있지만, finite donor depletion이나 evolved radiation stress와 구분한다.
그 공급자는 H Ly-alpha effective line model이며 isotope-resolved recoil
provider를 자체로 공급하지 않는다.

## 3. Source constants

```text
E21 = 10.198714553953742 eV
native LYA_FACT = 4.662899067555897e15 cm^-3
native hPc = 1.239841874331e-04 eV cm
```

`hydrogen.h`의 literal과 source facts를 보존한다. 저장된 source facts에서
modern exact hc를 대입한 LYA_FACT 차이는 상대
`-2.661653527580299e-7`이다. inherited 2e-8 gate를 적용하는 비교에 이를
roundoff로 섞거나 상수를 조용히 치환하지 않는다. Native source identity와
현대 constants를 사용한 별도 physical model을 구분한다.

E21의 eV-to-J 변환은 native frozen contract대로 exact conversion을 쓴다.

## 4. 유한 inventory와 incident face의 연결

BASS B3b2는 실제 REC 35 cell x 26 direction의 910 locked packet state를
이미 검증했다. 그 scope는 scalar isotropic bootstrap INITIAL_DATA,
hydrogen tetrad, coupled_macro_endpoint=false다. 해당 cell occupation은
native Ly-alpha blue-face incident trace와 구별된다.

기존 G_i,A_j,f_ij가 정의하는 finite donor count를 사용할 때는 실제
선택 donor 집합과 volume이 필요하다. Face-flux 방식을 택하면 area,
time interval, angular flux factor 및 face reconstruction owner가 필요하다.
이미 저장된 line-centre occupation 한 점만으로 finite bandwidth나
수용 가능한 photon stock을 발명하지 않는다.

B3b의 prescribed-f>0 positive gross up/down map은 재사용 가능한 식이다.
Finite donor coupling에서는 f_plus의 depletion을 함께 닫는 계약이 필요하다.
고정 f_plus로 계산한 뒤 donor 부족을 clipping하면 해당 계약을 충족하지 않는다.

## 5. 최신 REC physical binding 상태

최신 `rec_history_pullback_20261025/NEXT_INPUT_CONTRACT.md`에 따르면:

- actual original history 35,239,470 bytes,
  SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1,
  prefix5127,313queries의 payload admission은 완료했다.
- H5 physical epsilon/reference/endpoint/curvature/absolute history bound 및
  physical outgoing bound는 null이다.
- H6 실제 incident trace, selected Bianchi geodesic/direction/frame/measure/
  volume/clock/source-query owner 결속은 OPEN이다.
- H7 실제 DY,DQ,Dtheta,reference 변화와 thermal ODE/retiming/geometry/measure
  owner 결속은 OPEN이다.
- PB01 numerical controls .01U/.2safe_radius를 physical uncertainty로 쓰지 않는다.

## 6. 이번 adapter의 최소 입출력

즉시 결속 가능한 출력:

- native source snapshot와 decimal incoming departure.
- source reference/constant convention과 source-qualified population 식.
- exclusive native pair 또는 detached mode 중 하나의 명시적 선택.
- 위 source의 정확한 domain과 기존 검증 범위.

추가 공급이 필요한 필드는 다음처럼 typed 상태로 유지한다.

```text
finite_incident_support = null
finite_donor_inventory_link_to_line_face = null
volume_and_clock_binding = null
selected_channel_isotope_state_recoil_owner = null
source_qualified_physical_error_radii = null
physical_finite_absorption_admission = INPUT_DEPENDENT
```

이 결손은 선택한 Ly-alpha channel의 의무다. 선택하지 않은 미래의 모든
atomic/nuclear/molecular supplier를 이번 B3h/B3i의 일괄 선행조건으로 추가하지
않는다. B3i의 per-sector T/Q bridge는 별도 구현·검증할 수 있으며,
실제 finite absorption admission과 calibrated geometry execution은 위 입력이
공급된 뒤 판정한다.

## 7. 예산과 실행

중앙 B3h 계약은 새 allowance를 발급하지 않으며 remaining wall/CPU=null,
budget_reset=false다. 이번 복구는 network/file/hash 작업만 수행했다.
과학 결과 재계산·새 native/IVP/source transaction은 0이다.
