#  Analysis of inkjet flow 
import os
import ansys.fluent.core as pyfluent
from ansys.fluent.core import UIMode

# %%
solver = pyfluent.launch_fluent(
    precision="double",
    processor_count=4,
    mode="solver",
   version="2d",
   ui_mode=UIMode.GUI,
)

# %%
solver.settings.file.read_case(file_name="inkjet.msh")

# %%
mesh = solver.settings.results.graphics.mesh
mesh.create("mesh-1")
mesh["mesh-1"].surfaces_list = ["axis", "inlet", "default-interior", "outlet", "wall_no_wet", "wall_wet"]
mesh["mesh-1"].options.edges = True
mesh["mesh-1"].display()

# %%

views = solver.settings.results.graphics.views
views.restore_view(view_name="front")

# Select x-axis for mirror planes
#views.mirror_planes="axis"
#views.mirror_planes()
#dir(views.mirror_planes)
#views.mirror_planes.create(axis='X')



# %%

solver.settings.mesh.scale(x_scale = 1e-06, y_scale = 1e-06)

# %%
solver.settings.setup.general.units.set_units(quantity = "length", units_name = "mm")

# %%
solver.settings.setup.general.units.set_units(quantity = "surface-tension", units_name = "dyne/cm")

# %%
solver.settings.setup.general.solver.time = "unsteady-1st-order"

# %%
solver.settings.setup.general.solver.two_dim_space = "axisymmetric"

# %%
solver.settings.setup.models.viscous.model = "laminar"

# %%
solver.settings.setup.models.multiphase.models = "vof"

# %%
solver.settings.setup.materials.database.copy_by_name(name = "water-liquid", type = "fluid")

# %%
phases = solver.settings.setup.models.multiphase.phases

#phases["phase-1"].set_state({"name": "air"})
#phases["phase-2"].set_state({"name": "water"})

phases["phase-1"].set_state({"material": "air"})
phases["phase-2"].set_state({"material": "water-liquid"})




# %%
# solver.settings.setup.models.multiphase.phases()

# %%
# solver.settings.setup.models.multiphase.phase_interaction.forces()

# %%
forces = solver.settings.setup.models.multiphase.phase_interaction.forces

forces.set_state({
    "surface_tension_model": True,
    "surface_tension_model_type": "Continuum Surface Force",
    "wall_adhesion": True
})

forces.surface_tension["air"]["water-liquid"].set_state({
    "option": "constant",
    "constant": 0.0735
})



# %%
solver.settings.setup.general.operating_conditions.reference_pressure_location = [0.1, 0.03]

# %%
mixture_velocity= solver.settings.setup.named_expressions.create("mixture")
mixture_velocity.definition = "IF(t<=10e-06[sec],3.58[m/s]*cos(PI*t/30e-6[s]),0[m/s])"
#mixture_velocity.output_parameter = False

# %%
solver.settings.setup.boundary_conditions.velocity_inlet['inlet'].phase['mixture'].momentum.velocity_magnitude.value = "mixture"

# %%
solver.settings.setup.boundary_conditions.velocity_inlet['inlet'].phase['water-liquid'].multiphase.volume_fraction.value = 1

# %%
solver.settings.setup.boundary_conditions.wall['wall_no_wet'].phase['mixture'].multiphase.contact_angles['water-liquid-air'].value = 3.05432575
solver.settings.setup.boundary_conditions.wall['wall_wet'].phase['mixture'].multiphase.contact_angles['water-liquid-air'].value = 1.5707961

# %%

solver.settings.solution.methods.p_v_coupling.flow_scheme = "PISO"

# %% [markdown]
# ##### enabling non iterarive time advancement

# %%

solver.settings.solution.methods.p_v_coupling.flow_scheme="Fractional Step"

# %%
# solver.settings.solution.methods.spatial_discretization.discretization_scheme()

# %%
solver.settings.solution.methods.spatial_discretization.set_state({
    "discretization_scheme": {
        "mom": "quick",
        "mp": "compressive"
    }
})


# %%
solver.settings.solution.initialization.hybrid_initialize()

# %%
# solver.settings.solution.cell_registers()



# %%
solver.settings.solution.cell_registers.create("region")

region = solver.settings.solution.cell_registers["region"]

updated_type = {
    "option": "hexahedron",
    "hexahedron": {
        "min_point": [0.0, 0.0, 0.0],    
        "max_point": [0.10, 0.03, 0.0]
    
    }
}

region.set_state({"type": updated_type})



# %%
# solver.settings.solution.initialization.patch.vof_smooth_options()

# %%
solver.settings.solution.initialization.patch.calculate_patch(cell_zones = [], domain = "water-liquid", registers = ["region"], value = 1, variable = "mp")

# %%
# solver.settings.solution.calculation_activity()

# %%
# Save case file
solver.settings.file.write(file_name="inkjet.cas.h5", file_type="case")

# %%
solver.settings.solution.run_calculation.transient_controls.time_step_size = 1e-8
solver.settings.solution.run_calculation.transient_controls.time_step_count = 3000

# %%
solver.settings.solution.run_calculation.calculate()

# %%
solver.settings.file.write_case_data(file_name = "inkjet-1-00600.dat.h5")


