#!/bin/bash

python ../eq_state_relaxation.py --nx 30 --ny 30 --nz 30 \
                                 --j 1 --d "0.727" --mu_s 1 \
                                 --initial_state_sk_tube 3 \
                                 --bz_min 400 --bz_max 401 --bz_steps 1 \
                                 --save_initial_state \
                                 --sim_name "sk_tube_INIT" \
                                 --stopping_dmdt "10"
