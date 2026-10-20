# Simd in pulp - Rust
URL: https://docs.rs/pulp/0.22.3/pulp/trait.Simd.html

Simd in pulp - Rust

Source 

pub trait Simd: Seal + Debug + Copy + Send + Sync + 'static { 

Show 448 associated items

 type m8s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type i8s: Debug + Copy + Send + Sync + Pod + 'static; type u8s: Debug + Copy + Send + Sync + Pod + 'static; type m16s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type i16s: Debug + Copy + Send + Sync + Pod + 'static; type u16s: Debug + Copy + Send + Sync + Pod + 'static; type m32s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type f32s: Debug + Copy + Send + Sync + Pod + 'static; type c32s: Debug + Copy + Send + Sync + Pod + 'static; type i32s: Debug + Copy + Send + Sync + Pod + 'static; type u32s: Debug + Copy + Send + Sync + Pod + 'static; type m64s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static; type f64s: Debug + Copy + Send + Sync + Pod + 'static; type c64s: Debug + Copy + Send + Sync + Pod + 'static; type i64s: Debug + Copy + Send + Sync + Pod + 'static; type u64s: Debug + Copy + Send + Sync + Pod + 'static; const REGISTER_COUNT: usize; const IS_SCALAR: bool = false; const M64_LANES: usize = _; const U64_LANES: usize = _; const I64_LANES: usize = _; const F64_LANES: usize = _; const C64_LANES: usize = _; const M32_LANES: usize = _; const U32_LANES: usize = _; const I32_LANES: usize = _; const F32_LANES: usize = _; const C32_LANES: usize = _; const M16_LANES: usize = _; const U16_LANES: usize = _; const I16_LANES: usize = _; const M8_LANES: usize = _; const U8_LANES: usize = _; const I8_LANES: usize = _; // Required methods fn abs2_c32s(self, a: Self:: c32s) -> Self:: c32s; fn abs2_c64s(self, a: Self:: c64s) -> Self:: c64s; fn abs_max_c32s(self, a: Self:: c32s) -> Self:: c32s; fn abs_max_c64s(self, a: Self:: c64s) -> Self:: c64s; fn add_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn add_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; fn add_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn add_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn add_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn add_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn add_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn add_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn sub_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn sub_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; fn sub_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn sub_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn sub_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn sub_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s; fn sub_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn sub_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn sub_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn sub_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn sub_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn sub_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn mul_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn mul_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; fn mul_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn mul_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn mul_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn mul_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn mul_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn mul_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn mul_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn mul_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn div_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn div_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn equal_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: m32s; fn equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn equal_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: m64s; fn equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn greater_than_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn greater_than_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn greater_than_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn greater_than_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s; fn greater_than_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn greater_than_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s; fn greater_than_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn greater_than_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s; fn greater_than_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn greater_than_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn greater_than_or_equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn greater_than_or_equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn greater_than_or_equal_u16s( self, a: Self:: u16s, b: Self:: u16s, ) -> Self:: m16s; fn greater_than_or_equal_i16s( self, a: Self:: i16s, b: Self:: i16s, ) -> Self:: m16s; fn greater_than_or_equal_u32s( self, a: Self:: u32s, b: Self:: u32s, ) -> Self:: m32s; fn greater_than_or_equal_i32s( self, a: Self:: i32s, b: Self:: i32s, ) -> Self:: m32s; fn greater_than_or_equal_u64s( self, a: Self:: u64s, b: Self:: u64s, ) -> Self:: m64s; fn greater_than_or_equal_i64s( self, a: Self:: i64s, b: Self:: i64s, ) -> Self:: m64s; fn greater_than_or_equal_f32s( self, a: Self:: f32s, b: Self:: f32s, ) -> Self:: m32s; fn greater_than_or_equal_f64s( self, a: Self:: f64s, b: Self:: f64s, ) -> Self:: m64s; fn less_than_or_equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn less_than_or_equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn less_than_or_equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn less_than_or_equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s; fn less_than_or_equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn less_than_or_equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s; fn less_than_or_equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn less_than_or_equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s; fn less_than_or_equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn less_than_or_equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn less_than_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s; fn less_than_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s; fn less_than_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s; fn less_than_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s; fn less_than_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s; fn less_than_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s; fn less_than_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s; fn less_than_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s; fn less_than_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s; fn less_than_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s; fn and_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn and_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn and_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn and_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn or_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn or_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn or_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn or_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn xor_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn xor_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn xor_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn xor_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn min_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn min_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn min_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn min_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s; fn min_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn min_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn min_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn min_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn min_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn min_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn max_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s; fn max_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s; fn max_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s; fn max_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s; fn max_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s; fn max_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s; fn max_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s; fn max_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s; fn max_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s; fn max_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s; fn neg_c32s(self, a: Self:: c32s) -> Self:: c32s; fn neg_c64s(self, a: Self:: c64s) -> Self:: c64s; fn not_m8s(self, a: Self:: m8s) -> Self:: m8s; fn not_u8s(self, a: Self:: u8s) -> Self:: u8s; fn not_m16s(self, a: Self:: m16s) -> Self:: m16s; fn not_u16s(self, a: Self:: u16s) -> Self:: u16s; fn not_m32s(self, a: Self:: m32s) -> Self:: m32s; fn not_u32s(self, a: Self:: u32s) -> Self:: u32s; fn not_m64s(self, a: Self:: m64s) -> Self:: m64s; fn not_u64s(self, a: Self:: u64s) -> Self:: u64s; fn splat_u8s(self, value: u8) -> Self:: u8s; fn splat_i8s(self, value: i8) -> Self:: i8s; fn splat_u16s(self, value: u16) -> Self:: u16s; fn splat_i16s(self, value: i16) -> Self:: i16s; fn splat_u32s(self, value: u32) -> Self:: u32s; fn splat_i32s(self, value: i32) -> Self:: i32s; fn splat_u64s(self, value: u64) -> Self:: u64s; fn splat_i64s(self, value: i64) -> Self:: i64s; fn splat_c32s(self, value: c32) -> Self:: c32s; fn splat_f32s(self, value: f32) -> Self:: f32s; fn splat_c64s(self, value: c64) -> Self:: c64s; fn splat_f64s(self, value: f64) -> Self:: f64s; fn sqrt_f32s(self, a: Self:: f32s) -> Self:: f32s; fn sqrt_f64s(self, a: Self:: f64s) -> Self:: f64s; fn conj_c32s(self, a: Self:: c32s) -> Self:: c32s; fn conj_c64s(self, a: Self:: c64s) -> Self:: c64s; fn conj_mul_add_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s; fn conj_mul_add_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s; fn conj_mul_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s; fn conj_mul_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s; unsafe fn mask_load_ptr_c32s( self, mask: MemMask, ptr: *const c32, ) -> Self:: c32s; unsafe fn mask_load_ptr_c64s( self, mask: MemMask, ptr: *const c64, ) -> Self:: c64s; unsafe fn mask_load_ptr_u8s( self, mask: MemMask, ptr: *const u8, ) -> Self:: u8s; unsafe fn mask_load_ptr_u16s( self, mask: MemMask, ptr: *const u16, ) -> Self:: u16s; unsafe fn mask_load_ptr_u32s( self, mask: MemMask, ptr: *const u32, ) -> Self:: u32s; unsafe fn mask_load_ptr_u64s( self, mask: MemMask, ptr: *const u64, ) -> Self:: u64s; unsafe fn mask_store_ptr_c32s( self, mask: MemMask, ptr: *mut c32, values: Self:: c32s, ); unsafe fn mask_store_ptr_c64s( self, mask: MemMask, ptr: *mut c64, values: Self:: c64s, ); unsafe fn mask_store_ptr_u8s( self, mask: MemMask, ptr: *mut u8, values: Self:: u8s, ); unsafe fn mask_store_ptr_u16s( self, mask: MemMask, ptr: *mut u16, values: Self:: u16s, ); unsafe fn mask_store_ptr_u32s( self, mask: MemMask, ptr: *mut u32, values: Self:: u32s, ); unsafe fn mask_store_ptr_u64s( self, mask: MemMask, ptr: *mut u64, values: Self:: u64s, ); fn mul_add_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s; fn mul_add_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s; fn mul_add_e_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s; fn mul_add_e_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s; fn mul_add_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s; fn mul_add_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s; fn reduce_max_c32s(self, a: Self:: c32s) -> c32; fn reduce_max_c64s(self, a: Self:: c64s) -> c64; fn reduce_max_f32s(self, a: Self:: f32s) -> f32; fn reduce_max_f64s(self, a: Self:: f64s) -> f64; fn reduce_min_c32s(self, a: Self:: c32s) -> c32; fn reduce_min_c64s(self, a: Self:: c64s) -> c64; fn reduce_min_f32s(self, a: Self:: f32s) -> f32; fn reduce_min_f64s(self, a: Self:: f64s) -> f64; fn reduce_product_f32s(self, a: Self:: f32s) -> f32; fn reduce_product_f64s(self, a: Self:: f64s) -> f64; fn reduce_sum_c32s(self, a: Self:: c32s) -> c32; fn reduce_sum_c64s(self, a: Self:: c64s) -> c64; fn reduce_sum_f32s(self, a: Self:: f32s) -> f32; fn reduce_sum_f64s(self, a: Self:: f64s) -> f64; fn rotate_right_c32s(self, a: Self:: c32s, amount: usize) -> Self:: c32s; fn rotate_right_c64s(self, a: Self:: c64s, amount: usize) -> Self:: c64s; fn rotate_right_u32s(self, a: Self:: u32s, amount: usize) -> Self:: u32s; fn rotate_right_u64s(self, a: Self:: u64s, amount: usize) -> Self:: u64s; fn select_u32s( self, mask: Self:: m32s, if_true: Self:: u32s, if_false: Self:: u32s, ) -> Self:: u32s; fn select_u64s( self, mask: Self:: m64s, if_true: Self:: u64s, if_false: Self:: u64s, ) -> Self:: u64s; fn swap_re_im_c32s(self, a: Self:: c32s) -> Self:: c32s; fn swap_re_im_c64s(self, a: Self:: c64s) -> Self:: c64s; fn vectorize (self, op: Op) -> Op:: Output; fn widening_mul_u32s( self, a: Self:: u32s, b: Self:: u32s, ) -> (Self:: u32s, Self:: u32s); fn wrapping_dyn_shl_u32s( self, a: Self:: u32s, amount: Self:: u32s, ) -> Self:: u32s; fn wrapping_dyn_shr_u32s( self, a: Self:: u32s, amount: Self:: u32s, ) -> Self:: u32s; // Provided methods fn abs_f32s(self, a: Self:: f32s) -> Self:: f32s { ... } fn abs_f64s(self, a: Self:: f64s) -> Self:: f64s { ... } fn and_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn and_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn and_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn and_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn and_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn and_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn and_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn and_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn and_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s { ... } fn and_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s { ... } fn or_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn or_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn or_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn or_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn or_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn or_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn or_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn or_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn or_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s { ... } fn or_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s { ... } fn xor_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn xor_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn xor_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn xor_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn xor_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn xor_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn xor_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn xor_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn xor_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s { ... } fn xor_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s { ... } fn add_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s { ... } fn add_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s { ... } fn add_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s { ... } fn add_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s { ... } fn equal_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s { ... } fn equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s { ... } fn equal_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s { ... } fn equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s { ... } fn equal_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s { ... } fn equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s { ... } fn equal_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s { ... } fn equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s { ... } fn not_i8s(self, a: Self:: i8s) -> Self:: i8s { ... } fn not_i16s(self, a: Self:: i16s) -> Self:: i16s { ... } fn not_i32s(self, a: Self:: i32s) -> Self:: i32s { ... } fn not_i64s(self, a: Self:: i64s) -> Self:: i64s { ... } fn not_f32s(self, a: Self:: f32s) -> Self:: f32s { ... } fn not_f64s(self, a: Self:: f64s) -> Self:: f64s { ... } fn as_mut_rsimd_u8s(slice: &mut [u8]) -> (&mut [u8], &mut [Self:: u8s]) { ... } fn as_rsimd_u8s(slice: &[u8]) -> (&[u8], &[Self:: u8s]) { ... } fn as_mut_simd_u8s(slice: &mut [u8]) -> (&mut [Self:: u8s], &mut [u8]) { ... } fn as_simd_u8s(slice: &[u8]) -> (&[Self:: u8s], &[u8]) { ... } fn as_uninit_mut_rsimd_u8s( slice: &mut [MaybeUninit< u8>], ) -> (&mut [MaybeUninit< u8>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u8s( slice: &mut [MaybeUninit< u8>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u8>]) { ... } fn as_mut_rsimd_i8s(slice: &mut [i8]) -> (&mut [i8], &mut [Self:: i8s]) { ... } fn as_rsimd_i8s(slice: &[i8]) -> (&[i8], &[Self:: i8s]) { ... } fn as_mut_simd_i8s(slice: &mut [i8]) -> (&mut [Self:: i8s], &mut [i8]) { ... } fn as_simd_i8s(slice: &[i8]) -> (&[Self:: i8s], &[i8]) { ... } fn as_uninit_mut_rsimd_i8s( slice: &mut [MaybeUninit< i8>], ) -> (&mut [MaybeUninit< i8>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i8s( slice: &mut [MaybeUninit< i8>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i8>]) { ... } fn as_mut_rsimd_u16s(slice: &mut [u16]) -> (&mut [u16], &mut [Self:: u16s]) { ... } fn as_rsimd_u16s(slice: &[u16]) -> (&[u16], &[Self:: u16s]) { ... } fn as_mut_simd_u16s(slice: &mut [u16]) -> (&mut [Self:: u16s], &mut [u16]) { ... } fn as_simd_u16s(slice: &[u16]) -> (&[Self:: u16s], &[u16]) { ... } fn as_uninit_mut_rsimd_u16s( slice: &mut [MaybeUninit< u16>], ) -> (&mut [MaybeUninit< u16>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u16s( slice: &mut [MaybeUninit< u16>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u16>]) { ... } fn as_mut_rsimd_i16s(slice: &mut [i16]) -> (&mut [i16], &mut [Self:: i16s]) { ... } fn as_rsimd_i16s(slice: &[i16]) -> (&[i16], &[Self:: i16s]) { ... } fn as_mut_simd_i16s(slice: &mut [i16]) -> (&mut [Self:: i16s], &mut [i16]) { ... } fn as_simd_i16s(slice: &[i16]) -> (&[Self:: i16s], &[i16]) { ... } fn as_uninit_mut_rsimd_i16s( slice: &mut [MaybeUninit< i16>], ) -> (&mut [MaybeUninit< i16>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i16s( slice: &mut [MaybeUninit< i16>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i16>]) { ... } fn as_mut_rsimd_u32s(slice: &mut [u32]) -> (&mut [u32], &mut [Self:: u32s]) { ... } fn as_rsimd_u32s(slice: &[u32]) -> (&[u32], &[Self:: u32s]) { ... } fn as_mut_simd_u32s(slice: &mut [u32]) -> (&mut [Self:: u32s], &mut [u32]) { ... } fn as_simd_u32s(slice: &[u32]) -> (&[Self:: u32s], &[u32]) { ... } fn as_uninit_mut_rsimd_u32s( slice: &mut [MaybeUninit< u32>], ) -> (&mut [MaybeUninit< u32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u32s( slice: &mut [MaybeUninit< u32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u32>]) { ... } fn as_mut_rsimd_i32s(slice: &mut [i32]) -> (&mut [i32], &mut [Self:: i32s]) { ... } fn as_rsimd_i32s(slice: &[i32]) -> (&[i32], &[Self:: i32s]) { ... } fn as_mut_simd_i32s(slice: &mut [i32]) -> (&mut [Self:: i32s], &mut [i32]) { ... } fn as_simd_i32s(slice: &[i32]) -> (&[Self:: i32s], &[i32]) { ... } fn as_uninit_mut_rsimd_i32s( slice: &mut [MaybeUninit< i32>], ) -> (&mut [MaybeUninit< i32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i32s( slice: &mut [MaybeUninit< i32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i32>]) { ... } fn as_mut_rsimd_u64s(slice: &mut [u64]) -> (&mut [u64], &mut [Self:: u64s]) { ... } fn as_rsimd_u64s(slice: &[u64]) -> (&[u64], &[Self:: u64s]) { ... } fn as_mut_simd_u64s(slice: &mut [u64]) -> (&mut [Self:: u64s], &mut [u64]) { ... } fn as_simd_u64s(slice: &[u64]) -> (&[Self:: u64s], &[u64]) { ... } fn as_uninit_mut_rsimd_u64s( slice: &mut [MaybeUninit< u64>], ) -> (&mut [MaybeUninit< u64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_u64s( slice: &mut [MaybeUninit< u64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u64>]) { ... } fn as_mut_rsimd_i64s(slice: &mut [i64]) -> (&mut [i64], &mut [Self:: i64s]) { ... } fn as_rsimd_i64s(slice: &[i64]) -> (&[i64], &[Self:: i64s]) { ... } fn as_mut_simd_i64s(slice: &mut [i64]) -> (&mut [Self:: i64s], &mut [i64]) { ... } fn as_simd_i64s(slice: &[i64]) -> (&[Self:: i64s], &[i64]) { ... } fn as_uninit_mut_rsimd_i64s( slice: &mut [MaybeUninit< i64>], ) -> (&mut [MaybeUninit< i64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_i64s( slice: &mut [MaybeUninit< i64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i64>]) { ... } fn as_mut_rsimd_c32s(slice: &mut [c32]) -> (&mut [c32], &mut [Self:: c32s]) { ... } fn as_rsimd_c32s(slice: &[c32]) -> (&[c32], &[Self:: c32s]) { ... } fn as_mut_simd_c32s(slice: &mut [c32]) -> (&mut [Self:: c32s], &mut [c32]) { ... } fn as_simd_c32s(slice: &[c32]) -> (&[Self:: c32s], &[c32]) { ... } fn as_uninit_mut_rsimd_c32s( slice: &mut [MaybeUninit< c32>], ) -> (&mut [MaybeUninit< c32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_c32s( slice: &mut [MaybeUninit< c32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< c32>]) { ... } fn as_mut_rsimd_f32s(slice: &mut [f32]) -> (&mut [f32], &mut [Self:: f32s]) { ... } fn as_rsimd_f32s(slice: &[f32]) -> (&[f32], &[Self:: f32s]) { ... } fn as_mut_simd_f32s(slice: &mut [f32]) -> (&mut [Self:: f32s], &mut [f32]) { ... } fn as_simd_f32s(slice: &[f32]) -> (&[Self:: f32s], &[f32]) { ... } fn as_uninit_mut_rsimd_f32s( slice: &mut [MaybeUninit< f32>], ) -> (&mut [MaybeUninit< f32>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_f32s( slice: &mut [MaybeUninit< f32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< f32>]) { ... } fn as_mut_rsimd_c64s(slice: &mut [c64]) -> (&mut [c64], &mut [Self:: c64s]) { ... } fn as_rsimd_c64s(slice: &[c64]) -> (&[c64], &[Self:: c64s]) { ... } fn as_mut_simd_c64s(slice: &mut [c64]) -> (&mut [Self:: c64s], &mut [c64]) { ... } fn as_simd_c64s(slice: &[c64]) -> (&[Self:: c64s], &[c64]) { ... } fn as_uninit_mut_rsimd_c64s( slice: &mut [MaybeUninit< c64>], ) -> (&mut [MaybeUninit< c64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_c64s( slice: &mut [MaybeUninit< c64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< c64>]) { ... } fn as_mut_rsimd_f64s(slice: &mut [f64]) -> (&mut [f64], &mut [Self:: f64s]) { ... } fn as_rsimd_f64s(slice: &[f64]) -> (&[f64], &[Self:: f64s]) { ... } fn as_mut_simd_f64s(slice: &mut [f64]) -> (&mut [Self:: f64s], &mut [f64]) { ... } fn as_simd_f64s(slice: &[f64]) -> (&[Self:: f64s], &[f64]) { ... } fn as_uninit_mut_rsimd_f64s( slice: &mut [MaybeUninit< f64>], ) -> (&mut [MaybeUninit< f64>], &mut [MaybeUninit]) { ... } fn as_uninit_mut_simd_f64s( slice: &mut [MaybeUninit< f64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< f64>]) { ... } fn conj_mul_add_e_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s { ... } fn conj_mul_add_e_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s { ... } fn conj_mul_e_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s { ... } fn conj_mul_e_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s { ... } fn deinterleave_shfl_f32s (self, values: T) -> T { ... } fn deinterleave_shfl_f64s (self, values: T) -> T { ... } fn first_true_m8s(self, mask: Self:: m8s) -> usize { ... } fn first_true_m16s(self, mask: Self:: m16s) -> usize { ... } fn first_true_m32s(self, mask: Self:: m32s) -> usize { ... } fn first_true_m64s(self, mask: Self:: m64s) -> usize { ... } fn interleave_shfl_f32s (self, values: T) -> T { ... } fn interleave_shfl_f64s (self, values: T) -> T { ... } fn mask_between_m8s(self, start: u8, end: u8) -> MemMask { ... } fn mask_between_m16s(self, start: u16, end: u16) -> MemMask { ... } fn mask_between_m32s(self, start: u32, end: u32) -> MemMask { ... } fn mask_between_m64s(self, start: u64, end: u64) -> MemMask { ... } unsafe fn mask_load_ptr_f32s( self, mask: MemMask, ptr: *const f32, ) -> Self:: f32s { ... } unsafe fn mask_load_ptr_f64s( self, mask: MemMask, ptr: *const f64, ) -> Self:: f64s { ... } unsafe fn mask_load_ptr_i8s( self, mask: MemMask, ptr: *const i8, ) -> Self:: i8s { ... } unsafe fn mask_load_ptr_i16s( self, mask: MemMask, ptr: *const i16, ) -> Self:: i16s { ... } unsafe fn mask_load_ptr_i32s( self, mask: MemMask, ptr: *const i32, ) -> Self:: i32s { ... } unsafe fn mask_load_ptr_i64s( self, mask: MemMask, ptr: *const i64, ) -> Self:: i64s { ... } unsafe fn mask_store_ptr_f32s( self, mask: MemMask, ptr: *mut f32, values: Self:: f32s, ) { ... } unsafe fn mask_store_ptr_f64s( self, mask: MemMask, ptr: *mut f64, values: Self:: f64s, ) { ... } unsafe fn mask_store_ptr_i8s( self, mask: MemMask, ptr: *mut i8, values: Self:: i8s, ) { ... } unsafe fn mask_store_ptr_i16s( self, mask: MemMask, ptr: *mut i16, values: Self:: i16s, ) { ... } unsafe fn mask_store_ptr_i32s( self, mask: MemMask, ptr: *mut i32, values: Self:: i32s, ) { ... } unsafe fn mask_store_ptr_i64s( self, mask: MemMask, ptr: *mut i64, values: Self:: i64s, ) { ... } fn mul_add_e_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s { ... } fn mul_add_e_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s { ... } fn negate_mul_add_e_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s { ... } fn negate_mul_add_e_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s { ... } fn negate_mul_add_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s { ... } fn negate_mul_add_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s { ... } fn mul_e_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s { ... } fn mul_e_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s { ... } fn neg_f32s(self, a: Self:: f32s) -> Self:: f32s { ... } fn neg_f64s(self, a: Self:: f64s) -> Self:: f64s { ... } fn partial_load_c32s(self, slice: &[c32]) -> Self:: c32s { ... } fn partial_load_c64s(self, slice: &[c64]) -> Self:: c64s { ... } fn partial_load_f32s(self, slice: &[f32]) -> Self:: f32s { ... } fn partial_load_f64s(self, slice: &[f64]) -> Self:: f64s { ... } fn partial_load_i8s(self, slice: &[i8]) -> Self:: i8s { ... } fn partial_load_i16s(self, slice: &[i16]) -> Self:: i16s { ... } fn partial_load_i32s(self, slice: &[i32]) -> Self:: i32s { ... } fn partial_load_i64s(self, slice: &[i64]) -> Self:: i64s { ... } fn partial_load_u8s(self, slice: &[u8]) -> Self:: u8s { ... } fn partial_load_u16s(self, slice: &[u16]) -> Self:: u16s { ... } fn partial_load_u32s(self, slice: &[u32]) -> Self:: u32s { ... } fn partial_load_u64s(self, slice: &[u64]) -> Self:: u64s { ... } fn partial_store_c32s(self, slice: &mut [c32], values: Self:: c32s) { ... } fn partial_store_c64s(self, slice: &mut [c64], values: Self:: c64s) { ... } fn partial_store_f32s(self, slice: &mut [f32], values: Self:: f32s) { ... } fn partial_store_f64s(self, slice: &mut [f64], values: Self:: f64s) { ... } fn partial_store_i8s(self, slice: &mut [i8], values: Self:: i8s) { ... } fn partial_store_i16s(self, slice: &mut [i16], values: Self:: i16s) { ... } fn partial_store_i32s(self, slice: &mut [i32], values: Self:: i32s) { ... } fn partial_store_i64s(self, slice: &mut [i64], values: Self:: i64s) { ... } fn partial_store_u8s(self, slice: &mut [u8], values: Self:: u8s) { ... } fn partial_store_u16s(self, slice: &mut [u16], values: Self:: u16s) { ... } fn partial_store_u32s(self, slice: &mut [u32], values: Self:: u32s) { ... } fn partial_store_u64s(self, slice: &mut [u64], values: Self:: u64s) { ... } fn rotate_left_c32s(self, a: Self:: c32s, amount: usize) -> Self:: c32s { ... } fn rotate_left_c64s(self, a: Self:: c64s, amount: usize) -> Self:: c64s { ... } fn rotate_left_f32s(self, a: Self:: f32s, amount: usize) -> Self:: f32s { ... } fn rotate_left_f64s(self, a: Self:: f64s, amount: usize) -> Self:: f64s { ... } fn rotate_left_i32s(self, a: Self:: i32s, amount: usize) -> Self:: i32s { ... } fn rotate_left_i64s(self, a: Self:: i64s, amount: usize) -> Self:: i64s { ... } fn rotate_left_u32s(self, a: Self:: u32s, amount: usize) -> Self:: u32s { ... } fn rotate_left_u64s(self, a: Self:: u64s, amount: usize) -> Self:: u64s { ... } fn rotate_right_f32s(self, a: Self:: f32s, amount: usize) -> Self:: f32s { ... } fn rotate_right_f64s(self, a: Self:: f64s, amount: usize) -> Self:: f64s { ... } fn rotate_right_i32s(self, a: Self:: i32s, amount: usize) -> Self:: i32s { ... } fn rotate_right_i64s(self, a: Self:: i64s, amount: usize) -> Self:: i64s { ... } fn select_f32s( self, mask: Self:: m32s, if_true: Self:: f32s, if_false: Self:: f32s, ) -> Self:: f32s { ... } fn select_f64s( self, mask: Self:: m64s, if_true: Self:: f64s, if_false: Self:: f64s, ) -> Self:: f64s { ... } fn select_i32s( self, mask: Self:: m32s, if_true: Self:: i32s, if_false: Self:: i32s, ) -> Self:: i32s { ... } fn select_i64s( self, mask: Self:: m64s, if_true: Self:: i64s, if_false: Self:: i64s, ) -> Self:: i64s { ... } fn transmute_f32s_i32s(self, a: Self:: i32s) -> Self:: f32s { ... } fn transmute_f32s_u32s(self, a: Self:: u32s) -> Self:: f32s { ... } fn transmute_f64s_i64s(self, a: Self:: i64s) -> Self:: f64s { ... } fn transmute_f64s_u64s(self, a: Self:: u64s) -> Self:: f64s { ... } fn transmute_i32s_f32s(self, a: Self:: f32s) -> Self:: i32s { ... } fn transmute_m8s_u8s(self, a: Self:: u8s) -> Self:: m8s { ... } fn transmute_u8s_m8s(self, a: Self:: m8s) -> Self:: u8s { ... } fn transmute_m16s_u16s(self, a: Self:: u16s) -> Self:: m16s { ... } fn transmute_u16s_m16s(self, a: Self:: m16s) -> Self:: u16s { ... } fn transmute_m32s_u32s(self, a: Self:: u32s) -> Self:: m32s { ... } fn transmute_u32s_m32s(self, a: Self:: m32s) -> Self:: u32s { ... } fn transmute_m64s_u64s(self, a: Self:: u64s) -> Self:: m64s { ... } fn transmute_u64s_m64s(self, a: Self:: m64s) -> Self:: u64s { ... } fn transmute_i8s_u8s(self, a: Self:: u8s) -> Self:: i8s { ... } fn transmute_u8s_i8s(self, a: Self:: i8s) -> Self:: u8s { ... } fn transmute_u16s_i16s(self, a: Self:: i16s) -> Self:: u16s { ... } fn transmute_i16s_u16s(self, a: Self:: u16s) -> Self:: i16s { ... } fn transmute_i32s_u32s(self, a: Self:: u32s) -> Self:: i32s { ... } fn transmute_i64s_f64s(self, a: Self:: f64s) -> Self:: i64s { ... } fn transmute_i64s_u64s(self, a: Self:: u64s) -> Self:: i64s { ... } fn transmute_u32s_f32s(self, a: Self:: f32s) -> Self:: u32s { ... } fn transmute_u32s_i32s(self, a: Self:: i32s) -> Self:: u32s { ... } fn transmute_u64s_f64s(self, a: Self:: f64s) -> Self:: u64s { ... } fn transmute_u64s_i64s(self, a: Self:: i64s) -> Self:: u64s { ... } 

}

## Required Associated Constants§

## Provided Associated Constants§

#### const IS_SCALAR: bool = false

#### const M64_LANES: usize = _

#### const U64_LANES: usize = _

#### const I64_LANES: usize = _

#### const F64_LANES: usize = _

#### const C64_LANES: usize = _

#### const M32_LANES: usize = _

#### const U32_LANES: usize = _

#### const I32_LANES: usize = _

#### const F32_LANES: usize = _

#### const C32_LANES: usize = _

#### const M16_LANES: usize = _

#### const U16_LANES: usize = _

#### const I16_LANES: usize = _

#### const M8_LANES: usize = _

#### const U8_LANES: usize = _

## Required Associated Types§

#### type m8s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static

#### type i8s: Debug + Copy + Send + Sync + Pod + 'static

#### type u8s: Debug + Copy + Send + Sync + Pod + 'static

#### type m16s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static

#### type i16s: Debug + Copy + Send + Sync + Pod + 'static

#### type u16s: Debug + Copy + Send + Sync + Pod + 'static

#### type m32s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static

#### type f32s: Debug + Copy + Send + Sync + Pod + 'static

#### type c32s: Debug + Copy + Send + Sync + Pod + 'static

#### type i32s: Debug + Copy + Send + Sync + Pod + 'static

#### type u32s: Debug + Copy + Send + Sync + Pod + 'static

#### type m64s: Debug + Copy + Send + Sync + Zeroable + NoUninit + CheckedBitPattern + 'static

#### type f64s: Debug + Copy + Send + Sync + Pod + 'static

#### type c64s: Debug + Copy + Send + Sync + Pod + 'static

#### type i64s: Debug + Copy + Send + Sync + Pod + 'static

#### type u64s: Debug + Copy + Send + Sync + Pod + 'static

## Required Methods§

Source fn abs2_c32s(self, a: Self:: c32s) -> Self:: c32s

Contains the square of the norm in both the real and imaginary components.

Source fn abs2_c64s(self, a: Self:: c64s) -> Self:: c64s

Contains the square of the norm in both the real and imaginary components.

Source fn abs_max_c32s(self, a: Self:: c32s) -> Self:: c32s

Contains the max norm in both the real and imaginary components.

Source fn abs_max_c64s(self, a: Self:: c64s) -> Self:: c64s

Contains the max norm in both the real and imaginary components.

#### fn add_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s

#### fn add_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s

#### fn add_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn add_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn add_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn add_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn add_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn add_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn sub_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s

#### fn sub_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s

#### fn sub_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn sub_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn sub_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn sub_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn sub_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn sub_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn sub_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn sub_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn sub_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn sub_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn mul_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s

#### fn mul_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s

#### fn mul_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn mul_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn mul_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn mul_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn mul_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn mul_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn mul_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn mul_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn div_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn div_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s

#### fn equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s

#### fn equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s

#### fn equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s

#### fn equal_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: m32s

#### fn equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s

#### fn equal_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: m64s

#### fn equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s

#### fn greater_than_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s

#### fn greater_than_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s

#### fn greater_than_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s

#### fn greater_than_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s

#### fn greater_than_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s

#### fn greater_than_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s

#### fn greater_than_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s

#### fn greater_than_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s

#### fn greater_than_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s

#### fn greater_than_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s

#### fn greater_than_or_equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s

Source

#### fn greater_than_or_equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s

Source

#### fn greater_than_or_equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s

Source

#### fn greater_than_or_equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s

Source

#### fn greater_than_or_equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s

Source

#### fn greater_than_or_equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s

Source

#### fn greater_than_or_equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s

Source

#### fn greater_than_or_equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s

Source

#### fn greater_than_or_equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s

Source

#### fn greater_than_or_equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s

#### fn less_than_or_equal_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s

#### fn less_than_or_equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s

#### fn less_than_or_equal_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s

#### fn less_than_or_equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s

#### fn less_than_or_equal_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s

#### fn less_than_or_equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s

#### fn less_than_or_equal_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s

#### fn less_than_or_equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s

#### fn less_than_or_equal_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s

#### fn less_than_or_equal_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s

#### fn less_than_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: m8s

#### fn less_than_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s

#### fn less_than_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: m16s

#### fn less_than_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s

#### fn less_than_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: m32s

#### fn less_than_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s

#### fn less_than_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: m64s

#### fn less_than_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s

#### fn less_than_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: m32s

#### fn less_than_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: m64s

#### fn and_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn and_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn and_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn and_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn or_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn or_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

Source

#### fn or_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn or_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn xor_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn xor_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn xor_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn xor_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn min_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn min_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn min_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn min_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn min_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn min_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn min_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn min_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn min_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn min_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn max_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn max_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn max_u8s(self, a: Self:: u8s, b: Self:: u8s) -> Self:: u8s

#### fn max_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn max_u16s(self, a: Self:: u16s, b: Self:: u16s) -> Self:: u16s

#### fn max_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn max_u32s(self, a: Self:: u32s, b: Self:: u32s) -> Self:: u32s

#### fn max_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn max_u64s(self, a: Self:: u64s, b: Self:: u64s) -> Self:: u64s

#### fn max_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn neg_c32s(self, a: Self:: c32s) -> Self:: c32s

#### fn neg_c64s(self, a: Self:: c64s) -> Self:: c64s

#### fn not_m8s(self, a: Self:: m8s) -> Self:: m8s

#### fn not_u8s(self, a: Self:: u8s) -> Self:: u8s

#### fn not_m16s(self, a: Self:: m16s) -> Self:: m16s

#### fn not_u16s(self, a: Self:: u16s) -> Self:: u16s

#### fn not_m32s(self, a: Self:: m32s) -> Self:: m32s

#### fn not_u32s(self, a: Self:: u32s) -> Self:: u32s

#### fn not_m64s(self, a: Self:: m64s) -> Self:: m64s

#### fn not_u64s(self, a: Self:: u64s) -> Self:: u64s

#### fn splat_u8s(self, value: u8) -> Self:: u8s

#### fn splat_i8s(self, value: i8) -> Self:: i8s

#### fn splat_u16s(self, value: u16) -> Self:: u16s

#### fn splat_i16s(self, value: i16) -> Self:: i16s

#### fn splat_u32s(self, value: u32) -> Self:: u32s

#### fn splat_i32s(self, value: i32) -> Self:: i32s

#### fn splat_u64s(self, value: u64) -> Self:: u64s

#### fn splat_i64s(self, value: i64) -> Self:: i64s

#### fn splat_c32s(self, value: c32) -> Self:: c32s

#### fn splat_f32s(self, value: f32) -> Self:: f32s

#### fn splat_c64s(self, value: c64) -> Self:: c64s

#### fn splat_f64s(self, value: f64) -> Self:: f64s

#### fn sqrt_f32s(self, a: Self:: f32s) -> Self:: f32s

#### fn sqrt_f64s(self, a: Self:: f64s) -> Self:: f64s

#### fn conj_c32s(self, a: Self:: c32s) -> Self:: c32s

#### fn conj_c64s(self, a: Self:: c64s) -> Self:: c64s

#### fn conj_mul_add_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s

#### fn conj_mul_add_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s

#### fn conj_mul_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s

#### fn conj_mul_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s

Source unsafe fn mask_load_ptr_c32s( self, mask: MemMask, ptr: *const c32, ) -> Self:: c32s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_c64s( self, mask: MemMask, ptr: *const c64, ) -> Self:: c64s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_u8s( self, mask: MemMask, ptr: *const u8, ) -> Self:: u8s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_u16s( self, mask: MemMask, ptr: *const u16, ) -> Self:: u16s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_u32s( self, mask: MemMask, ptr: *const u32, ) -> Self:: u32s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_u64s( self, mask: MemMask, ptr: *const u64, ) -> Self:: u64s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_store_ptr_c32s( self, mask: MemMask, ptr: *mut c32, values: Self:: c32s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_c64s( self, mask: MemMask, ptr: *mut c64, values: Self:: c64s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_u8s( self, mask: MemMask, ptr: *mut u8, values: Self:: u8s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_u16s( self, mask: MemMask, ptr: *mut u16, values: Self:: u16s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_u32s( self, mask: MemMask, ptr: *mut u32, values: Self:: u32s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_u64s( self, mask: MemMask, ptr: *mut u64, values: Self:: u64s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

#### fn mul_add_c32s(self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s) -> Self:: c32s

#### fn mul_add_c64s(self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s) -> Self:: c64s

#### fn mul_add_e_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s

#### fn mul_add_e_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s

#### fn mul_add_f32s(self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s) -> Self:: f32s

#### fn mul_add_f64s(self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s) -> Self:: f64s

#### fn reduce_max_c32s(self, a: Self:: c32s) -> c32

#### fn reduce_max_c64s(self, a: Self:: c64s) -> c64

#### fn reduce_max_f32s(self, a: Self:: f32s) -> f32

#### fn reduce_max_f64s(self, a: Self:: f64s) -> f64

#### fn reduce_min_c32s(self, a: Self:: c32s) -> c32

#### fn reduce_min_c64s(self, a: Self:: c64s) -> c64

#### fn reduce_min_f32s(self, a: Self:: f32s) -> f32

#### fn reduce_min_f64s(self, a: Self:: f64s) -> f64

#### fn reduce_product_f32s(self, a: Self:: f32s) -> f32

#### fn reduce_product_f64s(self, a: Self:: f64s) -> f64

#### fn reduce_sum_c32s(self, a: Self:: c32s) -> c32

#### fn reduce_sum_c64s(self, a: Self:: c64s) -> c64

#### fn reduce_sum_f32s(self, a: Self:: f32s) -> f32

#### fn reduce_sum_f64s(self, a: Self:: f64s) -> f64

#### fn rotate_right_c32s(self, a: Self:: c32s, amount: usize) -> Self:: c32s

#### fn rotate_right_c64s(self, a: Self:: c64s, amount: usize) -> Self:: c64s

#### fn rotate_right_u32s(self, a: Self:: u32s, amount: usize) -> Self:: u32s

#### fn rotate_right_u64s(self, a: Self:: u64s, amount: usize) -> Self:: u64s

#### fn select_u32s( self, mask: Self:: m32s, if_true: Self:: u32s, if_false: Self:: u32s, ) -> Self:: u32s

#### fn select_u64s( self, mask: Self:: m64s, if_true: Self:: u64s, if_false: Self:: u64s, ) -> Self:: u64s

#### fn swap_re_im_c32s(self, a: Self:: c32s) -> Self:: c32s

#### fn swap_re_im_c64s(self, a: Self:: c64s) -> Self:: c64s

#### fn vectorize (self, op: Op) -> Op:: Output

#### fn widening_mul_u32s( self, a: Self:: u32s, b: Self:: u32s, ) -> (Self:: u32s, Self:: u32s)

#### fn wrapping_dyn_shl_u32s(self, a: Self:: u32s, amount: Self:: u32s) -> Self:: u32s

#### fn wrapping_dyn_shr_u32s(self, a: Self:: u32s, amount: Self:: u32s) -> Self:: u32s

## Provided Methods§

#### fn abs_f32s(self, a: Self:: f32s) -> Self:: f32s

#### fn abs_f64s(self, a: Self:: f64s) -> Self:: f64s

#### fn and_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s

#### fn and_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn and_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s

#### fn and_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn and_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s

#### fn and_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn and_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s

#### fn and_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn and_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn and_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn or_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s

#### fn or_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn or_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s

#### fn or_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn or_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s

#### fn or_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn or_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s

#### fn or_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn or_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn or_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn xor_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s

#### fn xor_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn xor_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s

#### fn xor_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn xor_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s

#### fn xor_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn xor_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s

Source

#### fn xor_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn xor_f32s(self, a: Self:: f32s, b: Self:: f32s) -> Self:: f32s

#### fn xor_f64s(self, a: Self:: f64s, b: Self:: f64s) -> Self:: f64s

#### fn add_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: i8s

#### fn add_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: i16s

#### fn add_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: i32s

#### fn add_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: i64s

#### fn equal_m8s(self, a: Self:: m8s, b: Self:: m8s) -> Self:: m8s

#### fn equal_i8s(self, a: Self:: i8s, b: Self:: i8s) -> Self:: m8s

#### fn equal_m16s(self, a: Self:: m16s, b: Self:: m16s) -> Self:: m16s

#### fn equal_i16s(self, a: Self:: i16s, b: Self:: i16s) -> Self:: m16s

#### fn equal_m32s(self, a: Self:: m32s, b: Self:: m32s) -> Self:: m32s

#### fn equal_i32s(self, a: Self:: i32s, b: Self:: i32s) -> Self:: m32s

#### fn equal_m64s(self, a: Self:: m64s, b: Self:: m64s) -> Self:: m64s

#### fn equal_i64s(self, a: Self:: i64s, b: Self:: i64s) -> Self:: m64s

#### fn not_i8s(self, a: Self:: i8s) -> Self:: i8s

#### fn not_i16s(self, a: Self:: i16s) -> Self:: i16s

#### fn not_i32s(self, a: Self:: i32s) -> Self:: i32s

#### fn not_i64s(self, a: Self:: i64s) -> Self:: i64s

#### fn not_f32s(self, a: Self:: f32s) -> Self:: f32s

#### fn not_f64s(self, a: Self:: f64s) -> Self:: f64s

#### fn as_mut_rsimd_u8s(slice: &mut [u8]) -> (&mut [u8], &mut [Self:: u8s])

#### fn as_rsimd_u8s(slice: &[u8]) -> (&[u8], &[Self:: u8s])

#### fn as_mut_simd_u8s(slice: &mut [u8]) -> (&mut [Self:: u8s], &mut [u8])

#### fn as_simd_u8s(slice: &[u8]) -> (&[Self:: u8s], &[u8])

#### fn as_uninit_mut_rsimd_u8s( slice: &mut [MaybeUninit< u8>], ) -> (&mut [MaybeUninit< u8>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_u8s( slice: &mut [MaybeUninit< u8>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u8>])

#### fn as_mut_rsimd_i8s(slice: &mut [i8]) -> (&mut [i8], &mut [Self:: i8s])

#### fn as_rsimd_i8s(slice: &[i8]) -> (&[i8], &[Self:: i8s])

#### fn as_mut_simd_i8s(slice: &mut [i8]) -> (&mut [Self:: i8s], &mut [i8])

#### fn as_simd_i8s(slice: &[i8]) -> (&[Self:: i8s], &[i8])

#### fn as_uninit_mut_rsimd_i8s( slice: &mut [MaybeUninit< i8>], ) -> (&mut [MaybeUninit< i8>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_i8s( slice: &mut [MaybeUninit< i8>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i8>])

#### fn as_mut_rsimd_u16s(slice: &mut [u16]) -> (&mut [u16], &mut [Self:: u16s])

#### fn as_rsimd_u16s(slice: &[u16]) -> (&[u16], &[Self:: u16s])

#### fn as_mut_simd_u16s(slice: &mut [u16]) -> (&mut [Self:: u16s], &mut [u16])

#### fn as_simd_u16s(slice: &[u16]) -> (&[Self:: u16s], &[u16])

#### fn as_uninit_mut_rsimd_u16s( slice: &mut [MaybeUninit< u16>], ) -> (&mut [MaybeUninit< u16>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_u16s( slice: &mut [MaybeUninit< u16>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u16>])

#### fn as_mut_rsimd_i16s(slice: &mut [i16]) -> (&mut [i16], &mut [Self:: i16s])

#### fn as_rsimd_i16s(slice: &[i16]) -> (&[i16], &[Self:: i16s])

#### fn as_mut_simd_i16s(slice: &mut [i16]) -> (&mut [Self:: i16s], &mut [i16])

#### fn as_simd_i16s(slice: &[i16]) -> (&[Self:: i16s], &[i16])

#### fn as_uninit_mut_rsimd_i16s( slice: &mut [MaybeUninit< i16>], ) -> (&mut [MaybeUninit< i16>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_i16s( slice: &mut [MaybeUninit< i16>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i16>])

#### fn as_mut_rsimd_u32s(slice: &mut [u32]) -> (&mut [u32], &mut [Self:: u32s])

#### fn as_rsimd_u32s(slice: &[u32]) -> (&[u32], &[Self:: u32s])

#### fn as_mut_simd_u32s(slice: &mut [u32]) -> (&mut [Self:: u32s], &mut [u32])

#### fn as_simd_u32s(slice: &[u32]) -> (&[Self:: u32s], &[u32])

#### fn as_uninit_mut_rsimd_u32s( slice: &mut [MaybeUninit< u32>], ) -> (&mut [MaybeUninit< u32>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_u32s( slice: &mut [MaybeUninit< u32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u32>])

#### fn as_mut_rsimd_i32s(slice: &mut [i32]) -> (&mut [i32], &mut [Self:: i32s])

#### fn as_rsimd_i32s(slice: &[i32]) -> (&[i32], &[Self:: i32s])

#### fn as_mut_simd_i32s(slice: &mut [i32]) -> (&mut [Self:: i32s], &mut [i32])

#### fn as_simd_i32s(slice: &[i32]) -> (&[Self:: i32s], &[i32])

#### fn as_uninit_mut_rsimd_i32s( slice: &mut [MaybeUninit< i32>], ) -> (&mut [MaybeUninit< i32>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_i32s( slice: &mut [MaybeUninit< i32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i32>])

Source

#### fn as_mut_rsimd_u64s(slice: &mut [u64]) -> (&mut [u64], &mut [Self:: u64s])

#### fn as_rsimd_u64s(slice: &[u64]) -> (&[u64], &[Self:: u64s])

#### fn as_mut_simd_u64s(slice: &mut [u64]) -> (&mut [Self:: u64s], &mut [u64])

#### fn as_simd_u64s(slice: &[u64]) -> (&[Self:: u64s], &[u64])

#### fn as_uninit_mut_rsimd_u64s( slice: &mut [MaybeUninit< u64>], ) -> (&mut [MaybeUninit< u64>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_u64s( slice: &mut [MaybeUninit< u64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< u64>])

#### fn as_mut_rsimd_i64s(slice: &mut [i64]) -> (&mut [i64], &mut [Self:: i64s])

#### fn as_rsimd_i64s(slice: &[i64]) -> (&[i64], &[Self:: i64s])

#### fn as_mut_simd_i64s(slice: &mut [i64]) -> (&mut [Self:: i64s], &mut [i64])

#### fn as_simd_i64s(slice: &[i64]) -> (&[Self:: i64s], &[i64])

#### fn as_uninit_mut_rsimd_i64s( slice: &mut [MaybeUninit< i64>], ) -> (&mut [MaybeUninit< i64>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_i64s( slice: &mut [MaybeUninit< i64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< i64>])

#### fn as_mut_rsimd_c32s(slice: &mut [c32]) -> (&mut [c32], &mut [Self:: c32s])

#### fn as_rsimd_c32s(slice: &[c32]) -> (&[c32], &[Self:: c32s])

#### fn as_mut_simd_c32s(slice: &mut [c32]) -> (&mut [Self:: c32s], &mut [c32])

#### fn as_simd_c32s(slice: &[c32]) -> (&[Self:: c32s], &[c32])

#### fn as_uninit_mut_rsimd_c32s( slice: &mut [MaybeUninit< c32>], ) -> (&mut [MaybeUninit< c32>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_c32s( slice: &mut [MaybeUninit< c32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< c32>])

#### fn as_mut_rsimd_f32s(slice: &mut [f32]) -> (&mut [f32], &mut [Self:: f32s])

#### fn as_rsimd_f32s(slice: &[f32]) -> (&[f32], &[Self:: f32s])

#### fn as_mut_simd_f32s(slice: &mut [f32]) -> (&mut [Self:: f32s], &mut [f32])

Source fn as_simd_f32s(slice: &[f32]) -> (&[Self:: f32s], &[f32])

##### Examples found in repository?

examples/dot_product.rs (line 402)

```
397		fn call(self) -> Self::Output {
398			let Self { simd, x, y } = self;
399
400			// x0 x1 x2.. x100
401			// [[x0 x1 x2 x3 x4 x5 x6 x7] [x8 x9 x10.. x15] [..x95]] | [x96 x97 x98 x99 x100]
402			let (xs, x1) = S::as_simd_f32s(x);
403			let (ys, y1) = S::as_simd_f32s(y);
404
405			// sum (x * y)
406			// sum (reduce_sum(X * Y))
407			// reduce_sum(sum (X * Y))
408
409			let mut acc0 = simd.splat_f32s(0.0);
410			let mut acc1 = simd.splat_f32s(0.0);
411			let mut acc2 = simd.splat_f32s(0.0);
412			let mut acc3 = simd.splat_f32s(0.0);
413
414			// 12 registers are being used
415			// 4 for accumulators + 2×4 inside the loop for x[0|1] and y[0|1]
416			let (xs_4, xs_1) = pulp::as_arrays::<4, _>(xs);
417			let (ys_4, ys_1) = pulp::as_arrays::<4, _>(ys);
418
419			for ([x0, x1, x2, x3], [y0, y1, y2, y3]) in iter::zip(xs_4, ys_4) {
420				acc0 = simd.mul_add_f32s(*x0, *y0, acc0);
421				acc1 = simd.mul_add_f32s(*x1, *y1, acc1);
422				acc2 = simd.mul_add_f32s(*x2, *y2, acc2);
423				acc3 = simd.mul_add_f32s(*x3, *y3, acc3);
424			}
425
426			for (x0, y0) in iter::zip(xs_1, ys_1) {
427				acc0 = simd.mul_add_f32s(*x0, *y0, acc0);
428			}
429
430			// reduce_sum_f32s
431			// f32x8 -> f32x4 + f32x4
432			// f32x4 -> f32x2 + f32x2
433			// f32x2 -> f32 + f32
434			acc0 = simd.add_f32s(acc0, acc1);
435			acc2 = simd.add_f32s(acc2, acc3);
436
437			acc0 = simd.add_f32s(acc0, acc2);
438
439			let mut acc = simd.reduce_sum_f32s(acc0);
440
441			for (x, y) in iter::zip(x1, y1) {
442				acc += x * y;
443			}
444
445			acc
446		}
447	}
448
449	simd.vectorize(Impl { simd, x, y })
450}
451
452// fma: fused multiply add
453pub fn dot_product_simd_extract_reduce_ilp_fma_epilogue_generic<S: Simd>(
454	simd: S,
455	x: &[f32],
456	y: &[f32],
457) -> f32 {
458	struct Impl<'a, S> {
459		simd: S,
460		x: &'a [f32],
461		y: &'a [f32],
462	}
463
464	impl<S: Simd> pulp::NullaryFnOnce for Impl<'_, S> {
465		type Output = f32;
466
467		#[inline(always)]
468		fn call(self) -> Self::Output {
469			let Self { simd, x, y } = self;
470
471			// x0 x1 x2.. x100
472			// [[x0 x1 x2 x3 x4 x5 x6 x7] [x8 x9 x10.. x15] [..x95]] | [x96 x97 x98 x99 x100]
473			let (xs, x1) = S::as_simd_f32s(x);
474			let (ys, y1) = S::as_simd_f32s(y);
475
476			// sum (x * y)
477			// sum (reduce_sum(X * Y))
478			// reduce_sum(sum (X * Y))
479
480			let mut acc0 = simd.splat_f32s(0.0);
481			let mut acc1 = simd.splat_f32s(0.0);
482			let mut acc2 = simd.splat_f32s(0.0);
483			let mut acc3 = simd.splat_f32s(0.0);
484
485			// 12 registers are being used
486			// 4 for accumulators + 2×4 inside the loop for x[0|1] and y[0|1]
487			let (xs_4, xs_1) = pulp::as_arrays::<4, _>(xs);
488			let (ys_4, ys_1) = pulp::as_arrays::<4, _>(ys);
489
490			for ([x0, x1, x2, x3], [y0, y1, y2, y3]) in iter::zip(xs_4, ys_4) {
491				acc0 = simd.mul_add_f32s(*x0, *y0, acc0);
492				acc1 = simd.mul_add_f32s(*x1, *y1, acc1);
493				acc2 = simd.mul_add_f32s(*x2, *y2, acc2);
494				acc3 = simd.mul_add_f32s(*x3, *y3, acc3);
495			}
496
497			for (x0, y0) in iter::zip(xs_1, ys_1) {
498				acc0 = simd.mul_add_f32s(*x0, *y0, acc0);
499			}
500
501			// reduce_sum_f32s
502			// f32x8 -> f32x4 + f32x4
503			// f32x4 -> f32x2 + f32x2
504			// f32x2 -> f32 + f32
505			acc0 = simd.add_f32s(acc0, acc1);
506			acc2 = simd.add_f32s(acc2, acc3);
507
508			acc0 = simd.add_f32s(acc0, acc2);
509
510			if !x1.is_empty() {
511				acc0 =
512					simd.mul_add_f32s(simd.partial_load_f32s(x1), simd.partial_load_f32s(y1), acc0);
513			}
514
515			simd.reduce_sum_f32s(acc0)
516		}
```

#### fn as_uninit_mut_rsimd_f32s( slice: &mut [MaybeUninit< f32>], ) -> (&mut [MaybeUninit< f32>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_f32s( slice: &mut [MaybeUninit< f32>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< f32>])

#### fn as_mut_rsimd_c64s(slice: &mut [c64]) -> (&mut [c64], &mut [Self:: c64s])

#### fn as_rsimd_c64s(slice: &[c64]) -> (&[c64], &[Self:: c64s])

#### fn as_mut_simd_c64s(slice: &mut [c64]) -> (&mut [Self:: c64s], &mut [c64])

#### fn as_simd_c64s(slice: &[c64]) -> (&[Self:: c64s], &[c64])

#### fn as_uninit_mut_rsimd_c64s( slice: &mut [MaybeUninit< c64>], ) -> (&mut [MaybeUninit< c64>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_c64s( slice: &mut [MaybeUninit< c64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< c64>])

#### fn as_mut_rsimd_f64s(slice: &mut [f64]) -> (&mut [f64], &mut [Self:: f64s])

#### fn as_rsimd_f64s(slice: &[f64]) -> (&[f64], &[Self:: f64s])

#### fn as_mut_simd_f64s(slice: &mut [f64]) -> (&mut [Self:: f64s], &mut [f64])

Source fn as_simd_f64s(slice: &[f64]) -> (&[Self:: f64s], &[f64])

##### Examples found in repository?

examples/basic.rs (line 147)

```
144				fn with_simd<S: Simd>(self, simd: S) -> Self::Output {
145					let Self { v } = self;
146
147					let (head, tail) = S::as_simd_f64s(v);
148
149					let mut acc0 = simd.splat_f64s(0.0);
150					let mut acc1 = simd.splat_f64s(0.0);
151					let mut acc2 = simd.splat_f64s(0.0);
152					let mut acc3 = simd.splat_f64s(0.0);
153
154					let (head4, head1) = pulp::as_arrays::<4, _>(head);
155
156					for &[x0, x1, x2, x3] in head4 {
157						acc0 = simd.add_f64s(acc0, x0);
158						acc1 = simd.add_f64s(acc1, x1);
159						acc2 = simd.add_f64s(acc2, x2);
160						acc3 = simd.add_f64s(acc3, x3);
161					}
162
163					for &x0 in head1 {
164						acc0 = simd.add_f64s(acc0, x0);
165					}
166
167					acc0 = simd.add_f64s(acc0, acc1);
168					acc2 = simd.add_f64s(acc2, acc3);
169					acc0 = simd.add_f64s(acc0, acc2);
170
171					simd.reduce_sum_f64s(simd.add_f64s(acc0, simd.partial_load_f64s(tail)))
172				}
```

#### fn as_uninit_mut_rsimd_f64s( slice: &mut [MaybeUninit< f64>], ) -> (&mut [MaybeUninit< f64>], &mut [MaybeUninit])

#### fn as_uninit_mut_simd_f64s( slice: &mut [MaybeUninit< f64>], ) -> (&mut [MaybeUninit], &mut [MaybeUninit< f64>])

Source fn conj_mul_add_e_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s

Computes `conj(a) * b + c`

Source fn conj_mul_add_e_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s

Computes `conj(a) * b + c`

Source fn conj_mul_e_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s

Computes `conj(a) * b`

Source fn conj_mul_e_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s

Computes `conj(a) * b`

#### fn deinterleave_shfl_f32s (self, values: T) -> T

#### fn deinterleave_shfl_f64s (self, values: T) -> T

#### fn first_true_m8s(self, mask: Self:: m8s) -> usize

#### fn first_true_m16s(self, mask: Self:: m16s) -> usize

#### fn first_true_m32s(self, mask: Self:: m32s) -> usize

#### fn first_true_m64s(self, mask: Self:: m64s) -> usize

#### fn interleave_shfl_f32s (self, values: T) -> T

#### fn interleave_shfl_f64s (self, values: T) -> T

#### fn mask_between_m8s(self, start: u8, end: u8) -> MemMask 

#### fn mask_between_m16s(self, start: u16, end: u16) -> MemMask 

Source fn mask_between_m32s(self, start: u32, end: u32) -> MemMask 

##### Examples found in repository?

examples/mask_store.rs (line 19)

```
8	fn bench_masked_store(bencher: Bencher, (): ()) {
9		let simd = V4::try_new().unwrap();
10
11		let mut x: __m512d = pulp::cast(simd.splat_f32s(0.0));
12		let x: &mut [f32] = bytemuck::cast_slice_mut(core::slice::from_mut(&mut x));
13		let x = x.as_mut_ptr();
14
15		bencher.bench(|| {
16			simd.vectorize(
17				#[inline(always)]
18				|| unsafe {
19					let mask = simd.mask_between_m32s(3, 13);
20					let raw_mask = mask.mask();
21					mask_mem(simd, raw_mask.into(), x);
22				},
23			)
24		});
25	}
26
27	#[inline]
28	#[target_feature(enable = "avx512f")]
29	unsafe fn mask_mem(simd: V4, mask: pulp::MemMask<pulp::b16>, x: *mut f32) {
30		for _ in 0..16 {
31			let y = simd.mask_load_ptr_f32s(mask, x);
32			core::arch::asm!("/* */", in("zmm0") x);
33			simd.mask_store_ptr_f32s(mask, x, y);
34		}
35	}
36
37	fn bench_combined_stores(bencher: Bencher, (): ()) {
38		let simd = V4::try_new().unwrap();
39
40		let mut x: __m512d = pulp::cast(simd.splat_f32s(0.0));
41		let x: &mut [f32] = bytemuck::cast_slice_mut(core::slice::from_mut(&mut x));
42		let x = x.as_mut_ptr();
43
44		bencher.bench(|| {
45			simd.vectorize(
46				#[inline(always)]
47				|| unsafe {
48					let mask = simd.mask_between_m32s(3, 13);
49					for _ in 0..16 {
50						simd.mask_store_ptr_f32s(mask, x, simd.mask_load_ptr_f32s(mask, x));
51					}
52				},
53			)
54		});
55	}
```

#### fn mask_between_m64s(self, start: u64, end: u64) -> MemMask 

Source unsafe fn mask_load_ptr_f32s( self, mask: MemMask, ptr: *const f32, ) -> Self:: f32s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

##### Examples found in repository?

examples/mask_store.rs (line 31)

```
29	unsafe fn mask_mem(simd: V4, mask: pulp::MemMask<pulp::b16>, x: *mut f32) {
30		for _ in 0..16 {
31			let y = simd.mask_load_ptr_f32s(mask, x);
32			core::arch::asm!("/* */", in("zmm0") x);
33			simd.mask_store_ptr_f32s(mask, x, y);
34		}
35	}
36
37	fn bench_combined_stores(bencher: Bencher, (): ()) {
38		let simd = V4::try_new().unwrap();
39
40		let mut x: __m512d = pulp::cast(simd.splat_f32s(0.0));
41		let x: &mut [f32] = bytemuck::cast_slice_mut(core::slice::from_mut(&mut x));
42		let x = x.as_mut_ptr();
43
44		bencher.bench(|| {
45			simd.vectorize(
46				#[inline(always)]
47				|| unsafe {
48					let mask = simd.mask_between_m32s(3, 13);
49					for _ in 0..16 {
50						simd.mask_store_ptr_f32s(mask, x, simd.mask_load_ptr_f32s(mask, x));
51					}
52				},
53			)
54		});
55	}
```

Source unsafe fn mask_load_ptr_f64s( self, mask: MemMask, ptr: *const f64, ) -> Self:: f64s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_i8s( self, mask: MemMask, ptr: *const i8, ) -> Self:: i8s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_i16s( self, mask: MemMask, ptr: *const i16, ) -> Self:: i16s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_i32s( self, mask: MemMask, ptr: *const i32, ) -> Self:: i32s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_load_ptr_i64s( self, mask: MemMask, ptr: *const i64, ) -> Self:: i64s

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::read`.

Source unsafe fn mask_store_ptr_f32s( self, mask: MemMask, ptr: *mut f32, values: Self:: f32s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

##### Examples found in repository?

examples/mask_store.rs (line 33)

```
29	unsafe fn mask_mem(simd: V4, mask: pulp::MemMask<pulp::b16>, x: *mut f32) {
30		for _ in 0..16 {
31			let y = simd.mask_load_ptr_f32s(mask, x);
32			core::arch::asm!("/* */", in("zmm0") x);
33			simd.mask_store_ptr_f32s(mask, x, y);
34		}
35	}
36
37	fn bench_combined_stores(bencher: Bencher, (): ()) {
38		let simd = V4::try_new().unwrap();
39
40		let mut x: __m512d = pulp::cast(simd.splat_f32s(0.0));
41		let x: &mut [f32] = bytemuck::cast_slice_mut(core::slice::from_mut(&mut x));
42		let x = x.as_mut_ptr();
43
44		bencher.bench(|| {
45			simd.vectorize(
46				#[inline(always)]
47				|| unsafe {
48					let mask = simd.mask_between_m32s(3, 13);
49					for _ in 0..16 {
50						simd.mask_store_ptr_f32s(mask, x, simd.mask_load_ptr_f32s(mask, x));
51					}
52				},
53			)
54		});
55	}
```

Source unsafe fn mask_store_ptr_f64s( self, mask: MemMask, ptr: *mut f64, values: Self:: f64s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_i8s( self, mask: MemMask, ptr: *mut i8, values: Self:: i8s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_i16s( self, mask: MemMask, ptr: *mut i16, values: Self:: i16s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_i32s( self, mask: MemMask, ptr: *mut i32, values: Self:: i32s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source unsafe fn mask_store_ptr_i64s( self, mask: MemMask, ptr: *mut i64, values: Self:: i64s, )

##### § Safety

Addresses corresponding to enabled lanes in the mask have the same restrictions as `core::ptr::write`.

Source fn mul_add_e_c32s( self, a: Self:: c32s, b: Self:: c32s, c: Self:: c32s, ) -> Self:: c32s

Computes `a * b + c`

Source fn mul_add_e_c64s( self, a: Self:: c64s, b: Self:: c64s, c: Self:: c64s, ) -> Self:: c64s

Computes `a * b + c`

Source fn negate_mul_add_e_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s

Computes `-a * b + c`

#### fn negate_mul_add_e_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s

#### fn negate_mul_add_f32s( self, a: Self:: f32s, b: Self:: f32s, c: Self:: f32s, ) -> Self:: f32s

#### fn negate_mul_add_f64s( self, a: Self:: f64s, b: Self:: f64s, c: Self:: f64s, ) -> Self:: f64s

Source fn mul_e_c32s(self, a: Self:: c32s, b: Self:: c32s) -> Self:: c32s

Computes `a * b`

Source fn mul_e_c64s(self, a: Self:: c64s, b: Self:: c64s) -> Self:: c64s

Computes `a * b`

#### fn neg_f32s(self, a: Self:: f32s) -> Self:: f32s

#### fn neg_f64s(self, a: Self:: f64s) -> Self:: f64s

#### fn partial_load_c32s(self, slice: &[c32]) -> Self:: c32s

#### fn partial_load_c64s(self, slice: &[c64]) -> Self:: c64s

Source fn partial_load_f32s(self, slice: &[f32]) -> Self:: f32s

##### Examples found in repository?

examples/dot_product.rs (line 512)

```
468		fn call(self) -> Self::Output {
469			let Self { simd, x, y } = self;
470
471			// x0 x1 x2.. x100
472			// [[x0 x1 x2 x3 x4 x5 x6 x7] [x8 x9 x10.. x15] [..x95]] | [x96 x97 x98 x99 x100]
473			let (xs, x1) = S::as_simd_f32s(x);
474			let (ys, y1) = S::as_simd_f32s(y);
475
476			// sum (x * y)
477			// sum (reduce_sum(X * Y))
478			// reduce_sum(sum (X * Y))
479
480			let mut acc0 = simd.splat_f32s(0.0);
481			let mut acc1 = simd.splat_f32s(0.0);
482			let mut acc2 = simd.splat_f32s(0.0);
483			let mut acc3 = simd.splat_f32s(0.0);
484
485			// 12 registers are being used
486			// 4 for accumulators + 2×4 inside the loop for x[0|1] and y[0|1]
487			let (xs_4, xs_1) = pulp::as_arrays::<4, _>(xs);
488			let (ys_4, ys_1) = pulp::as_arrays::<4, _>(ys);
489
490			for ([x0, x1, x2, x3], [y0, y1, y2, y3]) in iter::zip(xs_4, ys_4) {
491				acc0 = simd.mul_add_f32s(*x0, *y0, acc0);
492				acc1 = simd.mul_add_f32s(*x1, *y1, acc1);
493				acc2 = simd.mul_add_f32s(*x2, *y2, acc2);
494				acc3 = simd.mul_add_f32s(*x3, *y3, acc3);
495			}
496
497			for (x0, y0) in iter::zip(xs_1, ys_1) {
498				acc0 = simd.mul_add_f32s(*x0, *y0, acc0);
499			}
500
501			// reduce_sum_f32s
502			// f32x8 -> f32x4 + f32x4
503			// f32x4 -> f32x2 + f32x2
504			// f32x2 -> f32 + f32
505			acc0 = simd.add_f32s(acc0, acc1);
506			acc2 = simd.add_f32s(acc2, acc3);
507
508			acc0 = simd.add_f32s(acc0, acc2);
509
510			if !x1.is_empty() {
511				acc0 =
512					simd.mul_add_f32s(simd.partial_load_f32s(x1), simd.partial_load_f32s(y1), acc0);
513			}
514
515			simd.reduce_sum_f32s(acc0)
516		}
```

Source fn partial_load_f64s(self, slice: &[f64]) -> Self:: f64s

##### Examples found in repository?

examples/basic.rs (line 121)

```
85					fn call(self) -> Self::Output {
86						let Self { simd, v } = self;
87
88						let (head, tail) = pulp::as_arrays::<8, _>(v);
89
90						let mut acc0 = simd.splat_f64x8(0.0);
91						let mut acc1 = simd.splat_f64x8(0.0);
92						let mut acc2 = simd.splat_f64x8(0.0);
93						let mut acc3 = simd.splat_f64x8(0.0);
94
95						let (head4, head1) = pulp::as_arrays::<4, _>(head);
96
97						for [x0, x1, x2, x3] in head4 {
98							let x0 = pulp::cast(*x0);
99							let x1 = pulp::cast(*x1);
100							let x2 = pulp::cast(*x2);
101							let x3 = pulp::cast(*x3);
102
103							acc0 = pulp::cast(
104								simd.avx512f._mm512_add_pd(pulp::cast(acc0), pulp::cast(x0)),
105							);
106
107							acc0 = simd.add_f64x8(acc0, x0);
108							acc1 = simd.add_f64x8(acc1, x1);
109							acc2 = simd.add_f64x8(acc2, x2);
110							acc3 = simd.add_f64x8(acc3, x3);
111						}
112						for x0 in head1 {
113							let x0 = pulp::cast(*x0);
114							acc0 = simd.add_f64x8(acc0, x0);
115						}
116
117						acc0 = simd.add_f64x8(acc0, acc1);
118						acc2 = simd.add_f64x8(acc2, acc3);
119						acc0 = simd.add_f64x8(acc0, acc2);
120
121						let tail = simd.partial_load_f64s(tail);
122
123						simd.reduce_sum_f64s(simd.add_f64x8(acc0, tail))
124					}
125				}
126
127				simd.vectorize(Imp { simd, v })
128			});
129		}
130	}
131
132	fn sum_pulp_dispatch(bencher: Bencher, len: usize) {
133		let v = &*avec![0.0f64; len];
134
135		bencher.bench(|| {
136			struct Imp<'a> {
137				v: &'a [f64],
138			}
139
140			impl pulp::WithSimd for Imp<'_> {
141				type Output = f64;
142
143				#[inline(always)]
144				fn with_simd<S: Simd>(self, simd: S) -> Self::Output {
145					let Self { v } = self;
146
147					let (head, tail) = S::as_simd_f64s(v);
148
149					let mut acc0 = simd.splat_f64s(0.0);
150					let mut acc1 = simd.splat_f64s(0.0);
151					let mut acc2 = simd.splat_f64s(0.0);
152					let mut acc3 = simd.splat_f64s(0.0);
153
154					let (head4, head1) = pulp::as_arrays::<4, _>(head);
155
156					for &[x0, x1, x2, x3] in head4 {
157						acc0 = simd.add_f64s(acc0, x0);
158						acc1 = simd.add_f64s(acc1, x1);
159						acc2 = simd.add_f64s(acc2, x2);
160						acc3 = simd.add_f64s(acc3, x3);
161					}
162
163					for &x0 in head1 {
164						acc0 = simd.add_f64s(acc0, x0);
165					}
166
167					acc0 = simd.add_f64s(acc0, acc1);
168					acc2 = simd.add_f64s(acc2, acc3);
169					acc0 = simd.add_f64s(acc0, acc2);
170
171					simd.reduce_sum_f64s(simd.add_f64s(acc0, simd.partial_load_f64s(tail)))
172				}
```

#### fn partial_load_i8s(self, slice: &[i8]) -> Self:: i8s

#### fn partial_load_i16s(self, slice: &[i16]) -> Self:: i16s

#### fn partial_load_i32s(self, slice: &[i32]) -> Self:: i32s

#### fn partial_load_i64s(self, slice: &[i64]) -> Self:: i64s

#### fn partial_load_u8s(self, slice: &[u8]) -> Self:: u8s

#### fn partial_load_u16s(self, slice: &[u16]) -> Self:: u16s

#### fn partial_load_u32s(self, slice: &[u32]) -> Self:: u32s

#### fn partial_load_u64s(self, slice: &[u64]) -> Self:: u64s

#### fn partial_store_c32s(self, slice: &mut [c32], values: Self:: c32s)

#### fn partial_store_c64s(self, slice: &mut [c64], values: Self:: c64s)

#### fn partial_store_f32s(self, slice: &mut [f32], values: Self:: f32s)

#### fn partial_store_f64s(self, slice: &mut [f64], values: Self:: f64s)

#### fn partial_store_i8s(self, slice: &mut [i8], values: Self:: i8s)

#### fn partial_store_i16s(self, slice: &mut [i16], values: Self:: i16s)

#### fn partial_store_i32s(self, slice: &mut [i32], values: Self:: i32s)

#### fn partial_store_i64s(self, slice: &mut [i64], values: Self:: i64s)

#### fn partial_store_u8s(self, slice: &mut [u8], values: Self:: u8s)

#### fn partial_store_u16s(self, slice: &mut [u16], values: Self:: u16s)

#### fn partial_store_u32s(self, slice: &mut [u32], values: Self:: u32s)

#### fn partial_store_u64s(self, slice: &mut [u64], values: Self:: u64s)

#### fn rotate_left_c32s(self, a: Self:: c32s, amount: usize) -> Self:: c32s

#### fn rotate_left_c64s(self, a: Self:: c64s, amount: usize) -> Self:: c64s

#### fn rotate_left_f32s(self, a: Self:: f32s, amount: usize) -> Self:: f32s

#### fn rotate_left_f64s(self, a: Self:: f64s, amount: usize) -> Self:: f64s

#### fn rotate_left_i32s(self, a: Self:: i32s, amount: usize) -> Self:: i32s

#### fn rotate_left_i64s(self, a: Self:: i64s, amount: usize) -> Self:: i64s

#### fn rotate_left_u32s(self, a: Self:: u32s, amount: usize) -> Self:: u32s

#### fn rotate_left_u64s(self, a: Self:: u64s, amount: usize) -> Self:: u64s

#### fn rotate_right_f32s(self, a: Self:: f32s, amount: usize) -> Self:: f32s

#### fn rotate_right_f64s(self, a: Self:: f64s, amount: usize) -> Self:: f64s

#### fn rotate_right_i32s(self, a: Self:: i32s, amount: usize) -> Self:: i32s

#### fn rotate_right_i64s(self, a: Self:: i64s, amount: usize) -> Self:: i64s

#### fn select_f32s( self, mask: Self:: m32s, if_true: Self:: f32s, if_false: Self:: f32s, ) -> Self:: f32s

#### fn select_f64s( self, mask: Self:: m64s, if_true: Self:: f64s, if_false: Self:: f64s, ) -> Self:: f64s

#### fn select_i32s( self, mask: Self:: m32s, if_true: Self:: i32s, if_false: Self:: i32s, ) -> Self:: i32s

#### fn select_i64s( self, mask: Self:: m64s, if_true: Self:: i64s, if_false: Self:: i64s, ) -> Self:: i64s

#### fn transmute_f32s_i32s(self, a: Self:: i32s) -> Self:: f32s

#### fn transmute_f32s_u32s(self, a: Self:: u32s) -> Self:: f32s

Source

#### fn transmute_f64s_i64s(self, a: Self:: i64s) -> Self:: f64s

#### fn transmute_f64s_u64s(self, a: Self:: u64s) -> Self:: f64s

#### fn transmute_i32s_f32s(self, a: Self:: f32s) -> Self:: i32s

#### fn transmute_m8s_u8s(self, a: Self:: u8s) -> Self:: m8s

#### fn transmute_u8s_m8s(self, a: Self:: m8s) -> Self:: u8s

#### fn transmute_m16s_u16s(self, a: Self:: u16s) -> Self:: m16s

#### fn transmute_u16s_m16s(self, a: Self:: m16s) -> Self:: u16s

#### fn transmute_m32s_u32s(self, a: Self:: u32s) -> Self:: m32s

#### fn transmute_u32s_m32s(self, a: Self:: m32s) -> Self:: u32s

#### fn transmute_m64s_u64s(self, a: Self:: u64s) -> Self:: m64s

#### fn transmute_u64s_m64s(self, a: Self:: m64s) -> Self:: u64s

#### fn transmute_i8s_u8s(self, a: Self:: u8s) -> Self:: i8s

#### fn transmute_u8s_i8s(self, a: Self:: i8s) -> Self:: u8s

#### fn transmute_u16s_i16s(self, a: Self:: i16s) -> Self:: u16s

#### fn transmute_i16s_u16s(self, a: Self:: u16s) -> Self:: i16s

#### fn transmute_i32s_u32s(self, a: Self:: u32s) -> Self:: i32s

#### fn transmute_i64s_f64s(self, a: Self:: f64s) -> Self:: i64s

#### fn transmute_i64s_u64s(self, a: Self:: u64s) -> Self:: i64s

#### fn transmute_u32s_f32s(self, a: Self:: f32s) -> Self:: u32s

#### fn transmute_u32s_i32s(self, a: Self:: i32s) -> Self:: u32s

#### fn transmute_u64s_f64s(self, a: Self:: f64s) -> Self:: u64s

## Dyn Compatibility§

This trait is not dyn compatible.

In older versions of Rust, dyn compatibility was called "object safety".

## Implementors§

Source§ impl Simd for Scalar

Source§

#### const IS_SCALAR: bool = true

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type c32s = Complex< f32>

Source§

#### type c64s = Complex< f64>

Source§

#### type f32s = f32

Source§

#### type f64s = f64

Source§

#### type i16s = i16

Source§

#### type i32s = i32

Source§

#### type i64s = i64

Source§

#### type i8s = i8

Source§

#### type m16s = bool

Source§

#### type m32s = bool

Source§

#### type m64s = bool

Source§

#### type m8s = bool

Source§

#### type u16s = u16

Source§

#### type u32s = u32

Source§

#### type u64s = u64

Source§

#### type u8s = u8

Source§ impl Simd for Scalar128b

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type m8s = m8x16

Source§

#### type m16s = m16x8

Source§

#### type c32s = f32x4

Source§

#### type c64s = f64x2

Source§

#### type f32s = f32x4

Source§

#### type f64s = f64x2

Source§

#### type i16s = i16x8

Source§

#### type i32s = i32x4

Source§

#### type i64s = i64x2

Source§

#### type i8s = i8x16

Source§

#### type m32s = m32x4

Source§

#### type m64s = m64x2

Source§

#### type u16s = u16x8

Source§

#### type u32s = u32x4

Source§

#### type u64s = u64x2

Source§

#### type u8s = u8x16

Source§ impl Simd for Scalar256b

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type m8s = m8x32

Source§

#### type m16s = m16x16

Source§

#### type c32s = f32x8

Source§

#### type c64s = f64x4

Source§

#### type f32s = f32x8

Source§

#### type f64s = f64x4

Source§

#### type i16s = i16x16

Source§

#### type i32s = i32x8

Source§

#### type i64s = i64x4

Source§

#### type i8s = i8x32

Source§

#### type m32s = m32x8

Source§

#### type m64s = m64x4

Source§

#### type u16s = u16x16

Source§

#### type u32s = u32x8

Source§

#### type u64s = u64x4

Source§

#### type u8s = u8x32

Source§ impl Simd for Scalar512b

Source§

#### const REGISTER_COUNT: usize = 8

Source§

#### type m8s = m8x64

Source§

#### type m16s = m16x32

Source§

#### type c32s = f32x16

Source§

#### type c64s = f64x8

Source§

#### type f32s = f32x16

Source§

#### type f64s = f64x8

Source§

#### type i16s = i16x32

Source§

#### type i32s = i32x16

Source§

#### type i64s = i64x8

Source§

#### type i8s = i8x64

Source§

#### type m32s = m32x16

Source§

#### type m64s = m64x8

Source§

#### type u16s = u16x32

Source§

#### type u32s = u32x16

Source§

#### type u64s = u64x8

Source§

#### type u8s = u8x64

Source§ impl Simd for V2 Available on x86 or x86-64 only.

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type c32s = f32x4

Source§

#### type c64s = f64x2

Source§

#### type f32s = f32x4

Source§

#### type f64s = f64x2

Source§

#### type i16s = i16x8

Source§

#### type i32s = i32x4

Source§

#### type i64s = i64x2

Source§

#### type i8s = i8x16

Source§

#### type m16s = m16x8

Source§

#### type m32s = m32x4

Source§

#### type m64s = m64x2

Source§

#### type m8s = m8x16

Source§

#### type u16s = u16x8

Source§

#### type u32s = u32x4

Source§

#### type u64s = u64x2

Source§

#### type u8s = u8x16

Source§ impl Simd for V3 Available on x86 or x86-64 only.

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type c32s = f32x8

Source§

#### type c64s = f64x4

Source§

#### type f32s = f32x8

Source§

#### type f64s = f64x4

Source§

#### type i16s = i16x16

Source§

#### type i32s = i32x8

Source§

#### type i64s = i64x4

Source§

#### type i8s = i8x32

Source§

#### type m16s = m16x16

Source§

#### type m32s = m32x8

Source§

#### type m64s = m64x4

Source§

#### type m8s = m8x32

Source§

#### type u16s = u16x16

Source§

#### type u32s = u32x8

Source§

#### type u64s = u64x4

Source§

#### type u8s = u8x32

Source§ impl Simd for V4 Available on crate feature `x86-v4` and (x86 or x86-64) only.

Source§

#### const REGISTER_COUNT: usize = 32

Source§

#### type c32s = f32x16

Source§

#### type c64s = f64x8

Source§

#### type f32s = f32x16

Source§

#### type f64s = f64x8

Source§

#### type i16s = i16x32

Source§

#### type i32s = i32x16

Source§

#### type i64s = i64x8

Source§

#### type i8s = i8x64

Source§

#### type m16s = b32

Source§

#### type m32s = b16

Source§

#### type m64s = b8

Source§

#### type m8s = b64

Source§

#### type u16s = u16x32

Source§

#### type u32s = u32x16

Source§

#### type u64s = u64x8

Source§

#### type u8s = u8x64

Source§ impl Simd for V3_128b Available on x86 or x86-64 only.

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type c32s = f32x4

Source§

#### type c64s = f64x2

Source§

#### type f32s = f32x4

Source§

#### type f64s = f64x2

Source§

#### type i16s = i16x8

Source§

#### type i32s = i32x4

Source§

#### type i64s = i64x2

Source§

#### type i8s = i8x16

Source§

#### type m16s = m16x8

Source§

#### type m32s = m32x4

Source§

#### type m64s = m64x2

Source§

#### type m8s = m8x16

Source§

#### type u16s = u16x8

Source§

#### type u32s = u32x4

Source§

#### type u64s = u64x2

Source§

#### type u8s = u8x16

Source§ impl Simd for V3_256b Available on x86 or x86-64 only.

Source§

#### const REGISTER_COUNT: usize = 16

Source§

#### type c32s = f32x8

Source§

#### type c64s = f64x4

Source§

#### type f32s = f32x8

Source§

#### type f64s = f64x4

Source§

#### type i16s = i16x16

Source§

#### type i32s = i32x8

Source§

#### type i64s = i64x4

Source§

#### type i8s = i8x32

Source§

#### type m16s = m16x16

Source§

#### type m32s = m32x8

Source§

#### type m64s = m64x4

Source§

#### type m8s = m8x32

Source§

#### type u16s = u16x16

Source§

#### type u32s = u32x8

Source§

#### type u64s = u64x4

Source§

#### type u8s = u8x32

Source§ impl Simd for V3_512b Available on x86 or x86-64 only.

Source§

#### const REGISTER_COUNT: usize = 8

Source§

#### type c32s = f32x16

Source§

#### type c64s = f64x8

Source§

#### type f32s = f32x16

Source§

#### type f64s = f64x8

Source§

#### type i16s = i16x32

Source§

#### type i32s = i32x16

Source§

#### type i64s = i64x8

Source§

#### type i8s = i8x64

Source§

#### type m16s = m16x32

Source§

#### type m32s = m32x16

Source§

#### type m64s = m64x8

Source§

#### type m8s = m8x64

Source§

#### type u16s = u16x32

Source§

#### type u32s = u32x16

Source§

#### type u64s = u64x8

Source§

#### type u8s = u8x64