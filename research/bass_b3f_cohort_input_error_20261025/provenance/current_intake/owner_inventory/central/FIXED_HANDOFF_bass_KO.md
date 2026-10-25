# cosmosapjw-quantum/bass 인수인계

중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.

첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.

현재 소스 핀·예약·자원 정책(원본 계약 기준):

```json
{
  "numerics/BASS_CONTRACTS.json": {
    "schema": "longterm-scientific-contract.v1",
    "survey_date": "2026-10-23",
    "authority": "parent-assigned Astra scientific framing; implementation delegated only after contract",
    "production": "HOLD",
    "execution": "not_run",
    "resource_policy": {
      "ncp": false,
      "campaign_replay": false,
      "preserve_cumulative_ledger": true,
      "budget_reset": false,
      "new_scoped_local_unit_wall_seconds": 120,
      "existing_campaign_budgets": "preserve immutable run plans; do not infer remaining budget"
    },
    "status_axes": [
      "evidence",
      "execution",
      "claim",
      "publication"
    ],
    "repository": "cosmosapjw-quantum/bass",
    "pins": {
      "chemical_owner": "574c3af93810122af0a7977e00e34195e5251a09",
      "affine_reduction": "797d66580448dad7fc41f2c2db31fe0eb37908bf",
      "fixed_scale_core": "df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e",
      "G1A_science": "b456e218213fda302cf6e5168f8beb608eeb3e1b",
      "G1A_delivery": "ce59a3fd50139a0414d77d5fc493df9d45cd5f49",
      "G1B_contract_only": "90340fb361b0d3570ecf065ebad3487d62b4cf8a"
    },
    "units": {
      "signature": "(-,+,+,+)",
      "tau": "c*t/L",
      "k": "p_phys/Pstar",
      "m": "m_phys*c/Pstar",
      "w": "(8*pi*G/c^4)*L^2*c*Pstar*proper_number_density",
      "q": "c*p/(k_B*T_ref)"
    },
    "source_evidence": [
      "github_evidence.json",
      "SURVEY_HANDOFF.md"
    ]
  }
}
```


## B1-G1B-recover

원본: `numerics/BASS_CONTRACTS.json/nodes/0`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "B1-G1B-recover",
  "depends_on": [],
  "paths": [
    "research/background_kinetic_g1b_20261023/CONTRACT.md",
    "research/background_kinetic_g1b_20261023/"
  ],
  "equations": [
    "f_FD(q)=1/(exp(q)+1)",
    "f_Planck(q)=1/(exp(q)-1)",
    "qbar=I3/I2"
  ],
  "interface": "Restore actual source/test/raw byte manifest from backup; keep fixed continuum normalizers, identify massless-only radial reduction.",
  "acceptance": [
    "Match backup hash/inventory; bind8/8 claim to actual command/source; no reexecution solely for publication",
    "Git90340fb tree contains only contract in new lane"
  ],
  "pr_split": "PR B1 publishes recovered source and evidence receipt only.",
  "positive_claim": "Recover source-qualified S0/S1 continuum construction and finite tests.",
  "remaining": "Implementation and8/8 evidence not in inspected Git; backup intake required.",
  "status": "planned",
  "execution": "not_run",
  "repository": "cosmosapjw-quantum/bass",
  "dependencies": [],
  "source_pins": {
    "chemical_owner": "574c3af93810122af0a7977e00e34195e5251a09",
    "affine_reduction": "797d66580448dad7fc41f2c2db31fe0eb37908bf",
    "fixed_scale_core": "df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e",
    "G1A_science": "b456e218213fda302cf6e5168f8beb608eeb3e1b",
    "G1A_delivery": "ce59a3fd50139a0414d77d5fc493df9d45cd5f49",
    "G1B_contract_only": "90340fb361b0d3570ecf065ebad3487d62b4cf8a"
  },
  "source_refs": [
    "github_evidence.json",
    "SURVEY_HANDOFF.md"
  ],
  "scope": "Recover source-qualified S0/S1 continuum construction and finite tests.",
  "claim_limits": "Implementation and8/8 evidence not in inspected Git; backup intake required.",
  "resource_contract": {
    "ncp": false,
    "campaign_replay": false,
    "preserve_cumulative_ledger": true,
    "budget_reset": false,
    "new_scoped_local_unit_wall_seconds": 120,
    "existing_campaign_budgets": "preserve immutable run plans; do not infer remaining budget"
  },
  "source_status": "source-bound planning; not implemented by this survey"
}
```


## B2-G1B-curved

원본: `numerics/BASS_CONTRACTS.json/nodes/1`. 내부 선행: B1-G1B-recover. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "B2-G1B-curved",
  "depends_on": [
    "B1-G1B-recover"
  ],
  "paths": [
    "research/background_kinetic_g1b_20261023/CONTRACT.md",
    "research/background_kinetic_g1_20261023/kinetic.py",
    "research/background_kinetic_g1_20261023/vendor/core.py"
  ],
  "equations": [
    "kprime=-h*k-sigma*k+R cross k+((a.k)*k-a*k^2-k cross(n*k))/E",
    "logwprime=-3h+2*a.k/E"
  ],
  "interface": "Separate radial orders4/8/12/16 on[0,4,12,24,48], angular mu6/10/14/20/28/40/56,nphi=2*nmu; V/VIII tau0..0.8; independent time refinement; initial h from each discrete density.",
  "acceptance": [
    "Moment/boost/separation<5e-12; normalization<5e-13",
    "Selected fixed-state/grid/time and core/kinetic/rho-flux mismatch<2e-8",
    "Tail target<1e-12 conditional on common field; record denominators; retain coarse failures",
    "Envelope|h|<=2,||sigma||2<=1,|a|<=.5; stop claim if violated"
  ],
  "pr_split": "PR B2 adds new S2 controls, separate errors, audit and full raw outputs.",
  "positive_claim": "Selected smooth-source finite-window convergence with explicit tail/field assumptions.",
  "remaining": "Not nonlinear global tail certification; restore any already executedS2 before allocating new budget.",
  "status": "planned",
  "execution": "not_run",
  "repository": "cosmosapjw-quantum/bass",
  "dependencies": [
    "B1-G1B-recover"
  ],
  "source_pins": {
    "chemical_owner": "574c3af93810122af0a7977e00e34195e5251a09",
    "affine_reduction": "797d66580448dad7fc41f2c2db31fe0eb37908bf",
    "fixed_scale_core": "df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e",
    "G1A_science": "b456e218213fda302cf6e5168f8beb608eeb3e1b",
    "G1A_delivery": "ce59a3fd50139a0414d77d5fc493df9d45cd5f49",
    "G1B_contract_only": "90340fb361b0d3570ecf065ebad3487d62b4cf8a"
  },
  "source_refs": [
    "github_evidence.json",
    "SURVEY_HANDOFF.md"
  ],
  "scope": "Selected smooth-source finite-window convergence with explicit tail/field assumptions.",
  "claim_limits": "Not nonlinear global tail certification; restore any already executedS2 before allocating new budget.",
  "resource_contract": {
    "ncp": false,
    "campaign_replay": false,
    "preserve_cumulative_ledger": true,
    "budget_reset": false,
    "new_scoped_local_unit_wall_seconds": 120,
    "existing_campaign_budgets": "preserve immutable run plans; do not infer remaining budget"
  },
  "source_status": "source-bound planning; not implemented by this survey"
}
```


## B3-fourforce-owner

원본: `numerics/BASS_CONTRACTS.json/nodes/2`. 내부 선행: B2-G1B-curved. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "B3-fourforce-owner",
  "depends_on": [
    "B2-G1B-curved"
  ],
  "paths": [
    "research/background_kinetic_g1_20261023/kinetic.py",
    "research/background_kinetic_g1_20261023/vendor/core.py",
    "research/fourforce_contract_20261023/ (new proposed lane)"
  ],
  "equations": [
    "nabla_a T_s^{ab}=Q_s^b",
    "sum_s Q_s^b=0",
    "T_total=T_matter+T_photon"
  ],
  "interface": "Typed per-sector rho,q_i,p,pi_ij and four-force; owner IDs, frame, units, epoch, provenance. Source-age emission and electron-STF rate remain distinct outputs.",
  "acceptance": [
    "Exact equal/opposite exchange at interface; each component units checked",
    "Source ledger charges each transfer once; existing frozen2e-8 monitors retained",
    "Analytic zero-transfer and two-sector exchange fixtures; positive-domain callback refusal without silent clipping"
  ],
  "pr_split": "PR B3a contract/zero-exchange; B3b single physical exchange owner; B3c coupled bounded test.",
  "positive_claim": "One source-qualified balanced exchange pathway.",
  "remaining": "Full thermal/polarized collision closure remains separate; owner API must be fetched from current REC/HE/REI before implementation.",
  "status": "planned",
  "execution": "not_run",
  "repository": "cosmosapjw-quantum/bass",
  "dependencies": [
    "B2-G1B-curved"
  ],
  "source_pins": {
    "chemical_owner": "574c3af93810122af0a7977e00e34195e5251a09",
    "affine_reduction": "797d66580448dad7fc41f2c2db31fe0eb37908bf",
    "fixed_scale_core": "df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e",
    "G1A_science": "b456e218213fda302cf6e5168f8beb608eeb3e1b",
    "G1A_delivery": "ce59a3fd50139a0414d77d5fc493df9d45cd5f49",
    "G1B_contract_only": "90340fb361b0d3570ecf065ebad3487d62b4cf8a"
  },
  "source_refs": [
    "github_evidence.json",
    "SURVEY_HANDOFF.md"
  ],
  "scope": "One source-qualified balanced exchange pathway.",
  "claim_limits": "Full thermal/polarized collision closure remains separate; owner API must be fetched from current REC/HE/REI before implementation.",
  "resource_contract": {
    "ncp": false,
    "campaign_replay": false,
    "preserve_cumulative_ledger": true,
    "budget_reset": false,
    "new_scoped_local_unit_wall_seconds": 120,
    "existing_campaign_budgets": "preserve immutable run plans; do not infer remaining budget"
  },
  "source_status": "source-bound planning; not implemented by this survey"
}
```


## B4-production-restart

원본: `numerics/BASS_CONTRACTS.json/nodes/3`. 내부 선행: B3-fourforce-owner. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "B4-production-restart",
  "depends_on": [
    "B3-fourforce-owner"
  ],
  "paths": [
    "research/background_kinetic_g1_20261023/vendor/core.py",
    "research/background_production_adapter_20261023/ (new proposed lane)"
  ],
  "equations": [
    "C=Hamiltonian constraint",
    "checkpoint=(tau,state,source_epoch,grid_id,units,ledger,cumulative_budget)"
  ],
  "interface": "Opt-in adapter only; accepted-state transaction; snapshot each species and stress; preserve fixed L across H=0; restart schema rejects mismatched source/frame/grid.",
  "acceptance": [
    "One uninterrupted vs resumed trajectory using identical scientific tolerances",
    "No divided-by-H RHS or hidden normalization",
    "Restarts preserve signed sector stresses, cumulative exchange and budget; reject stale source epoch"
  ],
  "pr_split": "PR B4a schema/adapter; B4b restart parity; activation separate owner decision.",
  "positive_claim": "Restartable fixed-scale selected client.",
  "remaining": "Default dispatch and full physical domain not admitted.",
  "status": "planned",
  "execution": "not_run",
  "repository": "cosmosapjw-quantum/bass",
  "dependencies": [
    "B3-fourforce-owner"
  ],
  "source_pins": {
    "chemical_owner": "574c3af93810122af0a7977e00e34195e5251a09",
    "affine_reduction": "797d66580448dad7fc41f2c2db31fe0eb37908bf",
    "fixed_scale_core": "df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e",
    "G1A_science": "b456e218213fda302cf6e5168f8beb608eeb3e1b",
    "G1A_delivery": "ce59a3fd50139a0414d77d5fc493df9d45cd5f49",
    "G1B_contract_only": "90340fb361b0d3570ecf065ebad3487d62b4cf8a"
  },
  "source_refs": [
    "github_evidence.json",
    "SURVEY_HANDOFF.md"
  ],
  "scope": "Restartable fixed-scale selected client.",
  "claim_limits": "Default dispatch and full physical domain not admitted.",
  "resource_contract": {
    "ncp": false,
    "campaign_replay": false,
    "preserve_cumulative_ledger": true,
    "budget_reset": false,
    "new_scoped_local_unit_wall_seconds": 120,
    "existing_campaign_budgets": "preserve immutable run plans; do not infer remaining budget"
  },
  "source_status": "source-bound planning; not implemented by this survey"
}
```


## B5-domain-validation

원본: `numerics/BASS_CONTRACTS.json/nodes/4`. 내부 선행: B2-G1B-curved, B3-fourforce-owner, B4-production-restart. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "B5-domain-validation",
  "depends_on": [
    "B2-G1B-curved",
    "B3-fourforce-owner",
    "B4-production-restart"
  ],
  "paths": [
    "research/background_domain_validation_20261023/ (new proposed lane)"
  ],
  "equations": [
    "E_total<=E_time+E_radial+E_angular+E_tail+E_source (only with justified stability propagation)"
  ],
  "interface": "Preregister domain/species/anisotropy/mass/window matrix and separate observable errors, physical constraint and moment ledger errors.",
  "acceptance": [
    "Retain G1A wrong-weightV: core4.8901e-12 vs kinetic7.9509e-3/mismatch1.3636e-2 as validation requirement",
    "No production promotion from core constraint alone",
    "New campaign source/input hashes, original denominators and failures; external run only under new explicit budget"
  ],
  "pr_split": "PR B5a protocol; B5b scoped evidence; production scope statement after review.",
  "positive_claim": "Precisely bounded joint physical/numerical admission.",
  "remaining": "Global existence/convergence requires additional mathematics; no blanket claim.",
  "status": "planned",
  "execution": "not_run",
  "repository": "cosmosapjw-quantum/bass",
  "dependencies": [
    "B2-G1B-curved",
    "B3-fourforce-owner",
    "B4-production-restart"
  ],
  "source_pins": {
    "chemical_owner": "574c3af93810122af0a7977e00e34195e5251a09",
    "affine_reduction": "797d66580448dad7fc41f2c2db31fe0eb37908bf",
    "fixed_scale_core": "df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e",
    "G1A_science": "b456e218213fda302cf6e5168f8beb608eeb3e1b",
    "G1A_delivery": "ce59a3fd50139a0414d77d5fc493df9d45cd5f49",
    "G1B_contract_only": "90340fb361b0d3570ecf065ebad3487d62b4cf8a"
  },
  "source_refs": [
    "github_evidence.json",
    "SURVEY_HANDOFF.md"
  ],
  "scope": "Precisely bounded joint physical/numerical admission.",
  "claim_limits": "Global existence/convergence requires additional mathematics; no blanket claim.",
  "resource_contract": {
    "ncp": false,
    "campaign_replay": false,
    "preserve_cumulative_ledger": true,
    "budget_reset": false,
    "new_scoped_local_unit_wall_seconds": 120,
    "existing_campaign_budgets": "preserve immutable run plans; do not infer remaining budget"
  },
  "source_status": "source-bound planning; not implemented by this survey"
}
```


## 저장소 간 조건부 연결

채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.


- `B3-fourforce-owner` → `REI-L4`: selecting BASS four-force geometry feedback adapter. Closed sum of sectors in matching frame/clock; signed stresses retained


- `B2-G1B-curved` → `REI-L5`: claiming curved Bianchi smooth-source domain. Not a prerequisite to all LRS selected flat pilots
