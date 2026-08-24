//! B1 · 열역학 커널 (Rust).
//!
//! **왜 이것만 Rust 인가** (계획 §0 측정 결과): 재결합·동결 자체는 Python 으로 충분하다.
//! Rust 가 실제로 푸는 병목은 **ODE RHS 안에서 매 스텝 불리는 비싼 적분**이다 —
//! 중성미자 FD 적분이 Python scipy.quad 로 1 ms/호출이라, 완전한 열역사 ODE 가 매 스텝
//! 부르면 궤적당 ~8 초, 스캔 1e4 개면 22 시간이 된다.  여기서 µs 급으로 낮춘다.

pub mod dof;
pub mod dof_table;
pub mod fd;
