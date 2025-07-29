# Battery_Cell Simulation 
# #### Simulating a Single Battery Cell Using the MSMD Battery Model
# 
# 

# %% [markdown]
# Objective:
# 
# The goal is to set up and run a battery simulation in PyFluent using a special battery model called the NTGK model.
# 
# Problem Description:
# 
# In this simulation, we will model the behavior of a 14.6 Ah lithium-ion battery that uses LiMn₂O₄ as the cathode and graphite as the anode. we will explore how the battery performs when it is discharged at different rates and under different operating conditions (normal use, pulse discharge, short circuit, etc.). The simulation will help you understand how the battery's voltage, temperature, and performance change during these conditions.
# 
# ![Model.png](attachment:Model.png)
# 
# 

# %% [markdown]
# #### Import modules

# %%
import os
import ansys.fluent.core as pyfluent
from ansys.fluent.core import UIMode

# %% [markdown]
# #### Launch Fluent session with solver mode and user interface

# %%
solver = pyfluent.launch_fluent(
    precision="double",
    processor_count=4,
    mode="solver",
   ui_mode=UIMode.GUI,
)

# %% [markdown]
# #### Load the mesh file and display it with specified surfaces

# %%
File="unit_battery.msh.h5" # Path to the mesh file
solver.settings.file.read_case(file_name=File)

surfaces =["internal-18", "internal-18:20", "tab_n", "tab_p", "wall_active", "wall_n", "wall_p"]  #List of surfaces to display
mesh = solver.settings.results.graphics.mesh
mesh.create("mesh-1")
mesh["mesh-1"].surfaces_list = surfaces
mesh["mesh-1"].options.edges = True
mesh["mesh-1"].display()

# %% [markdown]
# In this battery simulation, we want to see how the battery behaves over time for example, how the voltage, temperature, or state of charge changes as the battery discharges.

# %%
solver.settings.setup.general.solver.time = "unsteady-1st-order"

# %% [markdown]
# Enable the battery model:
# 
# By enabling the Battery Model, Fluent activates the physics and equations needed to simulate how the battery behaves electrically, chemically, and thermally.
# 
# Select NTGK/DCIR Model:
# 
# This is a simplified but accurate model (based on experimental data) for simulating how voltage and heat change during discharge.
# NTGK stands for Newman, Tiedemann, Gu, and Kim, who developed this model.
# 
# Set Nominal Cell Capacity (14.6 Ah):
# 
# Defines the total amount of charge the battery can store, based on the actual battery specs.
# 
# Enable Joule Heat in Passive Zones:
# 
# Includes heat generated in non-active parts like tabs and connectors. This makes the thermal results more accurate.
# 
# Specify C-Rate (1C):
# 
# Sets how fast the battery discharges. A 1C rate means the battery will fully discharge in 1 hour. Higher C-rates mean faster discharge.
# 
# Minimum Stop Voltage (3 V):
# 
# Fluent will stop the simulation if the battery voltage drops below this. It's a safety cutoff, just like in real batteries.
# 
# Assign Zones under Conductive Zones:
# 
# You're telling Fluent which parts are the active battery region (electrochemical zone) and which are conductive parts like tabs or connectors.
# 
# Assign External Connectors:
# 
# Defines where the current enters and leaves the battery. These are the positive and negative terminals.
# 
# Print Battery System Connection Info:
# 
# This checks if Fluent understood your setup and shows how everything is connected (like a wiring diagram).

# %%
battery = solver.settings.setup.models.battery
battery.enabled = True
battery.echem_model = "ntgk/dcir"
battery.zone_assignment.active_zone = ["e_zone"]
battery.zone_assignment.passive_zone = ["tab_nzone", "tab_pzone"]
battery.zone_assignment.negative_tab = ["tab_n"]
battery.zone_assignment.positive_tab = ["tab_p"]
battery.zone_assignment.print_battery_connection()

# %% [markdown]
# ![battery connection info.png](<attachment:battery connection info.png>)

# %% [markdown]
# #### Defining New Materials for Cell and Tabs
# 
# we are telling the fluent :
# 1. what materials the battery is made of 
# 2. How well each material conducts electricity
# 
# this helps fluent calculate voltage, current, and heat crrectly during the simulation

# %%
materials = [
    {
        "name": "e_material",
        "chemical_formula": "e",
        "density": 2092,
        "specific_heat": 678,
        "thermal_conductivity": 18.2,
        "uds_diffusivity": {"option": "defined-per-uds", "uds-0": 1190000, "uds-1": 983000}
    },
    {
        "name": "p_material",
        "chemical_formula": "pmat",
        "density": 8978,
        "specific_heat": 381,
        "thermal_conductivity": 387.6,
        "uds_diffusivity": {"option": "constant", "value": 10000000}
    },
    {
        "name": "n_material",
        "chemical_formula": "nmat",
        "density": 8978,
        "specific_heat": 381,
        "thermal_conductivity": 387.6
    }
]

solids = solver.settings.setup.materials.solid
for mat in materials:
    solids.create(mat["name"])
    solids[mat["name"]].chemical_formula = mat["chemical_formula"]
    solids[mat["name"]].density.value = mat["density"]
    solids[mat["name"]].specific_heat.value = mat["specific_heat"]
    solids[mat["name"]].thermal_conductivity.value = mat["thermal_conductivity"]
    if "uds_diffusivity" in mat:
        solids[mat["name"]].uds_diffusivity = {"option": mat["uds_diffusivity"]["option"]}
        if mat["uds_diffusivity"]["option"] == "defined-per-uds":
            solids[mat["name"]].uds_diffusivity.uds_diffusivities["uds-0"].value = mat["uds_diffusivity"]["uds-0"]
            solids[mat["name"]].uds_diffusivity.uds_diffusivities["uds-1"].value = mat["uds_diffusivity"]["uds-1"]
        else:
            solids[mat["name"]].uds_diffusivity.value = mat["uds_diffusivity"]["value"]

# %% [markdown]
# ### Defining the cell zone conditions
# Assign e_material to e_zone → This means the active part of the battery cell (where the reactions happen) is made of this material.
# 
# Assign p_material to tab_pzone → This means the positive tab is made of the positive terminal material.
# 
# Assign n_material to tab_nzone → This means the negative tab is made of the negative terminal material
# 

# %%
cell_zones = [
    ("e_zone", "e_material"),
    ("tab_nzone", "n_material"),
    ("tab_pzone", "p_material")
]

for zone, material in cell_zones:
    solver.settings.setup.cell_zone_conditions.solid[zone].general.material = material

# %% [markdown]
# #### Defining Boundary Conditions
# 
# We are telling Fluent how the battery loses heat to the environment through its walls, so it can simulate real world heating and cooling behavior accurately. 
# 
# Copying the same conditions to other surfaces ensures everything is consistent.

# %%
wall = solver.settings.setup.boundary_conditions.wall
wall["wall_active"].thermal.thermal_condition = "Convection"
wall["wall_active"].thermal.heat_transfer_coeff.value = 5

solver.settings.setup.boundary_conditions.copy(from_="wall_active", to=["wall_n", "wall_p"], verbosity=True)

# %% [markdown]
# #### Specifying solution settings
# 
# In this battery simulation, you're not modeling any moving fluid (like air or liquid) flowing through or around the battery. The battery cell is modeled as a solid object — not a fluid flow problem.
# So:
# 
# No flow = No need to solve equations for velocity or pressure.
# 
# No turbulence = No air or liquid movement that could become chaotic.
# 
# 

# %%
solver.settings.solution.controls.equations["flow"] = False
solver.settings.solution.controls.equations["kw"] = False
solver.settings.solution.monitor.residual.options.criterion_type = "none"

# %% [markdown]
# Creating Report Definations:
# 
# We are setting up reports and plots so Fluent can track and save important battery results like voltage and temperature, while the simulation runs. This helps you analyze how the battery performs over time
# 
# 

# %%
# Surface report for voltage
surface_reports = solver.settings.solution.report_definitions.surface
surface_reports.create("voltage_vp")
surface_reports["voltage_vp"] = {
    "report_type": "surface-areaavg",
    "field": "passive-zone-potential",
    "surface_names": ["tab_p"]
}

# Volume report for maximum temperature
volume_reports = solver.settings.solution.report_definitions.volume
volume_reports.create("max_temp")
volume_reports["max_temp"] = {
    "report_type": "volume-max",
    "field": "temperature",
    "cell_zones": ["e_zone", "tab_nzone", "tab_pzone"]
}

# Configure report files
report_files = solver.settings.solution.monitor.report_files

report_files.create("voltage_vp-rfile")
report_files["voltage_vp-rfile"].report_defs = ["flow-time", "voltage_vp"]
report_files["voltage_vp-rfile"].file_name =  "ntgk-1c.out"
report_files["voltage_vp-rfile"].print = True

report_files.create("max_temp")
report_files["max_temp"].report_defs = ["max_temp"]
report_files["max_temp"].file_name = "max-temp-1c.out"
report_files["max_temp"].print = True

# Configure report plots
report_plots = solver.settings.solution.monitor.report_plots

report_plots.create("voltage_vp")
report_plots["voltage_vp"].report_defs = ["voltage_vp"]
report_plots["voltage_vp"].print = True
report_plots["voltage_vp"].axes.x.number_format.precision = 0
report_plots["voltage_vp"].axes.y.number_format.precision = 2

report_plots.create("max_temp")
report_plots["max_temp"].report_defs = ["max_temp"]
report_plots["max_temp"].print = True
report_plots["max_temp"].axes.x.number_format.precision = 0
report_plots["max_temp"].axes.y.number_format.precision = 2


# %% [markdown]
# #### Obtaining Solution:

# %%
solver.settings.solution.initialization.standard_initialize()
solver.settings.solution.run_calculation.transient_controls.time_step_size = 30
solver.settings.solution.run_calculation.transient_controls.time_step_count = 100
solver.settings.solution.run_calculation.calculate()

# %% [markdown]
# ####  Post procressing setup:
# 
# Configure contours and vectors plot for visualization

# %%
contours = solver.settings.results.graphics.contour
contour_list = [
    {"name": "contour-phi+", "field": "cathode-potential", "surfaces": ["wall_active"]},
    {"name": "contour-phi-", "field": "anode-potential", "surfaces": ["wall_active"]},
    {"name": "contour-phi-passive", "field": "passive-zone-potential", "surfaces": ["tab_n", "tab_p", "wall_n", "wall_p"]},
    {"name": "contour-temp", "field": "temperature", "surfaces": ["wall_p", "wall_active", "tab_p", "tab_n", "wall_n"]}
]

for contour in contour_list:
    contours.create(contour["name"])
    contours[contour["name"]].field = contour["field"]
    contours[contour["name"]].surfaces_list = contour["surfaces"]
    contours[contour["name"]].range_options.compute()

vectors = solver.settings.results.graphics.vector
vectors.create("vector-current_density")
vectors["vector-current_density"].vector_field = "current-density-j"
vectors["vector-current_density"].field = "current-magnitude"
vectors["vector-current_density"].surfaces_list = ["wall_n", "wall_p", "wall_active", "tab_n", "tab_p"]
vectors["vector-current_density"].options.vector_style = "arrow"
vectors["vector-current_density"].range_options.compute()


# Save case file
solver.settings.file.write(file_name="unit_battery.cas.h5", file_type="case")

# %% [markdown]
# ![C=1, Temp_contour](images/C%3D1%2C%20Temp_contour.png)
# 
# ![Contour Plot of Phase Potential for Passive Zones (c=1)](images/Contour%20Plot%20of%20Phase%20Potential%20for%20Passive%20Zones%28c%3D1%29.png)
# 
# ![Phase potential for negative (c=1)](images/phase%20potential%20for%20negative%28c%3D1%29.png)
# 
# ![Phase potential for positive (c=1)](images/Phase%20potential%20for%20positive%28c%3D1%29.png)
# 
# ![Vector current density](images/vector%20current%20density.png)
# 

# %%
solver.settings.file.write_case_data(file_name = " ntgk") # Save case data for the C rate=1

# %% [markdown]
# ####  Repeat the simulation for different C-Rate and time steps:
# 
# Running the simulation at different C-Rates helps you understand how the battery performs under various load conditions like slow, normal, and fast discharge.
# 
# We run simulations at different discharge speeds, save results separately, and then plot all results together to compare how the battery behaves under different conditions,  which is essential for battery design and analysis.
# 
# 

# %%
solver.settings.setup.models.battery.eload_condition.eload_settings.crate_value = 0.5 # C-Rate=0.5

report_files["voltage_vp-rfile"].file_name =  "ntgk-0.5c.out"

report_files["max_temp"].file_name = "max-temp-0.5c.out"

solver.settings.solution.initialization.standard_initialize()
solver.settings.solution.run_calculation.transient_controls.time_step_count = 230

solver.settings.solution.run_calculation.calculate()

# %%
solver.settings.setup.models.battery.eload_condition.eload_settings.crate_value = 5 # C-Rate=5

report_files["voltage_vp-rfile"].file_name =  "ntgk-5c.out"

report_files['max_temp'].file_name = "max-temp-5c.out"

solver.settings.solution.initialization.standard_initialize()
solver.settings.solution.run_calculation.transient_controls.time_step_count = 23

solver.settings.solution.run_calculation.calculate()

# %% [markdown]
# #### Using the Reduced Order Method (ROM)

# %%
solver.settings.file.read_case(file_name = " unit_battery.cas.h5")

# %%
solver.settings.solution.initialization.standard_initialize()
solver.settings.solution.run_calculation.transient_controls.time_step_size = 30
solver.settings.solution.run_calculation.transient_controls.time_step_count = 3
solver.settings.solution.run_calculation.calculate()

# %%
solver.settings.setup.models.battery.solution_method = "msmd-rom"
solver.settings.setup.models.battery.solution_option.option_settings.number_substeps = 10
solver.settings.solution.run_calculation.transient_controls.time_step_size = 30
solver.settings.solution.run_calculation.transient_controls.time_step_count = 100
solver.settings.solution.run_calculation.calculate()

# %%
contours = solver.settings.results.graphics.contour
contour_list = [
    {"name": "contour-phi+", "field": "cathode-potential", "surfaces": ["wall_active"]},
    {"name": "contour-phi-", "field": "anode-potential", "surfaces": ["wall_active"]},
    {"name": "contour-phi-passive", "field": "passive-zone-potential", "surfaces": ["tab_n", "tab_p", "wall_n", "wall_p"]},
    {"name": "contour-temp", "field": "temperature", "surfaces": ["wall_p", "wall_active", "tab_p", "tab_n", "wall_n"]}
]

for contour in contour_list:
    contours.create(contour["name"])
    contours[contour["name"]].field = contour["field"]
    contours[contour["name"]].surfaces_list = contour["surfaces"]
    contours[contour["name"]].range_options.compute()

vectors = solver.settings.results.graphics.vector
vectors.create("vector-current_density")
vectors["vector-current_density"].vector_field = "current-density-j"
vectors["vector-current_density"].field = "current-magnitude"
vectors["vector-current_density"].surfaces_list = ["wall_n", "wall_p", "wall_active", "tab_n", "tab_p"]
vectors["vector-current_density"].options.vector_style = "arrow"
vectors["vector-current_density"].range_options.compute()

# %% [markdown]
# ![Current density (ROM)](images/Current%20density%20%28ROM%29.png)
# 

# %% [markdown]
# The solution of the simulation using the ROM is significantly faster than when using the direct method without any changes in results.

# %% [markdown]
# #### External and Internal Short-Circuit Treatment:
# 
# We are going to simulate a battery short-circuit, specifically a situation where both an external and internal short happen at the same time

# %%
solver.settings.file.read_case(file_name = " unit_battery.cas.h5") # Read the original case file again

# %%
# Configure battery model settings
solver.settings.setup.models.battery.eload_condition.eload_settings.set_state({
    "eload_type": "specified-resistance",
    "external_resistance": 0.5
})

# %%
# Create and configure cell register
solver.settings.solution.cell_registers.create(name="register_patch")
solver.settings.solution.cell_registers["register_patch"] = {
    "type": {
        "option": "hexahedron",
        "hexahedron": {
            "inside": True,
            "max_point": [0.01, 0.02, 1.0],
            "min_point": [-0.01, -0.01, -1.0]
        }
    }
}

# %%
# Initialize solution
solver.settings.solution.initialization.standard_initialize()

# Patch initialization
solver.settings.solution.initialization.patch.calculate_patch(
    domain="",
    cell_zones=[],
    registers=["register_patch"],
    variable="battery-short-resistance",
    reference_frame="Relative to Cell Zone",
    use_custom_field_function=False,
    custom_field_function_name="",
    value=5e-07
)


# %%
# Set up transient calculation parameters
solver.settings.solution.run_calculation.transient_controls.set_state({
    "time_step_size": 1,
    "time_step_count": 5
})

# Run the simulation
solver.settings.solution.run_calculation.calculate()

# %%
solver.settings.file.write(file_type = "case-data", file_name = "ntgk_short_circuit.cas.h5")

# %%
# Calculate surface integral
solver.settings.results.report.surface_integrals.area_weighted_avg(
    report_of="passive-zone-potential",
    surface_names=["tab_p"],
    write_to_file=False
)

# %% [markdown]
# Surface Integral
# 
# ![surface_integral.png](attachment:surface_integral.png)

# %%
# Calculate volume integral
solver.settings.results.report.volume_integrals.volume_integral(
    cell_function="total-current-source",
    cell_zones=["e_zone"],
    write_to_file=False
)

# %% [markdown]
# volume integral
# 
# ![volume_integral.png](attachment:volume_integral.png)

# %%
# Create and configure negative current vector plot
solver.settings.results.graphics.vector.create()
solver.settings.results.graphics.vector.rename(new="vector-current-", old="vector-1")
solver.settings.results.graphics.vector["vector-current-"].set_state({
    "vector_field": "current-density-jn",
    "field": "current-magnitude",
    "surfaces_list": ["wall_n", "wall_p", "wall_active"],
    "options": {"vector_style": "arrow"}
})
solver.settings.results.graphics.vector["vector-current-"].range_options.compute()

# %% [markdown]
# Vector Plots of Current at the Negative Current Collectors
# 
# ![Vector Plots of Current at the Negative Current Collectors.png](<attachment:Vector Plots of Current at the Negative Current Collectors.png>)

# %%
# Create and configure positive current vector plot
solver.settings.results.graphics.vector.create()
solver.settings.results.graphics.vector.rename(new="vector-current+", old="vector-1")
solver.settings.results.graphics.vector["vector-current+"].set_state({
    "vector_field": "current-density-jp",
    "field": "current-magnitude",
    "surfaces_list": ["wall_n", "wall_p", "wall_active"],
    "options": {"vector_style": "arrow"}
})
solver.settings.results.graphics.vector["vector-current+"].range_options.compute()

# %% [markdown]
# Vector Plots of Current at the Positive Current Collectors
# 
# ![Vector Plots of Current at the Positive Current Collectors.png](<attachment:Vector Plots of Current at the Positive Current Collectors.png>)

# %%
# Create and configure temperature contour plot
solver.settings.results.graphics.contour.create()
solver.settings.results.graphics.contour["contour-1"].set_state({
    "field": "temperature",
    "surfaces_list": ["wall_p", "wall_active", "tab_p", "tab_n", "wall_n"]
})
solver.settings.results.graphics.contour["contour-1"].range_options.compute()

# %% [markdown]
# ![static_temperature.png](attachment:static_temperature.png)

# %%
solver.exit()


