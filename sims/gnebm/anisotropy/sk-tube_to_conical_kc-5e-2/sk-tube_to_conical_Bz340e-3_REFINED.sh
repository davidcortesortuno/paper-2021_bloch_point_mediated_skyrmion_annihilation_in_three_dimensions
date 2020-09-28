#!/bin/bash

sim () {
	BZ=$1
	python ../../gnebm.py \
		--nx 30 --ny 30 --nz 30 \
		--j 1 --d "0.727" --mu_s 1 --kc "-0.05" --bz ${BZ} \
		--sim_name "sk-tube_to_conical_Bz${BZ}mT_REFINED" \
		--add_image "npys/sk-tube_to_conical_Bz340mT_CI_400/image_000000.npy" \
		--add_image "npys/sk-tube_to_conical_Bz340mT_CI_400/image_000006.npy" \
		--add_image "npys/sk-tube_to_conical_Bz340mT_CI_400/image_000008.npy" \
		--add_interpolations 14 \
		--add_interpolations 14 \
		--stopping_dydt "1e-5" --max_steps 25 --spring_constant 1 \
        --keep_sim_climbing_image_steps 80 \
        --keep_sim_climbing_image 2e-6 \
		--save_m_every 500 \
        --integrator "sundials" \
        --interpolation_method "rotation"
}

for ((bz=340; bz>339; bz-=20))
do
	export LC_ALL=en_GB.utf-8 && export LANG=en_GB.utf-8 && \
	export OMP_NUM_THREADS=6 && sim ${bz}
done
