#!/bin/bash

sim () {
	BZ=$1
	python ../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --bz ${BZ} \
		--sim_name "sk-tube_to_one-dim-mod_Bz${BZ}mT_REFINED_LINEAR" \
		--add_image "npys/sk-tube_to_one-dim-mod_Bz380mT_CI_251/image_000000.npy" \
		--add_image "npys/sk-tube_to_one-dim-mod_Bz380mT_CI_251/image_000007.npy" \
		--add_image "npys/sk-tube_to_one-dim-mod_Bz380mT_CI_251/image_000012.npy" \
		--add_interpolations 15 \
		--add_interpolations 15 \
		--interpolation_method "linear" \
		--stopping_dydt "5e-7" --max_steps 250 --spring_constant 1 \
        --keep_sim_climbing_image 1e-7 \
        --keep_sim_climbing_image_steps 500 \
		--save_m_every 1500
}

export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
export OMP_NUM_THREADS=6 && sim 380
