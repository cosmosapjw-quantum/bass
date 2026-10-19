# S7 원래 run01: 결합 중력 벤치마크와 각도 분해능

이 그림은 저장된 **원래 run01** 결과만 읽어 그렸다. 이후의 정확 유리수 moment 진단이나 더 엄격한 내부 정지조건을 사용한 후속 실행은 이 그림의 판정과 점을 대체하지 않는다. 그림 제작 과정에서는 kernel, KL projection, ODE, native transport를 다시 실행하지 않았다. 원본 4개 파일의 실제 경로·크기·SHA-256, 표시한 모든 점, 표시하지 않은 시험의 목록은 `FIGURE_PROVENANCE.json`과 `PLOT_DATA_RUN01.json`에 있다.

## 게시용 캡션

**그림 S7. 비등방 복사 응답, 동역학, 각도 분해능의 서로 다른 검증.**
**A:** 복사만 있는 결합 Einstein–collisionless 계에서 (q=s/H), 
\(\mathcal{A}=\Delta P/U\)의 비선형 궤적(실선)과 선형 벤치마크(점선)를 비교했다. 초기 섭동은 \(q(0)=\mathcal{A}(0)=\epsilon\)이다. 본 곡선은 \(\epsilon=0.01\)이며 두 변수를 \(\epsilon\)으로 나누었다. 작은 그림은 \(\epsilon=0.01,0.005,0.0025\)의 저장된 최대 절대 오차를 표시한다. 회색 점선은 첫 오차에 고정한 \(O(\epsilon^2)\) 안내선으로, 자료에 적합한 회귀선이 아니다. 오차비는 각각 **3.9908, 3.9953**이다.
**B:** 양의 donor에서 동일한 64개 midpoint birth를 생성하는 결합 우주론에서 각도 prior, P2, P2/P4 보정을 비교했다. 세로축은 같은 birth 일정의 source-frame GL128 참조에 대한 \(\max_x|y-y_{\rm GL128}|\), \(y=s/H_*\)이다. \(y\)는 패널 A의 \(q=s/H\)와 다르다. 각 \(b_0\)에서 가로 방향은 \(n_\mu=8,16,32\)의 각도 분해능 변화이며, 같은 가로 위치의 세 기호가 moment 제약의 변화를 나타낸다. 각도 조합 27개 모두를 표시했다. 측정된 궤적 19개와 양의 지지 실패 8개이다.
**C:** native의 prescribed history, 동일한 16개 birth에서 \(|\mathcal{A}-\mathcal{A}_{\rm iso}|\)를 비교했다. 각도 조합 27개는 측정 18개와 양의 지지 실패 9개이다. 붉은 점선은 사전에 정한 large-\(b\) 각도 목표 \(10^{-6}\)이다. \(b_0=0.6,n_\mu=32\)의 P2/P4 결과는 **\(9.945297565870925\times10^{-4}\)**로 이 목표를 통과하지 못했다.
각 패널 위의 별도 회색 띠 안 ×는 양의 moment 해가 없는 지지이며, 수치 오차 값을 임의로 배정하지 않았다. 붉은 빈 원은 원래 run01의 해당 측정점에 기록된 gate 실패를 보존한다. \(b_0\)는 고정 좌표 격자의 기준 offset을 뜻하며 물리적 shear가 아니다. 두 각도 패널은 서로 다른 source 모델·관측량·geometry history이므로 절대 오차의 직접 우열 비교에 쓰지 않는다.

## 수치 해석과 판정 범위

복사 선형 벤치마크의 최대 오차는 \(3.887033223408387\times10^{-5}\), \(9.740044227717244\times10^{-6}\), \(2.4378494192866347\times10^{-6}\)이었다. 이 순서는 저장된 \(\epsilon\)의 내림차순이다. 그림은 사전에 유도한 선형 행렬 \([[-1,1],[-8/5,0]]\)에 대한 유한 섭동 오차가 해당 세 점에서 2차로 감소함을 보여 준다. P2-only quadrature의 가능한 전체 선형 스펙트럼을 직접 측정했다는 뜻은 아니다.

결합 각도 시험에서 \(b_0=0.3,n_\mu=16\)의 prior/P2/P2P4 오차는 각각 \(1.81809\times10^{-6}\), \(1.29187\times10^{-7}\), \(1.53085\times10^{-8}\)이다. 같은 분해능에서 제약을 추가한 효과와 각도 수를 늘린 효과를 구분할 수 있다. \(b_0=0.7,n_\mu=32\)에서도 P2/P4 결과 \(5.21151\times10^{-7}\)를 실제로 얻었다. 다른 지지에서의 실패는 그대로 남는다. \(b_0=0.9,n_\mu=32\)의 P2/P4에는 결과 값을 외삽하지 않았다.

Native의 \(b_0=0,n_\mu=32\) 오차는 약 \(2.4\times10^{-16}\)으로 해당 계산의 부동소수점 수준이다. 이 세 점으로 일반적인 continuum 수렴 차수를 적합하지 않았다. 고정 격자 offset을 바꾼 \(b_0=0.6\)에서는 \(n_\mu=32\)의 P2/P4가 P2보다 작은 오차를 보이지만 \(10^{-6}\) 목표는 실패했다. Moment 일치가 유한 shear history의 continuum angular accuracy를 자동 승인하지 않는 구체적인 사례이다. 또한 이 그림은 native finite-bin photon/energy 보존 gate를 대신하지 않는다.

## 보존한 실패와 그림 밖 시험

원래 결합 run01의 전체 기록은 **36개 시도, 28개 측정, 8개 지지 실패, 전체 FAIL**이다. 패널 B의 붉은 원은 `b03_n8_P2_K64`와 `b03_n32_P24_K64`의 `birth_moments` gate 실패이다. 전체 28개 측정 중 나머지 9개 참조·birth refinement 이력은 각도 비교 축에 중복하여 그리지 않았다. Isotropic donor 벤치마크와 birth refinement 자체의 판정도 이 그림에는 포함하지 않았다.

원래 native 기록은 **51개 시도, 42개 측정, 9개 지지 실패**, 상태는 `COMPLETED_WITH_RETAINED_GATE_FAILURES`이다. 패널 C에서 표시한 `angular_017`의 목표 실패 외에 다음 기록은 각도 block 밖에 있으므로 별도로 명시한다.

- `birth_time_031`: `MOMENTS` 실패. 원래 observer의 P2 값은 \(-3.0080105073437835\times10^{-15}\)이다. 같은 기록의 P4 값은 P2-only 제약의 승인 기준으로 바꾸어 해석하지 않는다.
- `slab_large_b_050`: `LARGE_B_ANGULAR_ACCURACY_TARGET` 실패. 원래 부호 있는 오차는 \(-9.945297565871203\times10^{-4}\)이다.
- 총 24개의 native 비각도 측정은 birth time, spectral panel, energy bin, slab 검증이다. 이들의 case ID 전체를 provenance에 보존했다.

붉은 원을 따로 붙이지 않은 prior/P2 비교점까지 모두 \(10^{-6}\) 승인 대상이었다는 뜻은 아니다. 붉은 선은 지정된 large-\(b\) 목표를 보여 주며, 붉은 원은 원본 receipt의 실제 gate 판정에만 대응한다. 원래 observer의 경계 실패를 이후 진단만으로 PASS로 덮어쓰지 않는다.

이 자료의 닫힌 donor 계는 에너지를 일관되게 이전하는 manufactured 검증이며 MD14 source의 물리적 에너지 예산을 승인하지 않는다. Native 패널은 prescribed background이며 결합 native Einstein 실행이나 reactive EoR history가 아니다. REI production, full EoR 또는 기존 owner 변경의 승인 범위를 넓히지 않는다.

## 파일과 재현

- `S7_SUMMARY_RUN01.svg` / `.png`: 폭 7.2 inch의 통합 세 패널. 약 180 mm의 두 단 폭 게시용이다.
- `S7_RADIATION_LINEAR_SINGLE_COLUMN.svg` / `.png`: 폭 3.54 inch의 복사 benchmark와 별도 오차 축.
- `S7_COUPLED_ANGULAR_SINGLE_COLUMN.svg` / `.png`, `S7_NATIVE_ANGULAR_SINGLE_COLUMN.svg` / `.png`: 폭 3.54 inch의 세로 facet. 약 90 mm의 한 단 폭 게시용이다.
- `sourceplot.py`: Matplotlib의 Agg backend로 저장된 측정만 읽는다. `python3 sourceplot.py --data PLOT_DATA_RUN01.json --out /tmp/bass-s7-figure-reproduction`으로 standalone 재현할 수 있다. 원본 solver는 호출하지 않는다.

SVG는 편집 가능한 text를 유지하고 PNG는 220 dpi이다. 영어 축·범례를 사용하여 한국어 폰트 유무에 따른 글리프 누락을 피했다. 실제 PNG 시각 readback과 수정 이력은 `FIGURE_AUDIT.json`에 기록했다.
