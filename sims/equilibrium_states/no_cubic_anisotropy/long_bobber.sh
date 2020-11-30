#!/bin/bash

python ../eq_state_relaxation.py --nx 30 --ny 30 --nz 30 \
                                 --j 1 --d "0.727" --mu_s 1 \
                                 --initial_state_one_bobber 5 \
                                 --bz_min 300 --bz_max 400 --bz_steps 6 \
                                 --sim_name "long_bobber" \
                                 --stopping_dmdt "1e-6"
