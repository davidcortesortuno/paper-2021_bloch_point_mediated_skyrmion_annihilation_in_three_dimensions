#!/bin/bash

sim () {
	BZ=$1
	python ../../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --kc "-0.05" --bz ${BZ} \
		--sim_name "sk-tube_to_conical_Bz${BZ}mT" \
		--add_image "../../../equilibrium_states/cubic_anisotropy/npys/sk_tube_kc-5e-2/m_sk_tube_kc-5e-2_Bz_000${BZ}.npy" \
		--add_image "../../../equilibrium_states/cubic_anisotropy/npys/one_dim_mod_kc-5e-2/m_one_dim_mod_kc-5e-2_Bz_000${BZ}.npy" \
		--add_interpolations 28 \
		--stopping_dydt "1e-5" --max_steps 250 --spring_constant 1 \
		--save_m_every 500 \
        --interpolation_method "rotation" \
        --keep_sim_climbing_image "6e-6" \
        --keep_sim_climbing_image_again "4e-6"
}

for ((bz=370; bz>369; bz-=20))
do
	export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
	export OMP_NUM_THREADS=6 && sim ${bz}
done
