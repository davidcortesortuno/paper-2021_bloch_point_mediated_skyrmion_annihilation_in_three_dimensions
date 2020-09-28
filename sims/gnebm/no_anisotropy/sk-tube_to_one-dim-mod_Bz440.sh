#!/bin/bash

sim () {
	BZ=$1
	python ../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --bz ${BZ} \
		--sim_name "sk-tube_to_one-dim-mod_Bz${BZ}mT" \
		--add_image "../../equilibrium_states/no_cubic_anisotropy/npys/sk_tube/m_sk_tube_Bz_000${BZ}.npy" \
		--add_image "../../equilibrium_states/no_cubic_anisotropy/npys/one_dim_mod/m_one_dim_mod_Bz_000${BZ}.npy" \
		--add_interpolations 30 \
		--stopping_dydt "8e-6" --max_steps 300 --spring_constant 1 \
        --keep_sim_climbing_image 4e-6 \
        --keep_sim_climbing_image 2e-6 \
		--save_m_every 400
}

export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
export OMP_NUM_THREADS=3 && sim 440
