# Modeling evaporating liquid spray
import ansys.fluent.core as pyfluent
from ansys.fluent.core import UIMode

# %%
solver = pyfluent.launch_fluent(
    precision="double",
    mode="solver",
   ui_mode=UIMode.GUI,
)

# %%
solver.settings.file.read_case(file_name="sector.msh.h5")

# %%
solver.settings.results.graphics.mesh.create()
solver.settings.results.graphics.mesh['mesh-1'].surfaces_list = ["atomizer-wall"]
solver.settings.results.graphics.mesh['mesh-1'].surfaces_list = ["central_air"]
solver.settings.results.graphics.mesh['mesh-1'].surfaces_list = ["swirling_air"]
solver.settings.results.graphics.mesh['mesh-1'].options.edges = True
solver.settings.results.graphics.mesh["mesh-1"].display()

# %%
solver.settings.setup.models.energy.enabled = True

# %%
solver.settings.setup.models.species.model.option = "species-transport"
solver.settings.setup.models.species.model.material = "methyl-alcohol-air"

# %%
solver.settings.setup.materials.mixture['methyl-alcohol-air'].species.volumetric = ["n2", "o2", "ch3oh"]

# %%
solver.settings.setup.boundary_conditions.periodic['periodic-a'].periodic.rotationally_periodic = "Rotational"
solver.settings.setup.boundary_conditions.periodic['periodic-b'].periodic.rotationally_periodic = "Rotational"

# %%
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].momentum.mass_flow_rate.value = 9.166999999999999e-05
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].momentum.direction_specification = "Direction Vector"
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].momentum.flow_direction[0].value = 0
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].momentum.flow_direction[2].value = 1
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].turbulence.turbulence_specification = "Intensity and Hydraulic Diameter"
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].turbulence.turbulent_intensity = 0.1
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].turbulence.hydraulic_diameter = 0.0037
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].thermal.total_temperature.value = 293
solver.settings.setup.boundary_conditions.mass_flow_inlet['central_air'].species.species_mass_fraction['o2'].value = 0.23

# %%
solver.settings.setup.boundary_conditions.velocity_inlet['co-flow-air'].momentum.velocity_magnitude.value = 1
solver.settings.setup.boundary_conditions.velocity_inlet['co-flow-air'].turbulence.turbulence_specification = "Intensity and Hydraulic Diameter"
solver.settings.setup.boundary_conditions.velocity_inlet['co-flow-air'].turbulence.hydraulic_diameter = 0.0726
solver.settings.setup.boundary_conditions.velocity_inlet['co-flow-air'].thermal.temperature.value = 293
solver.settings.setup.boundary_conditions.velocity_inlet['co-flow-air'].species.species_mass_fraction['o2'].value = 0.23

# %%
solver.settings.setup.boundary_conditions.pressure_outlet['outlet'].momentum.backflow_dir_spec_method = "From Neighboring Cell"
solver.settings.setup.boundary_conditions.pressure_outlet['outlet'].turbulence.backflow_turbulent_viscosity_ratio = 5
solver.settings.setup.boundary_conditions.pressure_outlet['outlet'].thermal.backflow_total_temperature.value = 293
solver.settings.setup.boundary_conditions.pressure_outlet['outlet'].species.backflow_species_mass_fraction['o2'].value = 0.23

# %%
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].momentum.velocity_specification_method = "Magnitude and Direction"
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].momentum.velocity_magnitude.value = 19
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].momentum.coordinate_system = "Cylindrical (Radial, Tangential, Axial)"
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].momentum.flow_direction[0].value = 0
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].momentum.flow_direction[1].value = 0.7071
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].momentum.flow_direction[2].value = 0.7071
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].turbulence.turbulence_specification = "Intensity and Hydraulic Diameter"
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].turbulence.hydraulic_diameter = 0.0043
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].thermal.temperature.value = 293
solver.settings.setup.boundary_conditions.velocity_inlet['swirling_air'].species.species_mass_fraction['o2'].value = 0.23

# %%
solver.settings.setup.boundary_conditions.wall['outer-wall'].momentum.shear_condition = "Specified Shear"

# %%
solver.settings.solution.initialization.hybrid_initialize()

# %%
solver.settings.solution.run_calculation.iter_count = 150

# %%
solver.settings.solution.run_calculation.calculate()

# %%
solver.settings.file.write_case_data(file_name = "spray1")

# %%
olver.settings.results.surfaces.iso_surface.create()
solver.settings.results.surfaces.iso_surface.rename(new = "angle=15", old = "iso-surface-1")
solver.settings.results.surfaces.iso_surface['angle=15'].field = "angular-coordinate"
solver.settings.results.surfaces.iso_surface['angle=15'].iso_values = [0.26179935]

# %%
solver.settings.results.graphics.contour.create()
solver.settings.results.graphics.contour['contour-1'].field = "velocity-magnitude"
solver.settings.results.graphics.contour['contour-1'].surfaces_list = ["angle=15"]
solver.settings.results.graphics.contour.rename(new = "contour-vel", old = "contour-1")
solver.settings.results.graphics.contour['contour-vel'].colorings.banded = True
solver.settings.results.graphics.contour['contour-vel'].range_options.compute()

# %%
solver.settings.results.graphics.pathline.create()
solver.settings.results.graphics.pathline.rename(new = "pathlines-air", old = "pathlines-1")
solver.settings.results.graphics.pathline['pathlines-air'].option.skip = 5
solver.settings.results.graphics.pathline['pathlines-air'].release_from_surfaces = ["swirling_air"]
solver.settings.results.graphics.pathline['pathlines-air'].range_options.compute()

# %% [markdown]
# #### Creating a spray injection

# %%
solver.settings.setup.models.discrete_phase.general_settings.interaction.enabled = True

# %%
solver.settings.setup.models.discrete_phase.general_settings.contour_plotting = "mean"

# %%
solver.settings.setup.models.discrete_phase.general_settings.unsteady_tracking.enabled = True

# %%
solver.settings.setup.models.discrete_phase.general_settings.unsteady_tracking.dpm_time_step_size = 0.0001

# %%
solver.settings.setup.models.discrete_phase.general_settings.unsteady_tracking.number_of_time_steps = 10

# %%
solver.tui.define.models.dpm.options.vaporization_options('no', 'yes')

# %%
solver.settings.setup.models.discrete_phase.physical_models.secondary_breakup_enabled = True

# %%
solver.settings.setup.models.discrete_phase.numerics.source_term_settings.linearization.enabled = True

# %%
solver.settings.setup.materials.droplet_particle.create()
solver.settings.setup.materials.droplet_particle.rename(new = "methyl-alcohol-liquid", old = "droplet-particle-1")
solver.settings.setup.materials.droplet_particle['methyl-alcohol-liquid'].chemical_formula = "ch3oh<l>"
solver.settings.setup.materials.droplet_particle['methyl-alcohol-liquid'].viscosity.value = 0.00095

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].injection_type.option = "air-blast-atomizer"

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.location.number_of_streams = 600


# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].particle_type = "droplet"

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].material = "methyl-alcohol-liquid"

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].interaction.evaporating_species = 'ch3oh'


# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.location.z = 0.0015


# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.temperature = 263

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.mass_flow_rate.flow_rate = 8.500000000000001e-05

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.cone_settings.child_names

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.child_names

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.times.stop_time=100

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values()

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].initial_values.location.azimuthal_stop_angle = 0.5235987

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1']()

# %%
injection = solver.settings.setup.models.discrete_phase.injections['injection-1']

# Enable breakup
injection.physical_models.droplet_breakup.enabled = True




# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].physical_models.particle_drag.option = "dynamic-drag"

# %%
solver.settings.setup.models.discrete_phase.injections['injection-1'].physical_models.turbulent_dispersion.enabled = True
solver.settings.setup.models.discrete_phase.injections['injection-1'].physical_models.turbulent_dispersion.random_eddy_lifetime = True

# %%
solver.settings.solution.controls.pseudo_time_explicit_relaxation_factor.global_dt_pseudo_relax['dpm'] = 0.9

# %%
solver.settings.solution.monitor.residual.options.criterion_type = "none"

# %%
solver.settings.solution.report_definitions.surface.create()
solver.settings.solution.report_definitions.surface['report-def-0'] = {"report_type" : "surface-massavg"}
solver.settings.solution.report_definitions.surface.rename(new = "ch3oh_outlet", old = "report-def-0")
solver.settings.solution.report_definitions.surface['ch3oh_outlet'].field = "ch3oh"
solver.settings.solution.report_definitions.surface['ch3oh_outlet'].surface_names = ["outlet"]


solver.settings.solution.monitor.report_files.create()
solver.settings.solution.monitor.report_files.rename(new = "report-file-ch3oh", old = "report-file-1")
solver.settings.solution.monitor.report_files['report-file-ch3oh'].report_defs = ["ch3oh_outlet"]


solver.settings.solution.monitor.report_plots.create()
solver.settings.solution.monitor.report_plots.rename(new = "report-plot-ch3oh", old = "report-plot-1")
solver.settings.solution.monitor.report_plots['report-plot-ch3oh'].report_defs = ["ch3oh_outlet"]

# %%
solver.settings.solution.report_definitions.volume.create()
solver.settings.solution.report_definitions.volume['report-def-0'] = {"report_type" : "volume-sum"}
solver.settings.solution.report_definitions.volume.rename(new = "dpm-mass-source", old = "report-def-0")
solver.settings.solution.report_definitions.volume['dpm-mass-source'].field = "dpm-mass-source"
solver.settings.solution.report_definitions.volume['dpm-mass-source'].cell_zones = ["fluid"]


solver.settings.solution.monitor.report_files.create()
solver.settings.solution.monitor.report_files.rename(new = "report-file-dpm-mass-source", old = "report-file-1")
solver.settings.solution.monitor.report_files['report-file-dpm-mass-source'].report_defs = ["dpm-mass-source"]
solver.settings.solution.monitor.report_files['report-file-dpm-mass-source'].file_name = r".\\report-file-dpm-mass-source.out"


solver.settings.solution.monitor.report_plots.create()
solver.settings.solution.monitor.report_plots.rename(new = "report-plot-dpm-mass-source", old = "report-plot-1")
solver.settings.solution.monitor.report_plots['report-plot-dpm-mass-source'].report_defs = ["dpm-mass-source"]

# %%
solver.settings.solution.monitor.report_plots["report-plot-dpm-mass-source"].axes.y.number_format.format_type="exponential"

# %%
solver.settings.solution.monitor.report_plots["report-plot-dpm-mass-source"].axes.y.number_format.precision=2

# %%
solver.settings.solution.report_definitions.injection.create()
solver.settings.solution.report_definitions.injection['report-def-0'] = {"report_type" : "injection-domain-mass"}
solver.settings.solution.report_definitions.injection.rename(new = "dpm-mass-in-domain", old = "report-def-0")
solver.settings.solution.report_definitions.injection['dpm-mass-in-domain'].injection_list = ["injection-1"]
solver.settings.solution.report_definitions.injection['dpm-mass-in-domain'].show_unsteady_rate = False


solver.settings.solution.monitor.report_files.create()
solver.settings.solution.monitor.report_files.rename(new = "report-file-dpm-mass-in-domain", old = "report-file-1")
solver.settings.solution.monitor.report_files['report-file-dpm-mass-in-domain'].report_defs = ["dpm-mass-in-domain"]
solver.settings.solution.monitor.report_files['report-file-dpm-mass-in-domain'].file_name = r".\\report-file-dpm-mass-in-domain.out"


solver.settings.solution.monitor.report_plots.create()
solver.settings.solution.monitor.report_plots.rename(new = "report-plot-dpm-mass-in-domain", old = "report-plot-1")
solver.settings.solution.monitor.report_plots['report-plot-dpm-mass-in-domain'].report_defs = ["dpm-mass-in-domain"]

# %%
solver.settings.solution.monitor.report_plots["report-plot-dpm-mass-in-domain"].axes.y.number_format.format_type="exponential"
solver.settings.solution.monitor.report_plots["report-plot-dpm-mass-in-domain"].axes.y.number_format.precision=2

# %%
solver.settings.solution.report_definitions.injection.create()
solver.settings.solution.report_definitions.injection['report-def-0'] = {"report_type" : "injection-evaporated-mass"}
solver.settings.solution.report_definitions.injection.rename(new = "dpm-evaporated-mass", old = "report-def-0")
solver.settings.solution.report_definitions.injection['dpm-evaporated-mass'].injection_list = ["injection-1"]


solver.settings.solution.monitor.report_files.create()
solver.settings.solution.monitor.report_files.rename(new = "report-file-dpm-evaporated-mass", old = "report-file-1")
solver.settings.solution.monitor.report_files['report-file-dpm-evaporated-mass'].file_name = r".\\report-file-dpm-evaporated-mass.out"
solver.settings.solution.monitor.report_files['report-file-dpm-evaporated-mass'].report_defs = ["dpm-evaporated-mass"]


solver.settings.solution.monitor.report_plots.create()
solver.settings.solution.monitor.report_plots.rename(new = "report-plot-dpm-evaporated-mass", old = "report-plot-1")
solver.settings.solution.monitor.report_plots['report-plot-dpm-evaporated-mass'].report_defs = ["dpm-evaporated-mass"]

# %%
solver.settings.solution.monitor.report_plots["report-plot-dpm-evaporated-mass"].axes.y.number_format.format_type="exponential"
solver.settings.solution.monitor.report_plots["report-plot-dpm-evaporated-mass"].axes.y.number_format.precision=2

# %%
solver.settings.solution.run_calculation.iterate(iter_count = 300)

# %%
solver.settings.file.write(file_type = "case-data", file_name = "spray2.cas.h5")

# %%
solver.settings.results.graphics.particle_track.create()
solver.settings.results.graphics.particle_track.rename(new = "particle-tracks-droplets", old = "particle-tracks-1")
solver.settings.results.graphics.particle_track['particle-tracks-droplets'].field = "particle-diameter"
solver.settings.results.graphics.particle_track['particle-tracks-droplets'].injections_list = ["injection-1"]
solver.settings.results.graphics.particle_track['particle-tracks-droplets'].display()

# %%
solver.settings.results.graphics.contour.create()
solver.settings.results.graphics.contour.rename(new = "contour-dpm-temp", old = "contour-1")
solver.settings.results.graphics.contour['contour-dpm-temp'].field = "dpm-temp"
solver.settings.results.graphics.contour['contour-dpm-temp'].surfaces_list = ["angle=15"]
solver.settings.results.graphics.contour['contour-dpm-temp'].colorings.banded = True
solver.settings.results.graphics.contour['contour-dpm-temp'].range_options.auto_range = False
solver.settings.results.graphics.contour['contour-dpm-temp'].range_options.minimum = 260
solver.settings.results.graphics.contour['contour-dpm-temp'].range_options.maximum = 270.9771
solver.settings.results.graphics.particle_track['contour-dpm-temp'].display()


solver.settings.results.graphics.contour.create()
solver.settings.results.graphics.contour.rename(new = "contour-dpm-sauter-diameter", old = "contour-1")
solver.settings.results.graphics.contour['contour-dpm-sauter-diameter'].field = "dpm-d32"
solver.settings.results.graphics.contour['contour-dpm-sauter-diameter'].surfaces_list = ["angle=15"]
solver.settings.results.graphics.particle_track['contour-dpm-sauter-diameter'].display()

solver.settings.results.graphics.vector.create()
solver.settings.results.graphics.vector.rename(new = "vector-dpm-velocity", old = "vector-1")
solver.settings.results.graphics.vector['vector-dpm-velocity'].vector_field = "dpm-mean-velocity"
solver.settings.results.graphics.vector['vector-dpm-velocity'].field = "dpm-vel-mag"
solver.settings.results.graphics.vector['vector-dpm-velocity'].options.vector_style = "arrow"
solver.settings.results.graphics.vector['vector-dpm-velocity'].options.scale = 7
solver.settings.results.graphics.vector['vector-dpm-velocity'].surfaces_list = ["angle=15"]
solver.settings.results.graphics.particle_track['vector-dpm-velocity'].display()


