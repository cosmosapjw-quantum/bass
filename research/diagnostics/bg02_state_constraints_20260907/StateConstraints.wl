(* ::Package:: *)
(* Exact, dimensionful 1+3/ONF state-to-constraint research adapter.
   PREPARED_UNEXECUTED: not installed by BASS init.wl, not a production RHS.
   No owner coefficient, connection generator, or curvature formula is copied.
   Dependencies are loaded by the caller; see run_state_constraints.wls. *)
BeginPackage["BASS`Research`"];
BG02StateConstraints::usage =
 "BG02StateConstraints[state, Assumptions->...] computes homogeneous Hamiltonian and momentum residuals from full exact ONF tensors using the existing BASS owner/geometry/projection APIs. It never projects the input onto a constraint surface.";
Begin["`Private`"];
ClearAll[BG02StateConstraints];
Options[BG02StateConstraints] = {Assumptions -> True};
BG02StateConstraints[state_Association, OptionsPattern[]] := Module[
 {keys, asm, a, n, sig, h, rho, q, lam, kg, values, realCondition,
  zeroQ, simplify, owner, gamma, ricci, k, divK, r3, s2, seed, hr, mr},
 keys = {"Hgeom","aB","nB","sigma","rho","q","Lambda","kappaG"};
 If[Sort[Keys[state]] =!= Sort[keys],
   Return[Failure["StateKeys", <|"required"->keys,"observed"->Keys[state]|>]]];
 asm = OptionValue[Assumptions];
 If[asm === False, Return[Failure["InvalidAssumptions",<||>]]];
 a=state["aB"]; n=state["nB"]; sig=state["sigma"]; h=state["Hgeom"];
 rho=state["rho"]; q=state["q"]; lam=state["Lambda"]; kg=state["kappaG"];
 If[!VectorQ[a] || Dimensions[a]=!={3} || !VectorQ[q] || Dimensions[q]=!={3} ||
    !MatrixQ[n] || Dimensions[n]=!={3,3} ||
    !MatrixQ[sig] || Dimensions[sig]=!={3,3} ||
    !AllTrue[{h,rho,lam,kg}, Dimensions[#] === {} &],
   Return[Failure["StateShape",<||>]]];
 values=Flatten[{a,n,sig,h,rho,q,lam,kg}];
 (* This exact-symbolic reference does not choose a floating-point tolerance.
    Numerical-domain policy belongs to a later, separately verified adapter. *)
 If[!FreeQ[values, _Real | _DirectedInfinity | Indeterminate],
   Return[Failure["ExactInputRequired",<||>]]];
 realCondition=And@@(Element[#,Reals]& /@ values);
 If[!TrueQ[FullSimplify[realCondition,Assumptions->asm]],
   Return[Failure["RealInputNotEstablished",<||>]]];
 If[!TrueQ[FullSimplify[kg>0,Assumptions->asm]],
   Return[Failure["PositiveKappaNotEstablished",<||>]]];
 zeroQ[x_] := AllTrue[Flatten[{x}], TrueQ[FullSimplify[#==0,Assumptions->asm]]&];
 simplify[x_] := FullSimplify[x,Assumptions->asm];
 If[!zeroQ[n-Transpose[n]], Return[Failure["NNotSymmetric",<||>]]];
 If[!zeroQ[sig-Transpose[sig]] || !zeroQ[Tr[sig]],
   Return[Failure["ShearNotSTF",<||>]]];
 If[!zeroQ[n.a], Return[Failure["JacobiNotEstablished",<|"residual"->n.a|>]]];
 (* A failed/unproved algebraic domain check is never repaired by symmetrizing,
    trace removal, diagonalization, or clamping. Einstein residuals may be nonzero. *)
 If[Min[Length[DownValues[BASS`Authority`BG02ConventionRegistry]],
        Length[DownValues[BASS`Geometry`LeviCivitaConnection]],
        Length[DownValues[BASS`Geometry`ONFRicciTensor]],
        Length[DownValues[BASS`Background`HamiltonianProjection]],
        Length[DownValues[BASS`Background`MomentumProjection]]] === 0,
   Return[Failure["MissingBG02Dependency",<||>]]];
 owner=BASS`Authority`BG02ConventionRegistry[];
 If[FailureQ[owner],Return[owner]];
 If[!AssociationQ[owner] || Lookup[owner,"contract_id",None]=!="BASS_BG02_OWNER_CONVENTION_V2",
   Return[Failure["UnexpectedBG02Owner",<||>]]];
 gamma=BASS`Geometry`LeviCivitaConnection[a,n];
 If[FailureQ[gamma],Return[gamma]];
 If[Dimensions[gamma]=!={3,3,3},Return[Failure["ConnectionNotEvaluated",<||>]]];
 ricci=BASS`Geometry`ONFRicciTensor[a,n];
 If[FailureQ[ricci],Return[ricci]];
 If[Dimensions[ricci]=!={3,3},Return[Failure["RicciNotEvaluated",<||>]]];
 k=h IdentityMatrix[3]+sig;
 (* Generated storage is {output, derivative-direction, differentiated-basis}.
    e_j(K_ik)=0, not D_j(K_ik)=0. Both free-index connection terms survive. *)
 divK=simplify@Table[-Sum[
   gamma[[m,j,i]] k[[m,j]] + gamma[[m,j,j]] k[[i,m]],
   {j,3},{m,3}],{i,3}];
 r3=simplify[Tr[ricci]];
 s2=simplify[Tr[sig.sig]];
 seed=<|"R3"->r3,"H"->h,"sigma2"->s2,
   "Lambda"->lam,"kappaG"->kg,"rho"->rho|>;
 hr=BASS`Background`HamiltonianProjection[seed];
 mr=Table[BASS`Background`MomentumProjection[
   Join[seed,<|"DivergenceK"->divK[[i]],"GradientK"->0,
     "qComponent"->q[[i]]|>]],{i,3}];
 If[!FreeQ[{hr,mr},_Failure],
   Return[Failure["ConstraintConsumerFailure",<|"Hamiltonian"->hr,"Momentum"->mr|>]]];
 hr=simplify[hr]; mr=simplify[mr];
 If[Dimensions[hr]=!={} || Dimensions[mr]=!={3},
   Return[Failure["ConstraintOutputShape",<||>]]];
 <|"status"->"EVALUATED_COMPONENTS_ONLY", "owner_contract"->owner["contract_id"],
   "InputState"->state, "Hamiltonian"->hr, "Momentum"->mr,
   "Jacobi"->simplify[n.a],
   "Carriers"-><|"Ricci"->simplify[ricci],"R3"->r3,"K"->k,
     "sigma2"->s2,"DivergenceK"->divK,"GradientK"->ConstantArray[0,3]|>,
   "domain"->"EXACT_REAL_SPATIALLY_HOMOGENEOUS_ONF",
   "native_xact"->False,"production_admitted"->False|>
];
BG02StateConstraints[___] := Failure["StateShape",<||>];
End[];
EndPackage[];
