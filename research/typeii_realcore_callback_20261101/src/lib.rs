//! Narrow source-bound test crate; never classify as full _rustcore Cargo PASS.
//! Test modules are exactly the owner files, not reimplemented stand-ins.
#[path = "../../../_rustcore/src/core/conventions.rs"]
pub mod original_conventions;
pub mod core {
    pub use crate::original_conventions as conventions;
}

#[path = "../../../_rustcore/src/geom/group.rs"]
pub mod original_group;
pub mod geom {
    pub use crate::original_group as group;
}

#[path = "../../../_rustcore/src/runtime/typeii_host.rs"]
pub mod original_typeii_host;
pub mod runtime {
    pub use crate::original_typeii_host as typeii_host;
}
