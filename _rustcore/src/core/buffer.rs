//! Flat reusable buffers for the designated RF-01 synthetic fixture.

use rayon::prelude::*;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SizingObservation {
    pub allocations: u64,
}

#[derive(Debug)]
pub struct FixtureBuffers {
    size: usize,
    state: Vec<f64>,
    operator: Vec<f64>,
    rk_stages: Vec<f64>,
    dense_solve: Vec<f64>,
    stencil: Vec<f64>,
}

impl FixtureBuffers {
    pub fn new(size: usize) -> Result<(Self, SizingObservation), &'static str> {
        let rk_size = size
            .checked_mul(4)
            .ok_or("four-stage workspace size overflow")?;
        Ok((
            Self {
                size,
                state: vec![0.0; size],
                operator: vec![0.0; size],
                rk_stages: vec![0.0; rk_size],
                dense_solve: vec![0.0; size],
                stencil: vec![0.0; size],
            },
            SizingObservation { allocations: 5 },
        ))
    }

    pub const fn size(&self) -> usize {
        self.size
    }

    pub fn capacities(&self) -> [usize; 5] {
        [
            self.state.capacity(),
            self.operator.capacity(),
            self.rk_stages.capacity(),
            self.dense_solve.capacity(),
            self.stencil.capacity(),
        ]
    }

    pub fn all_zero(&self) -> bool {
        self.state
            .iter()
            .chain(&self.operator)
            .chain(&self.rk_stages)
            .chain(&self.dense_solve)
            .chain(&self.stencil)
            .all(|value| *value == 0.0)
    }

    pub fn reset(&mut self) {
        self.state.fill(0.0);
        self.operator.fill(0.0);
        self.rk_stages.fill(0.0);
        self.dense_solve.fill(0.0);
        self.stencil.fill(0.0);
    }

    pub fn load_input(&mut self, input: &[f64]) -> Result<(), &'static str> {
        if input.len() != self.size {
            return Err("input length does not match the workspace");
        }
        self.state.copy_from_slice(input);
        Ok(())
    }

    /// Run the allocation-free inner loop after explicit workspace sizing.
    ///
    /// Every element is independent within each phase. Indexed parallel fills
    /// therefore preserve output order and the scalar operation order for a
    /// fixed element across private-pool sizes.
    pub fn run_designated_fixture(&mut self, steps: usize, table: &[f64; 4]) {
        let size = self.size;
        for _ in 0..steps {
            {
                let state = &self.state;
                self.operator
                    .par_iter_mut()
                    .enumerate()
                    .for_each(|(index, value)| {
                        let left = state[(index + size - 1) % size];
                        let right = state[(index + 1) % size];
                        *value = table[0] * state[index] + table[1] * (right - left);
                    });
            }
            {
                let state = &self.state;
                let operator = &self.operator;
                self.rk_stages
                    .par_chunks_exact_mut(4)
                    .enumerate()
                    .for_each(|(index, stages)| {
                        let k1 = operator[index];
                        let k2 = k1 + table[2] * state[index];
                        let k3 = k2 + table[2] * k1;
                        let k4 = k3 + table[3] * k2;
                        stages.copy_from_slice(&[k1, k2, k3, k4]);
                    });
            }
            {
                let state = &self.state;
                let stages = &self.rk_stages;
                self.dense_solve
                    .par_iter_mut()
                    .enumerate()
                    .for_each(|(index, value)| {
                        let base = 4 * index;
                        let update = stages[base]
                            + 2.0 * stages[base + 1]
                            + 2.0 * stages[base + 2]
                            + stages[base + 3];
                        *value = (state[index] + update / 6.0) / 1.125;
                    });
            }
            {
                let dense = &self.dense_solve;
                self.stencil
                    .par_iter_mut()
                    .enumerate()
                    .for_each(|(index, value)| {
                        let left = dense[(index + size - 1) % size];
                        let right = dense[(index + 1) % size];
                        *value = 0.25 * left + 0.5 * dense[index] + 0.25 * right;
                    });
            }
            self.state.copy_from_slice(&self.stencil);
        }
    }

    pub fn owned_output(&self) -> Vec<f64> {
        self.state.clone()
    }
}
