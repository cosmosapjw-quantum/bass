(* ::Package:: *)

BeginPackage["BASS`IR`"];

ExactScalarAST::usage = "ExactScalarAST[expr] converts an exact scalar to a semantic AST.";
ExactScalarASTQ::usage = "ExactScalarASTQ[ast] validates an exact-scalar AST.";

Begin["`Private`"];

ClearAll[ExactScalarAST, ExactScalarASTQ, convertExact, astListQ];
ExactScalarAST::inexact = "Inexact numbers are forbidden in exact scalar authority: `1`.";

ExactScalarAST[expr_] := If[! FreeQ[Unevaluated[expr], _Real],
 Message[ExactScalarAST::inexact, HoldForm[expr]];
 Failure["InexactScalar", <|"expression" -> HoldForm[expr]|>],
 convertExact[Unevaluated[expr]]];
convertExact[n_Integer] := <|"type" -> "integer", "value" -> n|>;
convertExact[r_Rational] := <|"type" -> "rational",
 "numerator" -> Numerator[r], "denominator" -> Denominator[r]|>;
convertExact[s_Symbol] := <|"type" -> "symbol", "name" -> SymbolName[Unevaluated[s]]|>;
convertExact[expr_Plus] := <|"type" -> "sum",
 "arguments" -> (convertExact /@ SortBy[List @@ Unevaluated[expr], ToString[#, InputForm] &])|>;
convertExact[expr_Times] := <|"type" -> "product",
 "arguments" -> (convertExact /@ SortBy[List @@ Unevaluated[expr], ToString[#, InputForm] &])|>;
convertExact[Power[base_, Rational[1, 2]]] := <|"type" -> "sqrt", "argument" -> convertExact[base]|>;
convertExact[Power[base_, exponent_]] := <|"type" -> "power",
 "base" -> convertExact[base], "exponent" -> convertExact[exponent]|>;
convertExact[expr_] /; AtomQ[Unevaluated[expr]] := <|"type" -> "atom",
 "input_form" -> ToString[Unevaluated[expr], InputForm]|>;
convertExact[expr_] := <|"type" -> "call", "head" -> ToString[Head[Unevaluated[expr]], InputForm],
 "arguments" -> (convertExact /@ List @@ Unevaluated[expr])|>;
astListQ[value_] := ListQ[value] && AllTrue[value, ExactScalarASTQ];

ExactScalarASTQ[ast_Association] := Switch[Lookup[ast, "type", Missing["KeyAbsent"]],
 "integer", IntegerQ[Lookup[ast, "value", None]],
 "rational", IntegerQ[Lookup[ast, "numerator", None]] &&
  IntegerQ[Lookup[ast, "denominator", None]] && Lookup[ast, "denominator", 0] =!= 0,
 "symbol", StringQ[Lookup[ast, "name", None]],
 "sum" | "product", astListQ[Lookup[ast, "arguments", None]],
 "sqrt", ExactScalarASTQ[Lookup[ast, "argument", None]],
 "power", ExactScalarASTQ[Lookup[ast, "base", None]] && ExactScalarASTQ[Lookup[ast, "exponent", None]],
 "call", StringQ[Lookup[ast, "head", None]] && astListQ[Lookup[ast, "arguments", None]],
 "atom", StringQ[Lookup[ast, "input_form", None]],
 _, False];
ExactScalarASTQ[_] := False;

End[];
EndPackage[];
