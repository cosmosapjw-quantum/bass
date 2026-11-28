# C8-time-refinement | R118-C4K BASS

Two independent actual native time grids, fixed radial quadrature, comparing composed tangent convergence and Gauss/det derivative: {
  "runs": [
    {
      "steps": 2048,
      "exit": 0,
      "seconds": 30.448878566036,
      "cmd": [
        "/home/cosmosapjw/r118c4k_bass_shadow/_rustcore/target/release/examples/c3x_radial",
        "/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c3l_reachable_sky/clock.csv",
        "/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c4k_composite_tangent/p0.ctrl",
        "2048",
        "192",
        "8",
        "8"
      ]
    },
    {
      "steps": 8192,
      "exit": 0,
      "seconds": 131.35995378997177,
      "cmd": [
        "/home/cosmosapjw/r118c4k_bass_shadow/_rustcore/target/release/examples/c3x_radial",
        "/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c3l_reachable_sky/clock.csv",
        "/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c4k_composite_tangent/p0.ctrl",
        "8192",
        "192",
        "8",
        "8"
      ]
    }
  ],
  "rows": [
    {
      "epoch": 0,
      "gauss_tangent": [
        -8.702219914517883e-10,
        -2.1770216733015435e-10,
        -5.44430776742189e-11
      ],
      "det_tangent": [
        6.013933925505532e-20,
        -2.702035101741218e-19,
        2.388632911257127e-19
      ],
      "lnH": [
        5.269880435947331e-07,
        5.273143002321632e-07,
        5.273959295663046e-07
      ],
      "I": {
        "difference": [
          6.006388708868371e-11,
          1.4814520537751393e-11
        ],
        "ratio": 4.0543929137378925,
        "fine_norm": 1.4191366246080455e-05
      },
      "E": {
        "difference": [
          2.3916431177366776e-12,
          5.839236007328765e-13
        ],
        "ratio": 4.095815128443089,
        "fine_norm": 1.690424232943595e-07
      },
      "B": {
        "difference": [
          4.788081895308744e-18,
          1.1195748940304877e-18
        ],
        "ratio": 4.276696378990397,
        "fine_norm": 1.2945369607627623e-12
      }
    },
    {
      "epoch": 1,
      "gauss_tangent": [
        -3.620001960031145e-09,
        -9.055766968531244e-10,
        -2.2646491894390755e-10
      ],
      "det_tangent": [
        8.724439356719293e-20,
        -5.234663614031576e-19,
        1.7025362239811437e-19
      ],
      "lnH": [
        3.493553342943058e-07,
        3.5071249070363866e-07,
        3.510520430802419e-07
      ],
      "I": {
        "difference": [
          1.5149008645947608e-10,
          3.7691777900842125e-11
        ],
        "ratio": 4.019181235175734,
        "fine_norm": 1.10770955420672e-05
      },
      "E": {
        "difference": [
          3.0516565534501073e-12,
          7.464590785435675e-13
        ],
        "ratio": 4.088176621020218,
        "fine_norm": 2.517168605721345e-07
      },
      "B": {
        "difference": [
          3.604916692226709e-18,
          9.661134783392078e-19
        ],
        "ratio": 3.7313594862828348,
        "fine_norm": 3.5301568602984614e-14
      }
    }
  ],
  "scope": "matched native 2048/4096/8192 early steps plus quarter-count late; identical radial quadrature and control; finite step sensitivity convergence, not continuum proof"
}

