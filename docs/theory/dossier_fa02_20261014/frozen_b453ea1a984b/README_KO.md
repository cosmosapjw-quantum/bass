# FA-02 · 고정 cap의 rapidity/pointing 접선

새 결과의 범위는 exact Kasner p=(2/3,2/3,-1/3), x in [.5,1], |chi|,|psi|<=.02, cap delta<=.02 및 고정 energy band [.98,1.02] E_star다. Physical observer boost는 e1, pointing은 e3 회전, analyzer는 각 ray에 투영한 고정 e2다.

FA.25를 고정 observer label로 되당겨 solid-angle Jacobian과 boundary를 함께 처리하고, energy·screen·analyzer의 first/second/mixed derivatives를 구현했다. 실제 입력의 complex bidisk majorant로 exact Taylor coefficient 기준 remainder를 증명했다:

- first-order remainder <=125 norm(h,infty)^2
- second-order remainder <=1250 norm(h,infty)^3

a=(.008,.010), h=(r,-r/2), r=.008,.004,.002에서 직접 계산의 second-order matrix trace residual은 8.95569e-8,1.12347e-8,1.40685e-9다. 비는 7.97146,7.98572로 cubic scaling에 접근한다. 이는 수렴 비교이고 interval-certified continuum run은 아니다. Unknown empirical errors remain null.

근거: 직접 유도, 실제 새 Wolfram6 zero groups와 xAct8 tensor groups, 국소 검사48, owner delta review. External independent review remains pending. 원래 21/21,D9.1,FA01은 보존한다.

## 재현

Python3와 NumPy가 필요하다. 기존 결과를 별도 복사해 두고 실행한다.

```bash
python runtime/fa02.py --mode jetoff --steps 512 --nr 10 --nphi 24
python runtime/fa02.py --mode finite --steps 512 --nr 10 --nphi 24
```

코드는 새 parameter derivatives만 계산한다. 기존 PNS/AP/F-N-STIM 캠페인을 호출하지 않는다. 이 payload의 remote 게시 여부는 같은 archive의 publication receipt를 따른다. 로컬 파일의 존재나 이 README 자체는 게시 성공의 증거가 아니다.
