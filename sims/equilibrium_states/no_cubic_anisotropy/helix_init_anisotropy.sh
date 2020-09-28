#!/bin/bash

python ../eq_state_relaxation.py --nx 30 --ny 30 --nz 30 \
                                 --j 1 --d "0.727" --mu_s 1 --kc "-0.05" \
                                 --initial_state_helix_angle_x 90 10 \
                                 --bz_min 100 --bz_max 101 --bz_steps 1 \
                                 --save_initial_state \
                                 --sim_name "helix_L10_anisotropy_test" \
                                 --stopping_dmdt "1e-5" 
