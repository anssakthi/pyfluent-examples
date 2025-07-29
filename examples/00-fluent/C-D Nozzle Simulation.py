#  C-D Nozzle Simulation 
# # Convergent-Divergent Nozzle

# %% [markdown]
#  **Objective**:
#    - Use PyFluent to set up the mesh, define boundary conditions, and solve the flow field.
#   - Simulate the flow through the nozzle to analyze velocity and pressure distributions.
# 

# %% [markdown]
# **Geometry specification**:
# 
# 
# ![image.png](attachment:image.png)

# %% [markdown]
# **Prerequisite**:
# ##### Before you can use the meshing workflow, you must set up the example and initialize this workflow.

# %% [markdown]
# ### Importing required Modules

# %%
import os
import ansys.fluent.core as pyfluent
from ansys.fluent.core import UIMode

# %% [markdown]
# ###  Launch Fluent session in Meshing Mode with user interface 

# %%
session = pyfluent.launch_fluent(
    mode="meshing",       
    ui_mode=UIMode.GUI,)

meshing = session.workflow

# %% [markdown]
# **Get input geometry path**:

# %%
input_file = os.path.join(os.getcwd(), 'nozzle.dsco')
#print(input_file)

# %% [markdown]
# **Initialize Meshing Workflow**:

# %%
meshing.InitializeWorkflow(WorkflowType="Watertight Geometry")
    
meshing.TaskObject["Import Geometry"].Arguments = {"FileName": input_file}
meshing.TaskObject["Import Geometry"].Execute()

# %%
meshing.TaskObject["Add Local Sizing"].Execute()

# %% [markdown]
# **Generating Surface Mesh**:
# 
# Setting Min Size = 2 mm and Max Size = 30 mm in surface meshing.
# 
# Capture critical geometry with enough detail (2 mm)
# 
# Avoid  fine mesh in simple areas (30 mm)
# 
# Improve simulation efficiency while maintaining accuracy where needed

# %%
surface_mesh = {
        "CFDSurfaceMeshControls": {
            "MaxSize": 30,
            "MinSize": 2,
            "SizeFunctions": "Curvature",
        }
    }
meshing.TaskObject["Generate the Surface Mesh"].Arguments.set_state(surface_mesh)
meshing.TaskObject["Generate the Surface Mesh"].Execute()

# %% [markdown]
# **Describing the geometry**:

# %%
geometry_describe = {
        "SetupType": "The geometry consists of only fluid regions with no voids",
        "WallToInternal": "No",
        "InvokeShareTopology": "No",
        "Multizone": "No",
    }
meshing.TaskObject["Describe Geometry"].Arguments.set_state(geometry_describe)
meshing.TaskObject["Describe Geometry"].Execute()

# %% [markdown]
# **Update Boundary Condition**: not working

# %%
boundary_condition = {
        "BoundaryLabelList": ["inlet"],
        "BoundaryLabelTypeList": ["pressure-inlet"],
        "OldBoundaryLabelList": ["inlet"],
        "OldBoundaryLabelTypeList": ["velocity-inlet"],
    }
meshing.TaskObject["Update Boundaries"].Arguments.set_state(boundary_condition)
meshing.TaskObject["Update Boundaries"].Execute()

# Update regions
meshing.TaskObject["Update Regions"].Execute()

# %% [markdown]
# **Add Boundary Layers**:
# 
# These are layers of  thin elements grown normal to the wall surfaces to better capture gradients near boundaries
# 
# Fluent will generate 8  layers starting at the wall and extending outward if we set number of layers=8
# 
# Set transition layer=0.35, each layer will be 35% thicker than the previous one

# %%
boundary_layer = {
        "NumberOfLayers": 8,
        "TransitionRatio": 0.35,
    }
meshing.TaskObject["Add Boundary Layers"].Arguments.update_dict(boundary_layer)
meshing.TaskObject["Add Boundary Layers"].Execute()


# %% [markdown]
# **Generate Volume Mesh**:
# 
# The volume mesh fills the interior of your flow domain with 3D elements.
# 

# %%
volume_mesh = {"VolumeFill": "poly-hexcore", "HexMaxSize": "20",}
mesh_preference={"Avoid1_8Transition": "yes"}
meshing.TaskObject["Generate the Volume Mesh"].Arguments.set_state(volume_mesh)
meshing.TaskObject["Generate the Volume Mesh"].Arguments.set_state(mesh_preference)
meshing.TaskObject["Generate the Volume Mesh"].Execute()

# %% [markdown]
# ![alt text](Assets/Mesh.png)
# ![alt text](Assets/mesh1.png)

# %% [markdown]
# **Switch to solver**:

# %%
solver = session.switch_to_solver()

# %% [markdown]
# **Display Mesh**:

# %%
mesh = solver.settings.results.graphics.mesh
mesh.create("mesh-1")
mesh["mesh-1"].surfaces_list = ["inlet", "outlet", "symmetry", "solid:1", "walls"]
mesh["mesh-1"].options.edges = True
mesh["mesh-1"].display()

# %%
# Set units not working
solver.settings.setup.general.units.set_units(quantity = "pressure", units_name = "atm")

# %% [markdown]
# **Solver Type**:
# 
# For a compressible converging-diverging nozzle, the density-based solver is used because it can accurately capture compressibility effects, shock waves, and high-speed flow behavior, which are essential characteristics of this kind of problem.

# %%
setup=solver.settings.setup
setup.general.solver.type = "density-based-implicit"
setup.models.energy.enabled = True
setup.materials.fluid["air"].density = {"option": "ideal-gas"}
setup.general.operating_conditions.operating_pressure = 0

# %% [markdown]
# **Defining Boundary Conditions**:
# 
# Gauge pressure=0.9  is the total pressure (stagnation pressure) of the incoming flow.
# It represents the pressure the flow would have if brought to rest isentropically (i.e., no losses).
# 
# Supersonic/Initial Gauge Pressure = 0.7369 is the estimated static pressure at the nozzle inlet
# 
# Turbulent Intensity = 1.5 defines the level of fluctuations in the incoming flow.
# 
# 

# %%
inlet = setup.boundary_conditions.pressure_inlet["inlet"]
inlet.momentum.gauge_total_pressure.value = 91192.5
inlet.momentum.supersonic_or_initial_gauge_pressure.value = 74666.3925
inlet.turbulence.turbulent_intensity = 0.015

outlet = setup.boundary_conditions.pressure_outlet["outlet"]
outlet.momentum.gauge_pressure.value = 74666.3925
outlet.turbulence.backflow_turbulent_intensity = 0.015

# %% [markdown]
# **Define Courant Number**:
# 
#  Courant number governs the numerical stability of simulations. It measures how far information travels in the domain during a single time step.
# 
#  Set the courant number to 25 to speed up convergence on a simple, steady compressible flow problem like a C-D nozzle

# %%
# Set solution controls
solver.settings.solution.controls.courant_number = 25

# %% [markdown]
# **Creating surface report defination**:
# 
# Creating a mass flow surface report at the outlet is essential for tracking, validating, and documenting how much mass is flowing out which is critical in simulations like a C-D nozzle, where compressibility and choking directly affect flow rate

# %%
# Configure mass flow rate report
reports = solver.settings.solution.report_definitions.surface
reports.create("mass-flow-rate")
reports["mass-flow-rate"] = {"report_type": "surface-massflowrate", "surface_names": ["outlet"]}
solver.settings.solution.monitor.report_files["mass-flow-rate-rfile"].file_name = r".\steady-mdot-rfile.out"

# %%
# Save case file
solver.settings.file.write(file_name="nozzle_sss.cas.h5", file_type="case")

# Initialize and run calculation
solver.settings.solution.initialization.hybrid_initialize()
solver.settings.solution.run_calculation.iter_count = 400

# %%
solver.settings.solution.run_calculation.calculate()

# %%
# Report fluxes
solver.settings.results.report.fluxes.mass_flow(write_to_file=False, zones=["outlet", "inlet"])

# %%
 # Create pressure contour
contours = solver.settings.results.graphics.contour
contours.create("pressure_contour")
contours["pressure_contour"].surfaces_list = ["symmetry"]
contours["pressure_contour"].range_options.compute()

    # Create velocity contour
contours.create("velocity_contour")
contours["velocity_contour"].field = "velocity-magnitude"
contours["velocity_contour"].surfaces_list = ["symmetry"]
contours["velocity_contour"].range_options.compute()


