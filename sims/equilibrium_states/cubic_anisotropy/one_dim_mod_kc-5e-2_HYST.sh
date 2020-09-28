#!/bin/bash

python ../eq_state_relaxation.py --nx 30 --ny 30 --nz 30 \
                                 --j 1 --d "0.727" --kc "-0.05" --mu_s 1 \
                                 --initial_state_one_dim_mod \
                                 --bz_min 000 --bz_max 600 --bz_steps 31 \
                                 --sim_name "one_dim_mod_kc-5e-2_HYST" \
                                 --bz_hysteresis \
                                 --stopping_dmdt "1e-6"
