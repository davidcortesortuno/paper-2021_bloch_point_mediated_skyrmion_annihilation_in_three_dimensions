#!/bin/bash

sim () {
	BZ=$1
	python ../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --bz ${BZ} \
		--sim_name "sk-tube_to_one-dim-mod_Bz${BZ}mT_REFINED" \
		--add_image "npys/sk-tube_to_one-dim-mod_Bz480mT_CI_303/image_000000.npy" \
		--add_image "npys/sk-tube_to_one-dim-mod_Bz480mT_CI_303/image_000003.npy" \
		--add_image "npys/sk-tube_to_one-dim-mod_Bz480mT_CI_303/image_000004.npy" \
		--add_interpolations 10 \
		--add_interpolations 10 \
		--stopping_dydt "6e-6" --max_steps 100 --spring_constant 1 \
        --keep_sim_climbing_image 2e-6 \
        --keep_sim_climbing_image_steps 200 \
		--save_m_every 400
}

export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
export OMP_NUM_THREADS=6 && sim 480
