//! H2-Rust · 운동론 커널 — 무충돌 구적(freestream)과 Lewis-Challinor 다극 계층.
//!
//! Python 오라클: `bianchi.matter.freestream` (정확 구적), `bianchi.matter.hierarchy`.
//! 두 경로 모두 차등테스트로 대조한다 (`tests/test_rustcore_differential.py`).
//!
//! **왜 Rust 인가**: 계층은 (l_max+1)×(i_max+1) 개의 PSTF 텐서를 상태로 갖는 ODE 계이고,
//! RK4 한 스텝마다 σ-결합 축약과 PSTF 사영을 수십 번 수행한다.  Python/numpy 로는
//! 스텝당 소형 배열 오버헤드가 지배적이다 (R1 광선추적과 같은 병리).

pub mod characteristics;
pub mod coeff_hier;
pub mod coeff_tables;
pub mod collide_exact;
pub mod collision;
pub mod comoving;
pub mod coupled;
pub mod generic_vector;
pub mod grid_collide;
pub mod hierarchy;
pub mod pol_collide;
pub mod pstf;
pub mod pstf_gen;
pub mod qevolve;
pub mod quad;
pub mod radial;
pub mod sphere;
pub mod tilted_hier;
pub mod tilted_terms;
pub mod transport;
pub mod typev;
pub mod viscous;
