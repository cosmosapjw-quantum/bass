# G-POL-LIOUVILLE-II-B2B literature and algorithm boundary

## Primary external checks

1. Ning Wang and Jin-Luen Lee, *Geometric Properties of the Icosahedral-Hexagonal Grid on the Two-Sphere*, SIAM J. Sci. Comput. 33 (2011) 2536–2559, DOI 10.1137/090761355. The paper describes icosahedral grids obtained by subdividing icosahedron faces and projecting new vertices to the sphere, and distinguishes recursive and nonrecursive constructions.

2. Maria Francesca Carfora, *Semi-Lagrangian advection on a spherical geodesic grid*, Int. J. Numer. Meth. Fluids 55 (2007) 127–142, DOI 10.1002/fld.1445. The method combines a geodesic triangulation with backward characteristic departure points and interpolation, and assesses solid-body rotation and deformation-flow tests.

3. Fuqiang Lu et al., *High-Order Semi-Lagrangian Schemes for the Transport Equation on Icosahedron Spherical Grids*, Atmosphere 13 (2022) 1807, DOI 10.3390/atmos13111807. It formulates the sphere problem in three-dimensional Cartesian coordinates and separates backward departure integration from interpolation at the departure point. It also records the diffusion of linear interpolation and the nonconservative character of ordinary semi-Lagrangian interpolation.

4. SciPy `scipy.spatial.ConvexHull` documentation and the Qhull manual. `ConvexHull.simplices` exposes simplicial hull facets and SciPy delegates hull construction to Qhull. BASS uses this only as an independent Python oracle for the recursively generated Rust icosphere; Qhull is not a Rust runtime dependency.

## BASS-owned authority

B2B does not import a scalar tracer remapper as polarization authority. The runtime path is:

`backward PR11 characteristic -> deterministic spherical face/stencil -> PR14 common-screen packed-tensor remap -> forward PR11 characteristic`.

The concrete mesh is a recursively refined regular icosahedron. Face location uses radial intersection with a planar hull facet,

`lambda e = sum_i w_i v_i`,

with finite convex barycentric weights and deterministic lexicographic edge/vertex tie-breaking. The B2A common-screen transport remains responsible for polarization gauge covariance. PR13 remains the local Stokes-sign authority, including `packed[8] = -V/2`.

## Explicit non-claims

This checkpoint is not Qhull in Rust, a general spherical Delaunay library, a conservative flux-form method, a high-order/nonconvex interpolator, a HEALPix adapter, or a production search accelerator. It does not establish map-level E/B or power-spectrum accuracy.
