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


# FIELD = 80
for FIELD in range(0, 181, 20):

    nx, ny, nz = 30, 30, 30
    dx, dy, dz = 1, 1, 1
    mesh = CuboidMesh(nx=nx, ny=ny, nz=nz,
                      dx=dx, dy=dy, dz=dz,
                      x0=-nx * 0.5, y0=-ny * 0.5, z0=-nz * 0.5,
                      unit_length=1.,
                      periodicity=(True, True, False)
                      )

    sim_name = 'sk_helix'
    sim = Sim(mesh, name=sim_name, integrator='sundials_openmp')

    sim.mu_s = 1
    sim.add(Exchange(1))
    sim.add(DMI(0.727, dmi_type='bulk'))
    bz_min = FIELD
    sim.add(Zeeman((0.0, 0.0, bz_min * 1e-3)), save_field=True)
    kc = -0.05
    if np.abs(kc) > 0.0:
        sim.add(CubicAnisotropy(kc))

    # .........................................................................

    sim.driver.alpha = 0.9
    sim.driver.do_precession = False

    # Zeeman_int = sim.get_interaction('Zeeman')
    # Zeeman_int.update_field((0.0, 0.0, B_sweep * 1e-3))

    H_BG = np.load(f'../npys/helix-y_kc-5e-2_L10/m_helix-y_kc-5e-2_L10_Bz_{FIELD:06d}.npy')
    sim.set_m(H_BG)

    # Embed skyrmion in the helical phase
    r = sim.mesh.coordinates
    rho = np.sqrt(r[:, 0] ** 2 + r[:, 1] ** 2)
    phi = np.arctan2(r[:, 1], r[:, 0])
    m = np.copy(sim.spin.reshape(-1, 3))
    # m[rho < 5] = [0, 0, -1.]

    sign = -1
    k = np.pi / 6
    # m[rho < 5][:, 0] = sign * np.sin(k * rho[rho < 5]) * np.cos(phi[rho < 5])
    # m[rho < 5][:, 1] = sign * np.sin(k * rho[rho < 5]) * np.sin(phi[rho < 5])
    # m[rho < 5][:, 2] = -np.cos(k * rho[rho < 5])

    ftr = rho < 6
    m[ftr] = np.column_stack((sign * np.sin(k * rho[ftr]) * np.cos(phi[ftr]),
                              sign * np.sin(k * rho[ftr]) * np.sin(phi[ftr]),
                              -np.cos(k * rho[ftr])))

    sim.set_m(m.reshape(-1))

    # .....................................................................

    # save_vtk(sim, sim_name + '_INITIAL', field_mT=FIELD)
    sim.relax(stopping_dmdt=3e-6, max_steps=5000,
              save_m_steps=None, save_vtk_steps=None)

    # .....................................................................

    save_vtk(sim, sim_name, field_mT=FIELD)

    if not os.path.exists('npys/{}'.format(sim_name)):
        os.makedirs('npys/{}'.format(sim_name))
    name = 'npys/{}/m_{}_Bz_{:06d}.npy'.format(sim.driver.name,
                                               sim_name,
                                               int(FIELD))
    np.save(name, sim.spin)
