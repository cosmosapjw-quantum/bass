#!/usr/bin/env python3
"""Prepare an opt-in geometry-only candidate from the pinned native source."""
from pathlib import Path
import argparse,hashlib,shutil,difflib,json
EXPECTED='65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254'
TYPES='''
// BASS AX11: per-immutable-model exact f64-key reuse; not an interpolant.
use std::sync::{Arc, Mutex};
use std::time::Instant;
#[derive(Clone, Copy, Debug, Default)]
pub struct ExactReuseProfile {
    pub calls: u64,
    pub misses: u64,
    pub hits: u64,
    pub reference_hits: u64,
    pub quadrature_ns: u128,
    pub cache_ns: u128,
}
#[derive(Debug, Default)]
struct ExactReuseState {
    enabled: bool,
    reference: Option<BackgroundPoint>,
    recent: [Option<BackgroundPoint>; 16],
    cursor: usize,
    profile: ExactReuseProfile,
}
'''
METHODS='''    /// Opt-in execution setting only. Model/source/cosmology are immutable.
    /// Clones share this bounded cache and its profile, never another model's.
    pub fn configure_exact_reuse(&self, enabled: bool) -> Result<(), ForwardError> {
        let mut state = self.exact_reuse.lock().map_err(|_| invalid("AxbiCachePoisoned"))?;
        *state = ExactReuseState { enabled, ..ExactReuseState::default() };
        Ok(())
    }
    pub fn exact_reuse_profile(&self) -> Result<ExactReuseProfile, ForwardError> {
        Ok(self.exact_reuse.lock().map_err(|_| invalid("AxbiCachePoisoned"))?.profile)
    }
    pub fn point_at_scale(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {
        // Preserve the original error ordering before any cache lookup.
        positive(a)?;
        if a < self.a_ref || a > self.a_end { return Err(invalid("AxbiScaleDomain")); }
        let started = Instant::now();
        {
            let mut state = self.exact_reuse.lock().map_err(|_| invalid("AxbiCachePoisoned"))?;
            state.profile.calls += 1;
            if state.enabled {
                let is_reference = a.to_bits() == self.a_ref.to_bits();
                let found = if is_reference { state.reference } else {
                    state.recent.iter().flatten().find(|p| p.a.to_bits() == a.to_bits()).copied()
                };
                if let Some(point) = found {
                    state.profile.hits += 1;
                    if is_reference { state.profile.reference_hits += 1; }
                    state.profile.cache_ns += started.elapsed().as_nanos();
                    return Ok(point);
                }
            }
        }
        let quadrature = Instant::now();
        let result = self.point_at_scale_uncached(a);
        let quadrature_ns = quadrature.elapsed().as_nanos();
        {
            let mut state = self.exact_reuse.lock().map_err(|_| invalid("AxbiCachePoisoned"))?;
            state.profile.misses += 1;
            state.profile.quadrature_ns += quadrature_ns;
            if state.enabled {
                if let Ok(point) = &result {
                    if a.to_bits() == self.a_ref.to_bits() { state.reference = Some(*point); }
                    else {
                        let slot = state.cursor;
                        state.recent[slot] = Some(*point);
                        state.cursor = (slot + 1) % state.recent.len();
                    }
                }
            }
            state.profile.cache_ns += started.elapsed().as_nanos().saturating_sub(quadrature_ns);
        }
        result
    }
'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--unit',type=Path,required=True);a=ap.parse_args()
 source=a.original/'rust/rei_microphysics/src/axbi_background.rs';raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise SystemExit('ORIGINAL_BACKGROUND_SHA_MISMATCH')
 if a.candidate.exists():raise SystemExit('CANDIDATE_EXISTS_NO_OVERWRITE')
 shutil.copytree(a.original,a.candidate,ignore=shutil.ignore_patterns('target'))
 s=raw.decode();old=s
 marker='#[derive(Clone, Debug)]\npub struct AxbiBackground {'
 if s.count(marker)!=1:raise SystemExit('AMBIGUOUS_BACKGROUND')
 s=s.replace(marker,TYPES+'\n'+marker)
 s=s.replace('    panels: usize,\n}\nimpl AxbiBackground {','    panels: usize,\n    exact_reuse: Arc<Mutex<ExactReuseState>>,\n}\nimpl AxbiBackground {',1)
 s=s.replace('            panels,\n        };','            panels,\n            exact_reuse: Arc::new(Mutex::new(ExactReuseState::default())),\n        };',1)
 signature='    pub fn point_at_scale(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {'
 if s.count(signature)!=1:raise SystemExit('POINT_SIGNATURE_NOT_UNIQUE')
 s=s.replace(signature,METHODS+'    fn point_at_scale_uncached(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {',1)
 oldbody=old.split(signature,1)[1].split('    pub fn point_at_time',1)[0]
 newbody=s.split('    fn point_at_scale_uncached(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {',1)[1].split('    pub fn point_at_time',1)[0]
 assert oldbody==newbody,'QUADRATURE_ARITHMETIC_CHANGED'
 dest=a.candidate/'rust/rei_microphysics/src/axbi_background.rs';dest.write_text(s)
 (dest.parent/'bass_ax11_reference_background.rs').write_bytes(raw)
 patch=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/rust/rei_microphysics/src/axbi_background.rs',tofile='b/rust/rei_microphysics/src/axbi_background.rs'))
 (a.unit/'owner_geometry_only.patch').write_text(patch)
 record={'original_background_sha256':EXPECTED,'candidate_background_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'original_quadrature_body_byte_identical':True,'quadrature_panels':4096,'quadrature_nodes':4097,'a_ref_not_shortcut':True,'cache_slots':16,'pinned_reference_extra_slot':1,'default_enabled':False,'key':'exact f64::to_bits within complete immutable model instance','source_owner_mutation':False,'patch_target':'rei_bianchi AX11 native axbi_background only'}
 (a.unit/'results/CANDIDATE_SOURCE.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
main()
