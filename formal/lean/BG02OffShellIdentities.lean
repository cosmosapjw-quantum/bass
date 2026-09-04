import Mathlib

namespace BASS.BG02

def Hres (R3 H sigma2 Lambda kappaG rho : ℚ) : ℚ :=
  (R3 + 6 * H^2 - sigma2 - 2 * Lambda - 2 * kappaG * rho) / 2

def Ftrace (R3 H sigma2 divA A2 Lambda kappaG p : ℚ) : ℚ :=
  -R3/12 - 3*H^2/2 - sigma2/4 + (divA+A2)/3 + Lambda/2 - kappaG*p/2

def FADM (R3 H divA A2 Lambda kappaG rho p : ℚ) : ℚ :=
  -R3/3 - 3*H^2 + (divA+A2)/3 + kappaG*(rho-p)/2 + Lambda

def FRay (H sigma2 divA A2 Lambda kappaG rho p : ℚ) : ℚ :=
  -H^2 - sigma2/3 + (divA+A2)/3 - kappaG*(rho+3*p)/6 + Lambda/3

theorem adm_trace_identity
    (R3 H sigma2 divA A2 Lambda kappaG rho p : ℚ) :
    FADM R3 H divA A2 Lambda kappaG rho p
      - Ftrace R3 H sigma2 divA A2 Lambda kappaG p
      + Hres R3 H sigma2 Lambda kappaG rho / 2 = 0 := by
  simp [FADM, Ftrace, Hres]
  ring

theorem trace_ray_identity
    (R3 H sigma2 divA A2 Lambda kappaG rho p : ℚ) :
    Ftrace R3 H sigma2 divA A2 Lambda kappaG p
      - FRay H sigma2 divA A2 Lambda kappaG rho p
      + Hres R3 H sigma2 Lambda kappaG rho / 6 = 0 := by
  simp [Ftrace, FRay, Hres]
  ring

theorem adm_ray_identity
    (R3 H sigma2 divA A2 Lambda kappaG rho p : ℚ) :
    FADM R3 H divA A2 Lambda kappaG rho p
      - FRay H sigma2 divA A2 Lambda kappaG rho p
      + 2 * Hres R3 H sigma2 Lambda kappaG rho / 3 = 0 := by
  simp [FADM, FRay, Hres]
  ring

end BASS.BG02
