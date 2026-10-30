# BASS KM-2F | Einstein–원본 편광광자–냉전자 결합의 실제 Bianchi-I 해

**2026-10-30 · 새 물리 단위 한정 실행·검증, 상위 BASS DAG 9/15 (21 edges), KM-2 PARTIAL.** 부모 Draft PR276 immutable HEAD `58277dab1af10850ff0a86c74673743b2c0a8a5a`. 신규 Draft PR278 브랜치 `research/bass-km2f-einstein-momentum-constraints-20261030-r1`. 기존 원본, 형제 PR, production/main 모두 그대로 보존, 병합 없음.

## 1. 이 연구에서 처음 해결한 실제 GR 제약

이전 KM-2E는 광자-냉전자 충돌 반작용을 함께 진화시켰지만 **Bianchi I 기하 H,σ는 외부에서 처방**했다. 이전 초기 전자 β=(+.3,-.4,+.2)를 Einstein Bianchi I 문제에 그대로 넣으면 총 유속 q_gamma+q_e가 0이 아니므로 공간적으로 균일한 Einstein 운동량 제약을 위반한다. Bianchi I의 균일한 정상계 운동량 제약은 **총 유속 q_total=0**이며, 비대각 shear를 마음대로 선택하거나 Hamiltonian만 맞춘다고 해결되지 않는다.

본 유닛에서는 **동일한 원본 광자 초기 분포와 편광·각도 광선·weights를 그대로 고정**한 채, 전자 초기 β를 `-q_gamma0/R_e0`로 결정했다. 기존 원본 초기 광자 `rho_gamma0=39.01110262768746`, `q_gamma0=(14.49610381,-18.92212948,9.43499472)`를 확인했다. 앞선 KM-2E의 인공 전자/광자 초기 정상계 에너지비 .75라면 |β_e0|=.87619가 필요해 유한한 GL ray 각도적분의 force gap이 커진다. 별도 GR 파일럿의 투명한 새로운 물질 초기조건은 `R_e0/rho_gamma0=3.0`으로 |β_e0|=.21891가 되며, 이 값은 **관측으로 보정한 전자/양성자 수밀도가 아닌 인공 연구 매개변수**다. 무차원 중력결합 κ=8πG ρ_unit Tstar²=.003, Λ=0을 고정하고 `H0=+[κρtotal0+σ0²]^(1/2)/√3`를 적용했다.

## 2. 질량껍질·계량·자기일관 Einstein 방정식

Signature (-,+,+,+), 정상 고유시간 u=t/Tstar. 원본 photon propagation directions n, 원본 P8 real `S+iA` Hermitian polarization, 원본 KM1 parallel screen/angle weights와 원본 KM2A finite-beta elastic Thomson. 공간 격자와 전자 압력 없는 dust는 균일하다. 방향은 기존 초기 normal angular grid에서 시작해 동적인 spatial momentum coframe A(u)를 이용해 `n=A n0/|A n0|`;  A' = -(HI+σ) A`, `w=w0 det A/|A n0|³`로 계속 진화하며, 원본 KM1 screen `E'=(n' n^T-n n'^T)E`로 광자 편광 방향을 옮긴다. 이제 H와 σ는 이전 KM2C의 처방 `Profile.fields(u)`를 사용하지 않고 **동일한 coupled ODE 안의 Einstein 방정식**으로 진화한다. 최초 σ(0)만 원본 KM2C `Profile('noncommuting')`의 대칭·tracefree 값으로 사용한다.

냉전자: `p=γβ`, `γ=√(1+p·p)`, `ζ=n_lab(u)/n_lab(0)`, `n_rest/n_rest0=ζγ0/γ`, `ν(u)=ν0 ζγ0/γ`, `R_e=M0 ζγ`, `Q_e=M0 ζp`, `P_e=R_e β⊗β`. 엄밀한 전자 normal-number law `ζ'=-3Hζ`, 동적 운동량 `p'=-(HI+σ)p-F_gamma_spatial/(M0 ζ)`, 여기서 `F_gamma`는 원래 코드의 순간 공변 Thomson photon fourforce이며 냉전자는 그 **정확히 반대** 힘을 받는다. Full photon ray의 J'에는 기존 KM1 P8 streaming과 KM2A collision을 그대로 사용한다.

`ρ=ρ_gamma+R_e`, `Q=q_gamma+Q_e`, `P=P_gamma+P_e`, `p_iso=tr P/3`, `π=P-p_iso I`, `σ²=tr(σ²)/2`. 새로운 homogeneous Einstein equations:

```
H' = -κ(ρ+p_iso)/2 -σ²
σ' = -3H σ+κπ
3H² = κρ+σ²                  [Hamiltonian constraint]
Q = 0                         [homogeneous momentum constraint]
```

임의의 tracefree 대칭 σ는 5개 독립 변수로 보존해 인위적인 state projection을 사용하지 않는다. `A'`와 normal screen E' 그리고 광자 full polarized J'는 H,σ와 완전히 결합. 정상 frame의 공간 metric g_spatial=(AᵀA)^(-1)와 그것의 positive definiteness, photon redshift, density dilution `ζ=det(A)`를 검사했다.

**유한 angular quadrature 오차의 정확한 취급:** `δF = F_gamma(raw P8)-F_gamma(covariant)`. 총 에너지·운동량 수지와 Hamiltonian 제약 전파를 직접 유도:

```
ρ' = -3H(ρ+p_iso)-σ:π+δF0
Q' = -(4HI+σ)Q+δF_spatial
C_H =3H²-κρ-σ²
C_H'=-κ δF0
R_geometry-R_matter=4 C_H,
R_geometry=6H'+12H²+2σ², R_matter=κ(ρ-3p_iso)
```

앞의 식들은 이전 수치 하늘의 finite positive GL-ray quadrature를 **엄밀한 continuum source로 거짓 대체하지 않고** 제약 전파에 명시적으로 넣는다. 독립 Wolfram symbolic check에서 `C_H'=-κδF0` 및 scalar curvature identity 잔차가 각각 `-κδF0`와 0으로 귀결됨을 확인했다. 추가로 `d(σ/ζ)/du=κπ/ζ` 적분을 원래 Einstein shear source의 독립 확인으로 사용했다.

## 3. 실제 원격 실행 데이터와 독립 회귀

새 [GitHub Actions #41030924777](https://github.com/cosmosapjw-quantum/bass/actions/runs/41030924777) **SUCCESS**, 새로운 full-coupled Einstein+full polarized photon+nabla cold electron IVP를 ntheta12/16에서 실제 생성. 고정 source와 재현성 있는 원래 동적 소스 회귀 **12/12 pytest PASS**. Raw primitive tensors and stress for five epochs plus 24-point independent source-integral diagnostics included as JSON/CSV.

| 측정값 | nθ=12, nφ=24 | nθ=16, nφ=32 |
|---|---:|---:|
| 양의 H(0) | .4077710220597041 | .40777102205970406 |
| H(.25) | .34728215450207445 | .3472821545497597 |
| 총 정상계 ρ(0) | 156.0444105107498 | 156.0444105107498 |
| 총 정상계 ρ(.25) | 114.87356768345528 | 114.87356755278712 |
| σ²(0) | .03069838776259772 | .03069838776259772 |
| σ²(.25) | .01719398191463662 | .017193981947266974 |
| 최대 정규화 Hamiltonian 제약 잔차 | **1.26637861124e-9** | **1.49568519229e-12** |
| 최대 정규화 총 운동량 제약 잔차 | **4.63680331022e-9** | **4.55378522591e-12** |
| κπ에 의한 unsourced shear 희석 대비 순변화 노름 | **.00696983356581219** | **.006969833067281019** |
| 초기 σ와 최종 σ의 비가환자 Frobenius 노름 | .001770857940980589 | .001770857850352602 |
| 원본 discrete P8/covariant force 최대 정규화 gap | 1.79298566779e-7 | 5.51706882213e-10 |

모든 수치는 이 파일럿의 무차원 정규화 값. 초기 β_e=(-.1238630614482002,+.1616815744074234,-.08061802993228867), 최종 nθ16 β_e=(-.07598188318321183,+.09438171206674392,-.04489872361892869). 초기 momentum constraint를 만족시키기 위해 기존 KM2E **전자** 초기 β와 인공 정상 에너지비를 변경했지만 원본 **광자** 초기 분포는 byte-immutable. 이 차이를 과거 파일럿과 동일한 초기조건이라고 주장하지 않는다.

실제 중력 backreaction에 의해 H가 감소하고, σ²는 .0306984→.0171940으로 바뀐다. `σ_final-ζ_final σ_initial`의 노름이 약 .00697이므로 이는 단순한 shear  a^{-3} decay만이 아닌 **광자+전자 비등방 응력 κπ로 인한 새로운 source contribution**임을 확인한다. 초기 shear와 최종 shear의 commutator가 .00177085785로 0이 아니라 실제 고유축 회전/비가환 3×3 효과도 살아 있다. 이 결과는 ODE 초기조건과 부호 규약이 명시된 범위에서의 numerical data이며 고차 연속체 interval certificate가 아니다.

### 제약 전파를 따로 적분한 확인

- nθ16 `C_H(.25)≈5.4116e-13`, 실제 ΔC_H와 별도로 적분한 `-κ∫δF0du`의 차 **1.94419996915e-15**.
- nθ16 total-Q momentum constraint drift와 `∫[-(4HI+σ)Q+δF_sp] du`의 최대 차 **3.54583032042e-14**.
- nθ16 `σ/ζ`의 실제 진화 vs 독립 GL24 `κ∫π/ζ du`의 최대 차 **8.15862134795e-17**.
- 별도 독립 full GR IVP: 전자 matter-state를 p와 β로 각각 진화할 때 u=.25 최대 β 차 `1.0131e-15`, H 차 `2.78e-16`, 모든 shear 성분 차 `9.71e-17`, full photon J 차 `3.79e-14` (nθ12).
- 별도 Minkowski/zero-shear/κ=0 대조군의 총 photon+electron energy drift `-6.04643446422e-10`, max total momentum drift `1.47843515208e-9`이며, 이는 0으로 투영하지 않은 raw quadrature gap과 일치하는 허용 범위다. H와 σ는 정확히 0을 유지했다.

수치적으로 제약 잔차가 nθ12→16에서 ~1e-9→1e-12로 감소했다는 것은 각도 해상도가 지배하는 해당 실험의 검증이지, 모든 초기 photon 배경에 대한 정리 또는 무한 ray continuum 증명이 아니다. **GR 제약을 위반한 초기조건을 단순히 H만 맞춰서 해소하지 않았다.**

## 4. 재현 코드·원본 보호

New code `research/dual_lane_km2f_20261030/einstein_bianchi.py`, adversarial tests `tests/test_einstein_bianchi.py`, SHA manifest archiver `package_artifacts.py`, GitHub Actions `.github/workflows/km2f-einstein-constraints.yml`. 원본 모두 immutable BASS Git blob: KM2C curved_tilt `05aade3aab7e9a32c11608882c943e4d3cb6f379`; KM2A tilted_collision `92660768f4719d78261fed1cb44f186d2821629d`; KM1 source_memory `9d500e36fefaa4ddc22300a2f03d9eb9cfe98403`; KM2D accelerating_tilt `b599d3842e843d8de1de1499b73e6849374bf8f8`; KM2E coupled_electron_photon `12fbce8109fc07b1fbf60d9a066d8aa1c57ea9c1`. New source and tests exact Git blob hashes bound in stage receipts. Local preliminary tests 12/12 PASS, *actual CI regenerated the full physical data* and 12/12 PASS; physical inputs and SHA guards enforced inside CI. Native subagent and distinct-author independent R6/C9 NOT_RUN.

## 5. Scientific trust ceiling, downstream research

**This unit is a genuine homogeneous Einstein-Bianchi I numerical selfconsistent geometry coupled to original polarized collisionless streaming and Thomson photons plus cold electron dust**. The parent KM2E's photon/electron source is not redefined, yet the physical electron initial state and normalized mass/gravity parameters are intentionally changed to solve the full homogeneous GR constraints. This does not certify: inhomogeneous Einstein–Boltzmann, cosmological parameter observations, realistic electron/ion abundances, hot-electron pressure and Compton frequency redistribution, baryonic hydrodynamics, finite angular quadrature continuum enclosures, full Rust/MPFR formal proof, or independent human review. The present numerical H,σ and gauge provide a concrete new data node for later physically meaningful generalizations. **Upper DAG 9/15, KM2 PARTIAL, new completed upper 0, production_ready=false, merge_ready=false, auto_next=false**.

### Verified stages and archiving

Original science-head Actions run **41030924777** generated source-complete S0/S1/S2 GitHub artifacts **12966141258 / 12965467451 / 12965367780** and checked outer/nested ZIP CRC+member SHA (11/11,18/18,18/18 PASS). Google Drive provider creates plus exact raw-byte download SHA256 match for S0/S1/S2 and S2 inner ZIP:

| stage | outer bytes, SHA256 | Drive ID |
|---|---|---|
| S0 | 40823, `755903c918a388c05c1c1b42e6c2474a2deb2586afb2f1989fa4a04dc16ecd5a` | `1I3VHMGaKKI-yyE6b38BgCBi4tJJPzEA_` |
| S1 | 78119, `44690b520fc191dfdcca4264beefe24d6d0c4a8b8e02bbd6b9efffe380f9fd9a` | `1MblLA-5CqqxOCoucQwn8Un-7oQJJecvr` |
| S2 | 96868, `cf34bbbbff3571a9382333e38823910eb70a85c2d5956318a34c35de4afd8f60` | `1vSbvWAewkvJmRnTbCz2SxTPFwUxePNu_` |
| S2 nested science ZIP | 79381, `749b7a34bc15431a94ab0798d02790a461f62c5d5e8f9d30c9252177bdc75070` | `1Dc6Bh9NCobwueiOD23kn9glcxQhLaz2p` |

ChatGPT Library `/BASS_KM2F_20261030/` also holds create-only stage archives, direct new source and tests; Library raw independent readback NOT_RUN. **Dropbox new ZIP not uploaded**: app needs host-injected source_file fileParam unavailable in this code-driven invocation; no invented Dropbox checksum or second-provider ACK. The subsequent final documentation HEAD CI and complete final ZIP are verified separately and appended to PR metadata after their successful actual runs.

STOP_AFTER_ONE_BOUNDED_UNIT=true.
