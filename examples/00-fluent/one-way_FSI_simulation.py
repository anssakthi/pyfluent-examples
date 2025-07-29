# one-way FSI simulation
# ### One way Fluid-Structure Interaction
# Objective:
# 
# It focuses on simulating turbulent airflow through a cylindrical test chamber containing a steel probe, and analyzing the deformation of the probe due to aerodynamic forces. The deformation is assumed to be small enough that it does not infuence the fluid flow, allowing for a one-way coupling approach.
# 
# Problem Description:
# 
# The cylindrical test chamber is 20 cm long, with a diameter of 10 cm. Turbulent air enters the chamber at 100 m/s, flows around and through the steel probe, and exits through a pressure outlet.
# 
# ![problem schematic.png](<attachment:problem schematic.png>)
# 
# 

# %% [markdown]
# ### Import Modules

# %%
import ansys.fluent.core as pyfluent 
from ansys.fluent.core import UIMode

# %% [markdown]
# ###  Launch Fluent session in Solver Mode with user interface 

# %%
solver = pyfluent.launch_fluent(
    precision="double",
    mode="solver",
   ui_mode=UIMode.GUI,
)

# %% [markdown]
# #### Read the journal file:
# 
# This file is like a script thhat tells Fluent what to do step by step without needing to click/code .
# 1. It opens the mesh file, which contains the geometry and grid of the model.
# 2. It sets up and solves the fluid flow simulation,showing how air flows through the chamber.
# 3. This simulation will be used later as the starting point for the structural analysis(to calculate how the probe bends or deforms due to airflow)

# %%
File="d:/FSI/fluid_flow.jou" # Path to the journal file
solver.tui.file.read_journal(File) # Read the journal file

# %% [markdown]
# Enabling the structural model:
# 
# we are analyzing how a steel probe deforms due to fluid flow. Since the deformation is expected to be small, we use the Linear Elasticity Structural model without adding unnecessary complexity.

# %%
solver.settings.setup.models.structure.model = "linear-elasticity"

# %%
# Copy materials from the database and assign to solid zone
solver.settings.setup.materials.database.copy_by_name(type="solid", name="steel")
solver.settings.setup.cell_zone_conditions.solid["solid"] = {"general": {"material": "steel"}}

# %% [markdown]
# ### Defining the boundary conditions:
# 
# we need to tell Fluent how the probe is supported and how it is allowed to move. This is done using structural boundary condition
# 1. Fixed Support-> solid-top
# 2. Symmetry condition-> solid-symmetry and solid-symmetry:011
# 3. Fluid-Solid interface-> fsisurface-solid and fsisurface-solid-shadow
# 

# %%
wall = solver.settings.setup.boundary_conditions.wall

# Configure solid-symmetry boundary
wall["solid-symmetry"] = {
    "structure": {
        "z_disp_boundary_value": 0,
        "z_disp_boundary_condition": "Node Z-Displacement"
    }
}

# Configure solid-top boundary
wall["solid-top"].structure.x_disp_boundary_condition = "Node X-Displacement"
wall["solid-top"].structure.y_disp_boundary_condition = "Node Y-Displacement"
wall["solid-top"].structure.z_disp_boundary_condition = "Node Z-Displacement"

# Copy boundary conditions from solid-symmetry to solid-symmetry:011
solver.settings.setup.boundary_conditions.copy(from_="solid-symmetry", to=["solid-symmetry:011"], verbosity=True)

# Configure FSI surface
wall["fsisurface-solid"].structure.x_disp_boundary_condition = "Intrinsic FSI"
wall["fsisurface-solid"].structure.y_disp_boundary_condition = "Intrinsic FSI"
wall["fsisurface-solid"].structure.z_disp_boundary_condition = "Intrinsic FSI"


# %% [markdown]
# Enable the inclusion of operating pressure into the fluid-structure interaction force:
# 
#  Normally, Fluent uses guage pressure(i.e., pressure relative to the operating pressure) to compute those forces.
#  When you enable this settings(True), Fluent uses the absolute pressure in the FSI force calculation

# %%
solver.settings.setup.models.structure.expert.include_pop_in_fsi_force = True

# %% [markdown]
# ### Disable the flow and turbulence equations
# The fluid simulation has already been solved and converged in the first step (using the journal file).
# 
# We are now only interested in calculating the structural response (deformation) based on the already-computed fluid forces (like pressure).
# 
# Since the fluid flow won’t change, there is no need to re-solve the flow or turbulence equations.
# Disabling them:
# 1. Reduces computation time
# 2. Prevents Fluent from unnecessarily updating or changing the flow field
# 3. Focuses resources only on solving the structural equations

# %%
solver.settings.solution.controls.equations = {"flow" : False}
solver.settings.solution.controls.equations = {"kw" : False}

# %% [markdown]
# ### Run Solver

# %%
solver.settings.file.write_case(file_name = "probe_fsi_1way.cas.h5") # save the case file 
solver.settings.solution.run_calculation.iter_count = 2 # Since only structural calculations will be performed, you do not need a large number of iterations to reach convergence.
solver.settings.solution.run_calculation.calculate() # run the calculation


# %% [markdown]
# ### Post-Processing:
# 
# we are primarily interested in understanding how the solid (the steel probe) deforms due to the fluid forces. That’s why we plot only the Total Displacement contour on the solid zone and not on other surfaces.
# 
# As it directly shows the deformation of the steel probe caused by the fluid forces. This is the primary structural result of interest in a one-way FSI simulation, while the fluid zones remain undeformed."

# %%
contours = solver.settings.results.graphics.contour
contours.create("displacement_contour")
contours["displacement_contour"].field = "total-displacement"
contours["displacement_contour"].surfaces_list = ["fsisurface-solid"]
contours["displacement_contour"].range_options.compute()

# %% [markdown]
# ![x-y axis view.png](<attachment:x-y axis view.png>)
# 
# The total displacement contour of the solid probe clearly shows the deformation caused by fluid forces. As expected in a one-way FSI simulation, the deformation occurs only in the solid zone, while the fluid field remains unchanged. The results confirm that the structural response is consistent with the applied pressure distribution, and the deformation is within the small range assumed for linear elasticity.

# %%
solver.settings.file.write_case_data(file_name = "probe_fsi_1way") # save the case and data file after plotting the contour

# %%
solver.exit()  # Close the solver


