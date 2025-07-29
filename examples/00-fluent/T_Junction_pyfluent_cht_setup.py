# %%
# Import necessary libraries
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples, FluentVersion, FluentMode, UIMode

# %%
print(pyfluent.__version__)
pyfluent.logger.enable()

# %%
! set REMOTING_SERVER_ADDRESS="localhost"

# %%
# ! "%AWP_ROOT251%/fluent/ntbin/win64/fluent.exe" 3ddp -meshing -t4 -sifile="%TEMP%\server_info.txt"

# %%
# ! type "C:\\Users\\achitwar\\AppData\\Local\\Temp\\server_info.txt"

# %%
# Launch Fluent solver with specified settings
solver = pyfluent.launch_fluent(
    mode=FluentMode.SOLVER,
    product_version=FluentVersion.v251,
    precision="double",
    processor_count=4,
    ui_mode=UIMode.GUI,
    start_timeout=120,
)

# %%
solver.get_fluent_version()

# %%
mesh_file = r"D:\\Research\\1-way coupling example\\T_Junction.msh.h5"
solver.settings.file.read_mesh(file_name=mesh_file)

# %%
# Set the unit for temperature
solver.settings.setup.general.units.set_units(
    quantity="temperature", units_name="C"
)

# %%
# Enable energy model
solver.settings.setup.models.energy.enabled = True

# Set viscous model to k-epsilon
viscous_model = solver.settings.setup.models.viscous
viscous_model.model = "k-epsilon"
viscous_model.k_epsilon_model = "realizable"
viscous_model.k_epsilon_model = "standard"

# %%
# Define and assign fluid material properties
solver.settings.setup.materials.database.copy_by_name(type="fluid", name="water-liquid")
solver.settings.setup.cell_zone_conditions.fluid["fluid"].general.material = (
    "water-liquid"
)

# %%
# Define and assign solid material properties
solver.settings.setup.materials.database.copy_by_name(type="solid", name="steel")
solver.settings.setup.cell_zone_conditions.solid["solid-part_2"].general.material = (
    "steel"
)

# %%
# Setup inlet and outlet boundary conditions
main_inlet = solver.settings.setup.boundary_conditions.velocity_inlet["velocity_inlet_main"]

main_inlet.momentum.velocity_magnitude.value = 2
main_inlet.turbulence.turbulence_specification = "Intensity and Hydraulic Diameter"
main_inlet.turbulence.turbulent_intensity = 0.1
main_inlet.turbulence.hydraulic_diameter = "0.05 [m]"
main_inlet.thermal.temperature.value = 80  # 353.15 K

# %%
# Side inlet
side_inlet = solver.settings.setup.boundary_conditions.velocity_inlet["velocity_inlet_side"]
side_inlet.momentum.velocity_magnitude.value = 2
side_inlet.turbulence.turbulence_specification = "Intensity and Hydraulic Diameter"
side_inlet.turbulence.turbulent_intensity = 0.1
side_inlet.turbulence.hydraulic_diameter = "0.05 [m]"
side_inlet.thermal.temperature.value = 20  # 293.15 K

# %%
# Outlet boundary condition
outlet = solver.settings.setup.boundary_conditions.pressure_outlet["pressure_outlet"]
outlet.turbulence.turbulence_specification.allowed_values()
outlet.turbulence.turbulence_specification = "Intensity and Hydraulic Diameter"
outlet.turbulence.backflow_turbulent_intensity = 0.1
outlet.turbulence.backflow_hydraulic_diameter = "0.05 [m]"

# %%
# Wall boundary conditions
wall_convection = solver.settings.setup.boundary_conditions.wall['wall-solid-part_2']
wall_convection.thermal.thermal_condition.allowed_values()
wall_convection.thermal.thermal_condition = "Convection"
wall_convection.thermal.heat_transfer_coeff.value = 10
wall_convection.thermal.free_stream_temp.value = 15 # 288.15 K

# %%
# Wall hot end boundary condition
wall_temperature = solver.settings.setup.boundary_conditions.wall['wall_hot_end']
wall_temperature.thermal.thermal_condition.allowed_values()
wall_temperature.thermal.thermal_condition = "Temperature"
wall_temperature.thermal.temperature.value = 80  # 353.15 K

# %%
# Wall cold end boundary condition
wall_cold_end = solver.settings.setup.boundary_conditions.wall['wall_cold_end']
wall_cold_end.thermal.thermal_condition.allowed_values()
wall_cold_end.thermal.thermal_condition = "Temperature"
wall_cold_end.thermal.temperature.value = 20 # 293.15 K

# %%
# Mesh Interface
solver.settings.setup.mesh_interfaces.interface.create.argument_names

# %%
zone_list = solver.settings.setup.boundary_conditions.interface.get_object_names()
zone_list

# %%
# Create mesh interfaces
solver.settings.setup.mesh_interfaces.auto_create()

# %%
# Set spatial discretization scheme
solver.settings.solution.methods.spatial_discretization.discretization_scheme['pressure'] = "standard"

# Solver Settings initialization & set the iteration count
solver.settings.solution.initialization.hybrid_initialize()

# %%
# Initialize the solution and calculate
run_calculation = solver.settings.solution.run_calculation
run_calculation.iter_count = 200
run_calculation.calculate()

# %%
# Postprocessing
# Access the graphics object
graphics = solver.settings.results.graphics
# Set the hardcopy format for saving the image
graphics.picture.driver_options.hardcopy_format = "png"

# Set the view for contour display
contour_view = graphics.views.display_states.create("contour_view")
contour_view.front_faces_transparent = "disable"
contour_view.view_name = "back"

# Define the contour for wall temperature
wall_temperature_contour = solver.settings.results.graphics.contour.create(
    name="wall_temperature_contour"
)
wall_temperature_contour.field = "temperature"
wall_temperature_contour.surfaces_list = [zone for zone in zone_list if "solid" in zone]
wall_temperature_contour.display_state_name = contour_view.name()
wall_temperature_contour.display()

graphics.views.auto_scale()
graphics.picture.save_picture(file_name="T_Junction_wall_temperature_contour.png")

# %%
# Save the case and data files
solver.settings.file.write(
    file_type="case-data", file_name="T_Junction.cas.h5"
)

# %%
solver.exit()