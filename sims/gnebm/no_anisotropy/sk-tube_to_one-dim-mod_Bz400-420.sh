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
		--stopping_dydt "1e-5" --max_steps 250 --spring_constant 1 \
        --keep_sim_climbing_image 5e-6 \
        --keep_sim_climbing_image 2.5e-6 \
		--save_m_every 400
}

for ((bz=400; bz<421; bz+=20))
do
	export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
	export OMP_NUM_THREADS=5 && sim ${bz}
done
