#!/bin/bash

sim () {
	# BZ=$1
    printf -v BZ "%06d" $1
	python ../../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --kc "-0.05" --bz ${BZ} \
		--sim_name "hx-sk-tube_to_hx_Bz${BZ}mT" \
		--add_image "../../../equilibrium_states/cubic_anisotropy/helix_sk_tube_WEAK-TOL/npys/sk_helix/m_sk_helix_Bz_${BZ}.npy" \
		--add_image "../../../equilibrium_states/cubic_anisotropy/npys/helix-y_kc-5e-2_L10/m_helix-y_kc-5e-2_L10_Bz_${BZ}.npy" \
		--add_interpolations 28 \
		--stopping_dydt "1e-5" --max_steps 400 --spring_constant 1 \
        --keep_sim_climbing_image 5e-6 \
		--save_m_every 500 \
        --integrator "sundials" \
        --interpolation_method "rotation"
}

for ((bz=40; bz<100; bz+=20))
do
	export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
	export OMP_NUM_THREADS=5 && sim ${bz}
done
