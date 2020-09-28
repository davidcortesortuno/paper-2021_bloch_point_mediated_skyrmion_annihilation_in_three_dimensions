# import fidimag
import click
import fidimag.common.constant as C
from fidimag.common import CuboidMesh
from fidimag.atomistic import Sim
from fidimag.atomistic import Exchange, DMI, Zeeman, CubicAnisotropy
from fidimag.common.nebm_geodesic import NEBM_Geodesic
import numpy as np
import os
import shutil
import glob
import re


# -----------------------------------------------------------------------------

def save_vtk(sim, sim_name, field_mT):
    """
    """
    if not os.path.isdir('vtks/{}'.format(sim_name)):
        os.makedirs('vtks/{}'.format(sim_name))

    sim.driver.VTK.reset_data()
    # Here we save both Ms and spins as cell data
    sim.driver.VTK.save_scalar(sim._mu_s / C.mu_B, name='mu_s')
    sim.driver.VTK.save_vector(sim.spin.reshape(-1, 3), name='spins')
    # sim.driver.VTK.write_file(step=step)
    fname = "m_{}_Bz_{:06d}".format(sim_name, int(field_mT)) + ".vtk"
    sim.driver.VTK.vtk_data.tofile(os.path.join('vtks/{}'.format(sim_name),
                                                fname))


# -----------------------------------------------------------------------------

@click.command()
@click.option('--nx', type=int, default=30)
@click.option('--ny', type=int, default=30)
@click.option('--nz', type=int, default=30)
@click.option('--dx', type=float, default=1)
@click.option('--dy', type=float, default=1)
@click.option('--dz', type=float, default=1)
@click.option('--j', type=float, default=1.0, help='Exchange')
@click.option('--d', type=float, default=0.628, help='DMI')
@click.option('--kc', type=float, default=0.0, help='Cubic Anisotropy')
@click.option('--bz', type=float, default=0.1, help='Zeeman field in mT')
@click.option('--mu_s', type=float, default=1., help='Magnetic moment')
@click.option('--sim_name', type=str, default='NN', help='Simulation name')
@click.option('--add_image', multiple=True,
              help='Add one image to the elastic band')
@click.option('--add_interpolations', multiple=True, type=int,
              help='Add N interpolations between the first two images')
@click.option('--add_images_folder', type=str,
              help='Use a specific directory to find npy files for the band')
@click.option('--spring_constant', type=float, default=1e4,
              help='GNEBM spring constant')
@click.option('--stopping_dydt', type=float, default=1e-6,
              help='GNEBM stopping dY/dt')
@click.option('--max_steps', type=int, default=2000,
              help='GNEBM max number of steps')
@click.option('--keep_sim_climbing_image_steps', type=click.INT, default=None)
@click.option('--save_m_every', type=int, default=200,
              help='GNEBM Save magnetisation every X steps')
@click.option('--climbing_image', type=str,
              help='GNEBM Specify a climbing image for the band as an int'
                   'or as a path to an energy NDT file')
@click.option('--keep_sim_climbing_image', type=click.FLOAT, default=None,
              help='Continue sim after relaxation using the largest energy '
                   'image as climbing image')
@click.option('--keep_sim_climbing_image_again', type=click.FLOAT, default=None,
              help='Continue sim after relaxation using the local min energy '
                   'images as falling images')
@click.option('--integrator', type=str, default='sundials',
              help='sundials or verlet or rk4 or euler')
@click.option('--integrator_stepsize', type=float, default=1e-3,
              help='')
@click.option('--interpolation_method', type=str, default='rotation',
              help='linear or rotation')
@click.option('--variable_spring_forces', type=int,
              help='Variable spring forces')
@click.option('--interpolation_energy', type=str, default='polynomial',
              help='polynomial or Bernstein')
def simulation(nx, ny, nz,
               dx, dy, dz,
               j, d, kc, bz, mu_s,
               sim_name,
               add_image=None,
               add_interpolations=None,
               add_images_folder=None,
               spring_constant=None,
               stopping_dydt=None,
               max_steps=None,
               keep_sim_climbing_image_steps=None,
               save_m_every=None,
               climbing_image=None,
               keep_sim_climbing_image=None,
               keep_sim_climbing_image_again=None,
               integrator='sundials',
               integrator_stepsize=1e-3,
               interpolation_method='rotation',
               variable_spring_forces=None,
               interpolation_energy='polynomial'
               ):

    if add_interpolations:
        if (len(add_image) - 1) != len(add_interpolations):
            raise Exception('(N interpolations) != (N images - 1)')

    mesh = CuboidMesh(nx=nx, ny=ny, nz=nz,
                      dx=dx, dy=dy, dz=dz,
                      x0=-nx * 0.5, y0=-ny * 0.5, z0=-nz * 0.5,
                      unit_length=1.,
                      periodicity=(True, True, False)
                      )

    # Simulation
    sim = Sim(mesh, name=sim_name)
    sim.mu_s = mu_s
    sim.add(Exchange(j))
    sim.add(DMI(d, dmi_type='bulk'))
    sim.add(Zeeman((0.0, 0.0, bz * 1e-3)))
    if np.abs(kc) > 0.0:
        sim.add(CubicAnisotropy(kc))

    # GNEBM simulation ........................................................

    if add_interpolations:
        # Set the initial images from the list
        init_images = [np.load(image) for image in add_image]
        interpolations = [i for i in add_interpolations]
    elif add_images_folder:
        if add_images_folder.endswith('_LAST'):
            dir_list = glob.glob(add_images_folder[:-5] + '*')
            dir_list = sorted(dir_list,
               key=lambda f: int(re.search(r'(?<=_)[0-9]+$', f).group(0)))
            add_images_folder = dir_list[-1]

        flist = sorted(os.listdir(add_images_folder))
        init_images = [np.load(os.path.join(add_images_folder, image))
                       for image in flist]
        interpolations = []
    else:
        raise Exception('Specify an option to add images')

    if climbing_image:
        if climbing_image.isdigit():
            climbing_image = int(climbing_image)
        else:
            try:
                energies = np.loadtxt(climbing_image)[-1][1:]
                energies = energies - energies[0]
                climbing_image = np.where(energies == np.max(energies))[0][0]
            except OSError:
                raise Exception('Err trying to compute climb image from file')

        print('Using climbing image: {}'.format(climbing_image))

    # Start a NEB simulation passing the Simulation object and all the NEB
    # parameters
    neb = NEBM_Geodesic(sim,
                        init_images,
                        interpolations=interpolations,
                        spring_constant=spring_constant,
                        name=sim_name,
                        openmp=True,
                        climbing_image=climbing_image,
                        integrator=integrator,
                        interpolation_method=interpolation_method
                        )

    if integrator == 'verlet':
        neb.integrator.mass = 1
        neb.integrator.stepsize = integrator_stepsize
        dt = integrator_stepsize * 10
    else:
        dt = integrator_stepsize

    # .........................................................................

    for fdir in ['interpolations', 'ndts']:
        if not os.path.exists(fdir):
            os.makedirs(fdir)

    # Finally start the energy band relaxation
    neb.relax(max_iterations=max_steps,
              save_vtks_every=save_m_every,
              save_npys_every=save_m_every,
              stopping_dYdt=stopping_dydt,
              dt=dt
              )

    if variable_spring_forces:
        neb.variable_k = True
        neb.dk = spring_constant * 0.9

        neb.relax(max_iterations=max_steps,
                  save_vtks_every=save_m_every,
                  save_npys_every=save_m_every,
                  stopping_dYdt=stopping_dydt,
                  dt=dt,
                  save_initial_state=False
                  )

    # Continue with climbing image if specified
    if keep_sim_climbing_image:

        if not keep_sim_climbing_image_steps:
            keep_sim_climbing_image_steps = max_steps

        # Find all local maxima
        largest_E_im_idx = []
        for i in range(2, neb.n_images - 2):
            if (neb.energies[i] > neb.energies[i - 1] and
                    neb.energies[i - 1] > neb.energies[i - 2] and
                    neb.energies[i] > neb.energies[i + 1] and
                    neb.energies[i + 1] > neb.energies[i + 2]):

                largest_E_im_idx.append(i)
            elif (neb.energies[i] < neb.energies[i - 1] and
                  neb.energies[i - 1] < neb.energies[i - 2] and
                  neb.energies[i] < neb.energies[i + 1] and
                  neb.energies[i + 1] < neb.energies[i + 2]):

                largest_E_im_idx.append(-i)

        neb.climbing_image = largest_E_im_idx

        print('Continuing simulation with CI = {}'.format(largest_E_im_idx))

        neb.name += '_CI'
        # Data will be appended to the initial NDT file, at least we create a
        # new one with the CI appended to the sim name:
        # neb.create_tablewriter()
        # last_step_relax = neb.iterations

        # Variable dk for better resolution around saddle points
        # neb.variable_k = True
        # neb.dk = spring_constant

        neb.relax(max_iterations=keep_sim_climbing_image_steps,
                  save_vtks_every=save_m_every,
                  save_npys_every=save_m_every,
                  stopping_dYdt=keep_sim_climbing_image,
                  dt=dt,
                  save_initial_state=False
                  )

        # Remove initial state (same as final state from the prev relaxation)
        # shutil.rmtree('vtks/{}_{}'.format(neb.name, last_step_relax))

    # Continue with climbing image if specified
    if keep_sim_climbing_image_again:
        
        if not keep_sim_climbing_image_steps:
            keep_sim_climbing_image_steps = max_steps

        # Find all local maxima
        largest_E_im_idx = []
        for i in range(2, neb.n_images - 2):
            if (neb.energies[i] > neb.energies[i - 1] and
                    neb.energies[i - 1] > neb.energies[i - 2] and
                    neb.energies[i] > neb.energies[i + 1] and
                    neb.energies[i + 1] > neb.energies[i + 2]):

                largest_E_im_idx.append(i)
            elif (neb.energies[i] < neb.energies[i - 1] and
                  neb.energies[i - 1] < neb.energies[i - 2] and
                  neb.energies[i] < neb.energies[i + 1] and
                  neb.energies[i + 1] < neb.energies[i + 2]):

                largest_E_im_idx.append(-i)

        neb.climbing_image = largest_E_im_idx
        print('Continuing simulation with CI = {}'.format(largest_E_im_idx))
        neb.name += '_CI'
        neb.relax(max_iterations=keep_sim_climbing_image_steps,
                  save_vtks_every=save_m_every,
                  save_npys_every=save_m_every,
                  stopping_dYdt=keep_sim_climbing_image_again,
                  dt=dt,
                  save_initial_state=False
                  )

    # Produce a file with the data from a cubic interpolation for the band
    interp_data = np.zeros((200, 2))
    if interpolation_energy == 'polynomial':
        neb.compute_polynomial_factors()
        (interp_data[:, 0],
         interp_data[:, 1]) = neb.compute_polynomial_approximation_energy(200)
    elif interpolation_energy == 'Bernstein':
        neb.compute_Bernstein_polynomials()
        (interp_data[:, 0],
         interp_data[:, 1]) = neb.compute_Bernstein_approximation_energy(200)
    else:
        raise Exception('No valid interpolation method')

    np.savetxt('interpolations/{}_interpolation.dat'.format(sim_name),
               interp_data)

    # Clean files
    shutil.move(sim_name + '_energy.ndt',
                'ndts/{}_energy.ndt'.format(sim_name))
    shutil.move(sim_name + '_dYs.ndt',
                'ndts/{}_dYs.ndt'.format(sim_name))

# -----------------------------------------------------------------------------


if __name__ == '__main__':
    simulation()
