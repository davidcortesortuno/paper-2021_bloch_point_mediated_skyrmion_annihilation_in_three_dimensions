#!/bin/bash

sim () {
	# BZ=$1
    printf -v BZ "%06d" $1
	python ../../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --kc "-0.05" --bz ${BZ} \
		--sim_name "hx-sk-tube_to_hx_Bz${BZ}mT_REFINED" \
		--add_image "../../../equilibrium_states/cubic_anisotropy/helix_sk_tube/npys/sk_helix/m_sk_helix_Bz_${BZ}.npy" \
		--add_image "../../../equilibrium_states/cubic_anisotropy/npys/helix-y_kc-5e-2_L10/m_helix-y_kc-5e-2_L10_Bz_${BZ}.npy" \
		--add_interpolations 28 \
		--stopping_dydt "2e-6" --max_steps 1000 --spring_constant 1 \
        --keep_sim_climbing_image 1e-6 \
		--save_m_every 400 \
        --integrator "sundials" \
        --interpolation_method "rotation"
}

for ((bz=140; bz>139; bz-=20))
do
	export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
	export OMP_NUM_THREADS=5 && sim ${bz}
done
