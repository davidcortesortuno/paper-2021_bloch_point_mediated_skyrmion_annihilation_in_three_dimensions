# import fidimag
import click
import fidimag.common.constant as C
from fidimag.common import CuboidMesh
from fidimag.atomistic import Sim
from fidimag.atomistic import Exchange, DMI, Zeeman, CubicAnisotropy
import numpy as np
import os
import shutil


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


def one_dim_mod(r, Bz, D):

    COS_theta = Bz / (D ** 2)

    # conical
    if COS_theta <= 1.0:
        SIN_theta = np.sqrt(1 - COS_theta ** 2)
        psi = (2 * np.pi / 10.) * r[2]

        return (SIN_theta * np.cos(psi),
                SIN_theta * np.sin(psi),
                COS_theta
                )
    # fm
    else:
        return (0, 0.01, 0.99)


def helix_angle_x(r, angle_x=np.pi * 0.25, _lambda=10):

    k_mag = 2 * np.pi / _lambda
    k = np.array([np.sin(angle_x), 0, np.cos(angle_x)])
    # k1 = np.array([np.sin(angle_x), 0, np.cos(angle_x)])
    k2 = np.array([np.cos(angle_x), 0, -np.sin(angle_x)])
    k1 = np.cross(k, k2)

    theta = k_mag * np.dot(k, r)
    vec = np.sin(theta) * k1 + np.cos(theta) * k2

    return tuple(vec)


def sk_tube(r, Bz, D, sk_rad=3.):

    rho = r[0] ** 2 + r[1] ** 2
    if rho < sk_rad ** 2:
        return (0, 0, -1)

    return one_dim_mod(r, Bz, D)


def two_bobbers(r, Bz, D, Lz, bobber_rad=3., bobber_length=4.):

    rho = r[0] ** 2 + r[1] ** 2
    if rho < bobber_rad ** 2:
        if np.abs(r[2]) > (Lz * 0.5 - bobber_length):
            return (0, 0, -1)

    return one_dim_mod(r, Bz, D)


def two_bobbers_asymm(r, Bz, D, Lz, bobber_rad=3., bobber_length=5.):
    """
    TESTING
    """

    rho = r[0] ** 2 + r[1] ** 2
    if rho < bobber_rad ** 2:
        if (r[2] > (Lz * 0.5 - bobber_length)) or (r[2] < (Lz * 0.5 - (4 + bobber_length))):
            return (0, 0, -1)

    return one_dim_mod(r, Bz, D)


def one_bobber(r, Bz, D, Lz, bobber_rad=3., bobber_length=4.):

    rho = r[0] ** 2 + r[1] ** 2
    if rho < bobber_rad ** 2:
        if r[2] > (Lz * 0.5 - bobber_length):
            return (0, 0, -1)

    return one_dim_mod(r, Bz, D)


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
@click.option('--kc', type=float, default=0.0, help='Cubic anisotropy')
@click.option('--mu_s', type=float, default=1., help='Magnetic moment')
@click.option('--sim_name', type=str, default='NN', help='Simulation name')
@click.option('--bz_min', type=float, default=250, help='Min Bz field')
@click.option('--bz_max', type=float, default=340, help='Max Bz field')
@click.option('--bz_steps', type=int, default=91, help='N of field steps')
@click.option('--bz_hysteresis', is_flag=True)
@click.option('--initial_state_one_bobber', type=click.FLOAT, default=None,
              help='Bobber with length')
@click.option('--initial_state_two_bobbers', type=click.FLOAT, default=None,
              help='Two bobbers with length')
@click.option('--initial_state_two_bobbers_asymm', type=click.FLOAT, default=None,
              help='Two asymmetric bobbers with length separated by X lattice points')
@click.option('--initial_state_sk_tube', type=click.FLOAT, default=None,
              help='Skyrmion with radius')
@click.option('--initial_state_one_dim_mod', is_flag=True,
              help='1D modulation')
@click.option('--initial_state_helix_angle_x', default=[None, None],
              type=click.Tuple([float, float]),
              help='Helix with angle in the XZ plane: angle periodicity')
@click.option('--stopping_dmdt', type=float, default=1e-5,
              help='Min dm/dt LLG')
@click.option('--max_steps', type=int, default=4000, help='Max LLG steps')
@click.option('--save_initial_state', is_flag=True)
def simulation(nx, ny, nz,
               dx, dy, dz,
               j, d, kc,
               mu_s,
               sim_name,
               bz_min, bz_max, bz_steps, bz_hysteresis=False,
               initial_state_one_bobber=None,
               initial_state_two_bobbers=None,
               initial_state_two_bobbers_asymm=None,
               initial_state_sk_tube=None,
               initial_state_one_dim_mod=None,
               initial_state_helix_angle_x=(None, None),
               stopping_dmdt=1e-5,
               max_steps=4000,
               save_initial_state=None
               ):

    mesh = CuboidMesh(nx=nx, ny=ny, nz=nz,
                      dx=dx, dy=dy, dz=dz,
                      x0=-nx * 0.5, y0=-ny * 0.5, z0=-nz * 0.5,
                      unit_length=1.,
                      periodicity=(True, True, False)
                      )

    # J = 1.
    # D = 0.628  # L_D = 2 PI a J / D = 10 * a => D / J = 2 PI / 10.
    # Bz = 0.2   # B_z == (B_z mu_s / J)
    # mu_s = 1.

    sim = Sim(mesh, name=sim_name, integrator='sundials_openmp')

    sim.mu_s = mu_s
    sim.add(Exchange(j))
    sim.add(DMI(d, dmi_type='bulk'))
    sim.add(Zeeman((0.0, 0.0, bz_min * 1e-3)), save_field=True)
    if np.abs(kc) > 0.0:
        sim.add(CubicAnisotropy(kc))

    # .........................................................................

    sim.driver.alpha = 0.9
    sim.driver.do_precession = False

    if not os.path.exists('npys/{}'.format(sim_name)):
        os.makedirs('npys/{}'.format(sim_name))

    if not os.path.exists('txts'):
        os.makedirs('txts')

    for i, B_sweep in enumerate(np.linspace(bz_min, bz_max, bz_steps)):

        print('Bz = {:.0f} mT '.format(B_sweep).ljust(80, '-'))

        Zeeman_int = sim.get_interaction('Zeeman')
        Zeeman_int.update_field((0.0, 0.0, B_sweep * 1e-3))

        if (not bz_hysteresis) or (bz_hysteresis and i < 1):

            if initial_state_one_dim_mod:
                sim.set_m(lambda r: one_dim_mod(r, B_sweep * 1e-3, d))
            elif initial_state_helix_angle_x[0]:
                angle = initial_state_helix_angle_x[0] * np.pi / 180.
                periodic = initial_state_helix_angle_x[1]
                sim.set_m(lambda r: helix_angle_x(r, angle, periodic))
            elif initial_state_sk_tube:
                sk_rad = initial_state_sk_tube
                sim.set_m(lambda r: sk_tube(r, B_sweep * 1e-3, d, sk_rad=sk_rad))
            elif initial_state_two_bobbers:
                bobber_length = initial_state_two_bobbers
                sim.set_m(lambda r: two_bobbers(r, B_sweep * 1e-3, d,
                                                mesh.Lz,
                                                bobber_rad=3.,
                                                bobber_length=bobber_length))
            elif initial_state_two_bobbers_asymm:
                bobber_length = initial_state_two_bobbers_asymm
                sim.set_m(lambda r: two_bobbers_asymm(r, B_sweep * 1e-3, d,
                                                      mesh.Lz,
                                                      bobber_rad=3.,
                                                      bobber_length=bobber_length))
            elif initial_state_one_bobber:
                bobber_length = initial_state_one_bobber
                sim.set_m(lambda r: one_bobber(r, B_sweep * 1e-3, d,
                                               mesh.Lz,
                                               bobber_rad=3.,
                                               bobber_length=bobber_length))
            else:
                raise Exception('Not a valid initial state')

        if save_initial_state:
            save_vtk(sim, sim_name + '_INITIAL', field_mT=B_sweep)
            name = 'npys/{}/m_{}_INITIAL_Bz_{:06d}.npy'.format(sim.driver.name,
                                                               sim_name,
                                                               int(B_sweep))
            np.save(name, sim.spin)

        # .....................................................................

        sim.relax(stopping_dmdt=stopping_dmdt, max_steps=max_steps,
                  save_m_steps=None, save_vtk_steps=None)

        # .....................................................................

        save_vtk(sim, sim_name, field_mT=B_sweep)
        name = 'npys/{}/m_{}_Bz_{:06d}.npy'.format(sim.driver.name,
                                                   sim_name,
                                                   int(B_sweep))
        np.save(name, sim.spin)

        sim.driver.reset_integrator()

    shutil.move(sim_name + '.txt', 'txts/{}.txt'.format(sim_name))


# -----------------------------------------------------------------------------


if __name__ == '__main__':
    simulation()
