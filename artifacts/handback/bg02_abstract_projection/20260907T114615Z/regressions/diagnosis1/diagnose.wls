Needs["xAct`xTensor`"];
Get["/mnt/sn850x2t/local_ai_foundry/70_experiments/bg02-abstract-projection-20260907T114615Z/checkout/artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/source/wolfram/BASS/Kernel/Authority/BG02Convention.wl"];
Get["/mnt/sn850x2t/local_ai_foundry/70_experiments/bg02-abstract-projection-20260907T114615Z/checkout/artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/source/wolfram/BASS/Kernel/Background/EinsteinProjection.wl"];
Get["/mnt/sn850x2t/local_ai_foundry/70_experiments/bg02-abstract-projection-20260907T114615Z/regressions/diagnosis1/instrumented.wl"];
x=Catch[BASS`Research`AP1`BuildAbstractProjectionProof[],_,Function[{value,tag},<|"caught"->HoldForm[value],"tag"->tag|>]];
Print["DIAG_RESULT ",InputForm[x]];
Exit[0];
