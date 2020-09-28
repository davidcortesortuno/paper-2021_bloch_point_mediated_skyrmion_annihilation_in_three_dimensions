#!/bin/bash

python ../eq_state_relaxation.py --nx 30 --ny 30 --nz 30 \
                                 --j 1 --d "0.727" --kc "-0.05" --mu_s 1 \
                                 --initial_state_sk_tube 3 \
                                 --bz_min 260 --bz_max 261 --bz_steps 1 \
                                 --sim_name "sk_tube_kc-5e-2" \
                                 --stopping_dmdt "1e-6"
