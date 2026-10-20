# S12 결과 그림 독립 검토

검토자는 그림 작성자와 다른 `c9_review_finish`이다. 최종 PNG를 직접 열어 제목·축·눈금·범례·각주의 가독성과 겹침을 확인했고, 원자료 5개와 그림 산출물 4개의 바이트·SHA256을 대조했다. 저장된 수치에서 timing ratio, paired median, IQR, Richardson 차이, omission 차이를 독립적으로 다시 계산하여 CSV 30행과 비교했다. **79/79 PASS_SCOPED**이다. 이 수는 기존 독립 물리 검토 585개에 더하지 않는다.

상단의 NCP64 `NOT RUN`, A의 7쌍·warmup 2쌍, B의 3쌍·warmup 1쌍 및 4-case/2-worker 범위가 정확하다. IQR은 신뢰구간으로 표시하지 않았다. B는 process/file 비용을 포함한 전체 batch wall time이다.

C의 세 omission 막대는 `omitted_vs_Richardson_max_absolute`이다. 본문에서 사용할 수 있는 `full_vs_omitted_max_absolute`와 약간 다른 통계이며, 둘을 같은 값으로 쓰면 안 된다. 세 omission control의 내부 수치 gate와 full scientific status는 모두 실패로 유지한다. full tangent의 fine Richardson 최대 절대차는 7.923659645081571e-11이다.

D는 완료된 원 native `b9_n64_prior`의 저장 support만 그린다. 양의 P2/P4 해에 필요한 `Z=max μ² ≥ 3/5`를 충분조건으로 해석하지 않았다. birth 13부터 원 tolerance에서 불가능하다는 판단은 별도 exact full-polygon certificate와 함께 읽는다. 새 Rust extended n64 case 전체나 continuum에 대한 주장이 아니다.

첫 렌더 후 `make_figure.py`가 재렌더할 때 이전 FIGURE_MANIFEST.json을 산출물로 포함할 수 있다는 재현성 문제를 지적했다. root가 manifest 자체를 제외하도록 수정했고, 최종 manifest로 재검토했다. PNG와 CSV 바이트는 첫 렌더와 같으며 PDF/SVG의 최종 직렬화 해시는 새 manifest와 일치한다. 첫 검토 원본은 `first_render_review/`에 보존했다.

검토 과정의 compiler, ODE, benchmark, projector, native history, 완료 campaign 재실행은 모두 0회이다. 이 승인은 저장된 데이터와 그림 표현의 범위에 한정되며 actual MD14/shared-Q, full native spectral history, continuum 또는 full EoR 완료를 의미하지 않는다.
