Zenodo:                   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4384569.svg)](https://doi.org/10.5281/zenodo.4384569)

# Data Set

This repository contains both the experimental data and the simulation scripts
to reproduce the results of [2]: *Bloch point-mediated skyrmion annihilation in
three dimensions* by M. T. Birch, D. Cortés-Ortuño, N. D. Khanh, S.  Seki, A.
Štefančič, G. Balakrishnan, Y. Tokura and P. D. Hatton.

# Experimental data

Raw data from the figures of the paper, in the form of MPMS3 Data Files (`.dat`
files), are supplied in the `Experimental_Data` directory.

# Simulations

Simulations are based on the Fidimag [1] code and consist in two steps:

##  1. Find equilibrium states

These are found in `sims/equilibrium_states/` and use the main simulation
script `eq_state_relaxation.py`. Parameters are specfied in Bash files which
contain the range of field used to obtain the equilibrium states. Initial
profiles of the states are also found in the main Python script.

In the case of the skyrmion embedded in the helical phase, scripts to create
the initial configuration are found in
`sims/equilibrium_states/cubic_anisotropy/helix_sk_tube/sim.py` and in
`sim_hyst.py`. These scripts take the helical states (from a `npy` file) after
relaxation and create a skyrmion tube at the centre of the sample.

##  2. GNEBM simulations

After finding the equilibrium states, the magnetic configurations (stored in
`npy` files) are used to run the GNEBM to find the Minimum Energy Paths between
them. Simulations are based on the main Python script `sims/gnebm/gnebm.py`.

# Jupyter Notebooks

Notebooks where the energy of the configurations is analysed and where
visualisations of the configurations are shown, can be found in the `notebooks`
directory. Brief descriptions of the methods used in the Jupyter notebooks are
provided. The main methodology is to create a simulation object from Fidimag,
load `npy` files with the magnetic configurations and then analyze the data.
Visualisation of isosurfaces are performed using SciKit image [2] and plots of
the states are performed using Matplotlib [3]. Data analysis is also done via
Numpy arrays [4].


# Cite

If you find this material useful please cite us (you might need the LaTeX's
`url` package)

    @Misc{Birch2021,
      author       = {M. T. Birch and D. Cort\'es-Ortu\~no},
      title        = {{Data set for: Bloch point-mediated skyrmion annihilation in three dimensions}},
      howpublished = {Zenodo \url{doi:10.5281/zenodo.4384569}. Github: \url{https://github.com/davidcortesortuno/https://github.com/davidcortesortuno/paper-2021_bloch_point_mediated_skyrmion_annihilation_in_three_dimensions}},
      year         = {2021},
      doi          = {10.5281/zenodo.4384569},
      url          = {https://doi.org/10.5281/zenodo.4384569},
    }

# References

[1] Bisotti, M.-A., Cortés-Ortuño, D., Pepper, R., Wang, W., Beg, M., Kluyver,
T. and Fangohr, H., 2018. *Fidimag – A Finite Difference Atomistic and
Micromagnetic Simulation Package.* Journal of Open Research Software, 6(1),
p.22. DOI: http://doi.org/10.5334/jors.223

[2] Stéfan van der Walt, Johannes L. Schönberger, Juan Nunez-Iglesias, François
Boulogne, Joshua D. Warner, Neil Yager, Emmanuelle Gouillart, Tony Yu and the
scikit-image contributors. scikit-image: Image processing in Python. PeerJ
2:e453 (2014) https://doi.org/10.7717/peerj.453 

[3] J. D. Hunter, "Matplotlib: A 2D Graphics Environment", Computing in Science
& Engineering, vol. 9, no. 3, pp. 90-95, 2007.

[4] Harris, C.R., Millman, K.J., van der Walt, S.J. et al. Array programming
with NumPy. Nature 585, 357–362 (2020). DOI: 0.1038/s41586-020-2649-2.
