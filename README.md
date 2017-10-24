# Open-eObs
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5168b7d619c54feab1bdebc527ec1745)](https://www.codacy.com/app/BJSS/openeobs?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NeovaHealth/openeobs&amp;utm_campaign=Badge_Grade)

Open-eObs is an electronic observation, ward management and task management software
for Acute and Mental Health hospitals.

It provides the following observations that can be submitted via the mobile interface:
- Blood Glucose
- Blood Product
- Early Warning Score (EWS)
- Height
- Neurological
- Postural Blood Pressure
- Weight

It provides the following tools to assist with ward management:
- High level Ward Dashboard
- Interactive charts of observation data
- Patient Acuity Board
- Patient Record
- Patient Report
- Patient Visit Management (via `nh_eobs_adt_gui` module)
- Staff Allocation to Patients

It provides additional ward management tools for Mental Health settings:
- Patient Monitoring Exceptions (Patient off ward)
- Rapid Tranquilisation status flag

It provides the following tools to aid in the analysis of clinical activities:
- Overdue tasks list
- Ward staff Workload board (grouped by time left to complete task)
- EWS task OLAP view (via installation of `nh_eobs_analysis`)

## Installation
Open-eObs is a set of [Odoo](https://www.odoo.com/) modules that allow for electronic observations 
and builds on the [NHClinical](https://github.com/NeovaHealth/nhclinical) set of modules.

We currently develop against [our own tag of Odoo](https://github.com/bjss/odoo/tree/liveobs_1.11.1), this is to ensure consistency so it's recommended when
installing Odoo that you install this version.

Once you've downloaded Odoo, installed it's dependencies and installed PostgreSQL 9.3
you need to update the `server.cfg` file of your Odoo installation to point to 
the NhClinical and Open-eObs directories.

After restarting the server you can then log in as the admin user and install the
`nh_eobs_mobile` or `nh_eobs_mental_health` modules. These install the Acute and
Mental Health configurations of Open-eObs.

Additional modules such as `nh_eobs_adt_gui` and `nh_eobs_analysis` can also be
installed at this stage.

## Upgrading
To upgrade the Open-eObs modules you just need to update the Open-eObs modules and
press the upgrade module button for `nh_eobs_mobile` or `nh_eobs_mental_health` 
depending on what you have installed.

It's recommended you backup the existing database and module files before upgrading
so you can restore should anything go wrong.

## Contributing
We welcome contributions via the creation of issues (for feedback, bugs and suggestions)
and pull requests (for submitting code). 

You can read our contribution guidelines for more information on how to contribute
and what you can expect when contributing to Open-eObs

User guides can be found in [the Wiki](https://github.com/NeovaHealth/openeobs/wiki).
