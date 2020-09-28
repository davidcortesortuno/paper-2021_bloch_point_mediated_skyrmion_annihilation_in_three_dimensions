#!/bin/bash

sim () {
	# BZ=$1
    printf -v BZ "%06d" $1
	python ../../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --kc "-0.05" --bz ${BZ} \
		--sim_name "hx-sk-tube_to_hx_Bz${BZ}mT_REFINED" \
		--add_image "npys/hx-sk-tube_to_hx_Bz000060mT_CI_221/image_000000.npy" \
		--add_image "npys/hx-sk-tube_to_hx_Bz000060mT_CI_221/image_000002.npy" \
		--add_image "npys/hx-sk-tube_to_hx_Bz000060mT_CI_221/image_000007.npy" \
		--add_interpolations 14 \
		--add_interpolations 14 \
		--stopping_dydt "8e-6" --max_steps 100 --spring_constant 1 \
        --keep_sim_climbing_image 4e-6 \
        --keep_sim_climbing_image_steps 100 \
		--save_m_every 400 \
        --integrator "sundials" \
        --interpolation_method "rotation"
}

export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
export OMP_NUM_THREADS=6 && sim 60
