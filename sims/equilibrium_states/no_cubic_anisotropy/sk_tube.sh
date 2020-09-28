#!/bin/bash

python ../eq_state_relaxation.py --nx 30 --ny 30 --nz 30 \
                                 --j 1 --d "0.727" --mu_s 1 \
                                 --initial_state_sk_tube 3 \
                                 --bz_min 300 --bz_max 500 --bz_steps 11 \
                                 --sim_name "sk_tube" \
                                 --stopping_dmdt "1e-6"
