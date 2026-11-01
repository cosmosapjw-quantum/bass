//! Bounded persistent workers with indexed, caller-ordered results.
//! Scheduling never performs a floating-point reduction.
use crate::ForwardError;
use std::fmt;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::{mpsc, Arc, Mutex};
use std::thread::{self, JoinHandle};

type Job = Box<dyn FnOnce() + Send + 'static>;
fn bad(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}

pub struct OrderedWorkerPool {
    width: usize,
    sender: Option<mpsc::SyncSender<Job>>,
    workers: Vec<JoinHandle<()>>,
}
impl fmt::Debug for OrderedWorkerPool {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("OrderedWorkerPool")
            .field("width", &self.width)
            .finish()
    }
}
impl OrderedWorkerPool {
    pub fn new(width: usize) -> Result<Self, ForwardError> {
        if !(1..=64).contains(&width) {
            return Err(bad("AXBI_TRANSPORT_THREADS"));
        }
        if width == 1 {
            return Ok(Self {
                width,
                sender: None,
                workers: Vec::new(),
            });
        }
        let (sender, receiver) = mpsc::sync_channel::<Job>(2 * width);
        let receiver = Arc::new(Mutex::new(receiver));
        let mut workers = Vec::with_capacity(width);
        for index in 0..width {
            let receiver = Arc::clone(&receiver);
            match thread::Builder::new()
                .name(format!("rei-cell-{index}"))
                .spawn(move || loop {
                    let message = match receiver.lock() {
                        Ok(r) => r.recv(),
                        Err(_) => return,
                    };
                    match message {
                        Ok(job) => job(),
                        Err(_) => return,
                    }
                }) {
                Ok(worker) => workers.push(worker),
                Err(_) => {
                    drop(sender);
                    for worker in workers {
                        let _ = worker.join();
                    }
                    return Err(bad("AXBI_WORKER_SPAWN"));
                }
            }
        }
        Ok(Self {
            width,
            sender: Some(sender),
            workers,
        })
    }
    pub fn width(&self) -> usize {
        self.width
    }
    /// Dynamic contiguous chunks, finite job/result channels. All launched work
    /// is collected before the lowest-index cell error is returned.
    pub fn map_ordered<T, F>(&self, count: usize, function: F) -> Result<Vec<T>, ForwardError>
    where
        T: Send + 'static,
        F: Fn(usize) -> Result<T, ForwardError> + Send + Sync + 'static,
    {
        if self.width == 1 {
            return (0..count)
                .map(|index| {
                    catch_unwind(AssertUnwindSafe(|| function(index)))
                        .unwrap_or_else(|_| Err(bad("AXBI_WORKER_TASK_PANIC")))
                })
                .collect();
        }
        if count == 0 {
            return Ok(Vec::new());
        }
        let stride = count.div_ceil(4 * self.width).max(1);
        let jobs = count.div_ceil(stride);
        let (reply, received) = mpsc::sync_channel(jobs);
        let function = Arc::new(function);
        for start in (0..count).step_by(stride) {
            let end = (start + stride).min(count);
            let work = Arc::clone(&function);
            let reply = reply.clone();
            self.sender
                .as_ref()
                .ok_or_else(|| bad("AXBI_WORKER_CLOSED"))?
                .send(Box::new(move || {
                    let values = (start..end)
                        .map(|index| {
                            catch_unwind(AssertUnwindSafe(|| work(index)))
                                .unwrap_or_else(|_| Err(bad("AXBI_WORKER_TASK_PANIC")))
                        })
                        .collect::<Vec<_>>();
                    drop(work);
                    let _ = reply.send((start, values));
                }))
                .map_err(|_| bad("AXBI_WORKER_CLOSED"))?;
        }
        drop(reply);
        drop(function);
        let mut slots = (0..count)
            .map(|_| None)
            .collect::<Vec<Option<Result<T, ForwardError>>>>();
        for _ in 0..jobs {
            let (start, values) = received.recv().map_err(|_| bad("AXBI_WORKER_RESULT"))?;
            for (offset, value) in values.into_iter().enumerate() {
                slots[start + offset] = Some(value);
            }
        }
        slots
            .into_iter()
            .map(|slot| slot.ok_or_else(|| bad("AXBI_WORKER_RESULT"))?)
            .collect()
    }
}
impl Drop for OrderedWorkerPool {
    fn drop(&mut self) {
        drop(self.sender.take());
        for worker in self.workers.drain(..) {
            let _ = worker.join();
        }
    }
}
