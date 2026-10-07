# BASS–REI bridge 독립 판정

**CONFIRMED — scoped snapshot/controlled-history bridge를 다음 개발의 입력으로 사용할 수 있다.** 변경 source·tests·oracle·실제 실행 로그를 독립적으로 읽었고, 현재 변경에 대한 material finding 및 open blocker는 0이다. 이 검토자는 생산 코드와 oracle을 작성하지 않았으며 새 과학 실행을 추가하지 않았다.

실제 REI `HHeModel`/`HHeState`의 전체 source 유효성 검증을 거쳐 proper 핵밀도에 10⁶을 한 번 적용하고, BASS `ElectronState`의 HII + HeII + 2 HeIII 전자수 정의를 재사용한다. 기존 `ElectronState`가 ray factor D=γ(1−β·e)를 한 번 적용한다. source의 c 값이나 atomic clock 1/γ를 가져와 rate를 변형하지 않는다. 중성인 경우에도 잘못된 방향과 변환 overflow는 거절한다.

FT03 adapter는 의도적으로 density-only다. 외부로부터 받은 유효한 species snapshot의 전자밀도에 FT03 원자율 온도 범위를 추가하지 않는다. 이 인터페이스를 FT03 RHS admission으로 해석하면 안 된다. 이번 실제 history는 별도로 `ft03_adaptive_step`을 호출하므로 원래의 온도·잔차·local-error gate를 유지한다. 초기에 검토자가 제시한 ‘밀도 추출에도 FT03 RHS 필요’라는 더 강한 가정은 frozen contract를 읽고 철회했다.

검증은 scoped native 20개(새 focused 10개, API 존재 1개, 기존 visibility 6개, legacy REI/정확 pin 3개), 독립 Decimal-70 snapshot 786 assertions/140 native calls, 실제 두 FT03 history에 대한 22,029 assertions다. 논리 assertion 수를 독립 물리 시나리오 수로 읽지 않는다. 1000·2000 step 두 history는 같은 초기조건의 static controlled FT03이며, finer-grid 추가 Thomson depth는 2.2336042110622×10⁻⁴다. paired-grid survival 차이 6.5168602×10⁻⁹는 같은 observer tail을 갖는 두 discrete opacity history의 L1 map bound 안에 있다. 이것은 연속 FT03 해에 대한 uniform enclosure나 측정된 수렴차수가 아니다.

finite interval의 확률 항등식은 ΣPᵢ+S₀=exp(−τ_tail)이다. 입력은 caller-owned normal time이며 conformal clock, comoving density, volume filling factor Q를 자동 추론하지 않는다. Cold-Thomson approximation의 수학적 coefficient/history map을 검증했으며 finite-T/KN certificate, scalar-Q collision generator, 전체 Bianchi polarized transport를 승격하지 않는다. RCT는 OFF, upstream HE/CR/HH의 기존 열린 gate도 그대로다.

실제 host source 파일을 path import하고 exact materialized REI dependency를 사용한 **scoped build**를 확인했다. 전체 BASS crate, 원격 Cargo Git fetch, REC runtime suite는 실행하지 않았다. 기존 seven REI dispatch는 retained이고 관련 group_rates/lift/coverage 파일도 old/new pin 사이 byte-identical이다. 8 final evidence identity와 host 22개·REI 34개 materialization hash가 현재 파일과 일치한다.

게시할 additive current receipt는 과거 CHILD_DEPENDENCY_LOCK의 pin을 역사 기록으로 남기면서 이번 41e4592… native pin이 현재 입력임을 명시하면 된다. 이번 science/code review를 재귀적으로 반복할 이유는 없다. 최종 GitHub/백업 ACK는 owner delivery 단계에서 확인한다.
