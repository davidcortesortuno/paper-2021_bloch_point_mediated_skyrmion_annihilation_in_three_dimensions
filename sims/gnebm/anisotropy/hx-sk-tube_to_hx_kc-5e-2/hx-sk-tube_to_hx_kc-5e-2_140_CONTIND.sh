#!/bin/bash

sim () {
	# BZ=$1
    printf -v BZ "%06d" $1
	python ../../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --kc "-0.05" --bz ${BZ} \
		--sim_name "hx-sk-tube_to_hx_Bz${BZ}mT_REFINED_CONT" \
		--add_images_folder "npys/hx-sk-tube_to_hx_Bz000140mT_REFINED_1000" \
		--stopping_dydt "2e-6" --max_steps 400 --spring_constant 1 \
        --keep_sim_climbing_image 1e-6 \
		--save_m_every 400 \
        --integrator "sundials" \
        --interpolation_method "rotation"
}

export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
export OMP_NUM_THREADS=5 && sim 140
