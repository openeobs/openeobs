__author__ = 'colin'
from openerp.addons.mobile_frontend.controllers import urls

# URL structure
URL_PREFIX = '/mobile/'
URLS = urls.URLS

# patient list HTML
# 0 - url
# 1 - deadline time
# 2 - full name
# 3 - ews score
# 4 - trend icon (class)
# 5 - location (bed)
# 6 - parent location (ward)
PATIENT_LIST_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
              <div class="header-main block">
                    <img class="logo" src="/mobile/src/img/logo.png"/>
                    <ul class="header-meta">
                        <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                    </ul>
              </div>
              <ul class="header-menu two-col">
                   <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                   <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
              </ul>
        </div>
        <div class="content">
            <ul class="tasklist">
                {0}
            </ul>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

PATIENT_LIST_ITEM = """
<li>
    <a class="level-one block" href="{0}">
        <div class="task-meta">
            <div class="task-right">
                <p class="aside">{1}</p>
            </div>
            <div class="task-left">
                <strong>{2}</strong> ({3} <i class="{4}"></i>)<br/>
                <em>{5},{6}</em>
            </div>
        </div>
        <div class="task-meta">
            <p class="taskInfo">
            <br/>
            </p>
        </div>
    </a>
</li>
"""


# task list HTML
# 0 - url
# 1 - deadline time
# 2 - full name
# 3 - ews score
# 4 - trend icon (class)
# 5 - location (bed)
# 6 - parent location (ward)
# 7 - task name
TASK_LIST_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
              <div class="header-main block">
                    <img class="logo" src="/mobile/src/img/logo.png"/>
                    <ul class="header-meta">
                        <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                    </ul>
              </div>
              <ul class="header-menu two-col">
                   <li><a id="taskNavItem" href="/mobile/tasks/" class="selected">Tasks</a></li>
                   <li><a id="patientNavItem" href="/mobile/patients/">My Patients</a></li>
              </ul>
        </div>
        <div class="content">
            <ul class="tasklist">
                {task_list}
            </ul>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

TASK_LIST_ITEM = """
<li>
    <a class="level-one block" href="{0}">
        <div class="task-meta">
            <div class="task-right">
                <p class="aside">{1}</p>
            </div>
            <div class="task-left">
                {2}<strong>{3}</strong> ({4} <i class="{5}"></i>)<br/>
                <em>{6},{7}</em>
            </div>
        </div>
        <div class="task-meta">
            <p class="taskInfo">{8}<br/></p>
        </div>
    </a>
</li>
"""

# NEWS Observation template
# 0 - Patient URL
# 1 - Patient Name
# 2 - Task ID
# 3 - Timestamp for the observation
NEWS_OBS = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/" class="selected">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="{patient_url}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form task-id="{task_id}" patient-id="{patient_id}" data-type="ews" action="/mobile/task/submit/{task_id}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsField" id="parent_respiration_rate">
                        <div class="input-header">
                            <label for="respiration_rate">Respiration Rate</label>
                            <input step="1" name="respiration_rate" max="59" min="1" type="number" id="respiration_rate"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_indirect_oxymetry_spo2">
                        <div class="input-header">
                            <label for="indirect_oxymetry_spo2">O2 Saturation</label>
                            <input step="1" name="indirect_oxymetry_spo2" max="100" min="51" type="number" id="indirect_oxymetry_spo2"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_body_temperature">
                        <div class="input-header">
                            <label for="body_temperature">Body Temperature</label>
                            <input step="0.1" name="body_temperature" max="44.9" min="27.1" type="number" id="body_temperature"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_blood_pressure_systolic">
                        <div class="input-header">
                            <label for="blood_pressure_systolic">Blood Pressure Systolic</label>
                            <input step="1" name="blood_pressure_systolic" max="300" min="1" type="number" id="blood_pressure_systolic"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_blood_pressure_diastolic">
                        <div class="input-header">
                            <label for="blood_pressure_diastolic">Blood Pressure Diastolic</label>
                            <input step="1" name="blood_pressure_diastolic" max="280" min="1" type="number" id="blood_pressure_diastolic"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_pulse_rate">
                        <div class="input-header">
                            <label for="pulse_rate">Pulse Rate</label>
                            <input step="1" name="pulse_rate" max="250" min="1" type="number" id="pulse_rate"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_avpu_text">
                        <div class="input-header">
                            <label for="avpu_text">AVPU</label>
                        </div>
                       <div class="input-body">
                           <select name="avpu_text" id="avpu_text">
                                <option value="">Please Select</option>
                                <option value="A">Alert</option>
                                <option value="V">Voice</option>
                                <option value="P">Pain</option>
                                <option value="U">Unresponsive</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_oxygen_administration_flag">
                        <div class="input-header">
                            <label for="oxygen_administration_flag">Patient on supplemental O2</label>
                        </div>
                       <div class="input-body">
                           <select name="oxygen_administration_flag" id="oxygen_administration_flag">
                                <option value="">Please Select</option>
                                <option value="False">No</option>
                                <option value="True">Yes</option>
                           </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField valHide" id="parent_device_id">
                        <div class="input-header">
                            <label for="device_id">O2 Device</label>
                        </div>
                        <div class="input-body">
                            <select name="device_id" class="exclude" id="device_id">
                                {device_options}
                            </select>
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_flow_rate">
                        <div class="input-header">
                            <label for="flow_rate">Flow Rate</label>
                            <input class="exclude" step="0.1" name="flow_rate" max="100.0"  type="number" id="flow_rate"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_concentration">
                        <div class="input-header">
                            <label for="concentration">Concentration</label>
                            <input class="exclude" step="1" name="concentration" max="100"  type="number" id="concentration"/>

                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_cpap_peep">
                        <div class="input-header">
                            <label for="cpap_peep">CPAP: PEEP (cmH2O)</label>
                            <input class="exclude" step="1" name="cpap_peep" max="1000"  type="number" id="cpap_peep"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_niv_backup">
                        <div class="input-header">
                            <label for="niv_backup">NIV: Back-up rate (br/min)</label>
                            <input class="exclude" step="1" name="niv_backup" max="100"  type="number" id="niv_backup"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_niv_ipap">
                        <div class="input-header">
                            <label for="niv_ipap">NIV: IPAP (cmH2O)</label>
                            <input class="exclude" step="1" name="niv_ipap" max="100"  type="number" id="niv_ipap"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_niv_epap">
                        <div class="input-header">
                            <label for="niv_epap">NIV: EPAP (cmH2O)</label>
                            <input class="exclude" step="1" name="niv_epap" max="100"  type="number" id="niv_epap"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{task_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

DEVICE_OPTION = """<option value="{device_id}">{device_name}</option>"""

OBS_FREQ_OPTION = """<option value="{freq_time}">{freq_name}</option>"""

OBS_FREQ_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/" class="selected">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="obsChange block" task-id="{task_id}" patient-id="{patient_id}" data-type="frequency" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <h3>Confirm action taken?</h3>
                <p>Press the button below to confirm that you can completed the task Review Frequency</p>
                <div>
                    <div class="block obsSelectField" id="parent_frequency">
                        <div class="input-header">
                            <label for="frequency">Observation frequency</label>
                        </div>
                        <div class="input-body">
                            <select name="frequency"  id="frequency">
                                {frequency_options}
                            </select>
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{task_id}" type="hidden" name="taskId"/>
                <input value="0" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <p class="obsSubmit">
                    <a id="obsFreqSubmit" class="button submitButton" href="{task_url}">Confirm action</a>
                </p>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

ASSESS_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/" class="selected">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" task-id="{task_id}" patient-id="{patient_id}" data-type="assessment" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <h3>Confirm action taken?</h3>
                <p>Press the button below to confirm that you can completed the task Assess Patient</p>
                <input value="{task_id}" type="hidden" name="taskId"/>
                <input value="0" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <p class="obsSubmit">
                    <a id="confirmSubmit" class="button submitButton" href="{task_url}">Confirm action</a>
                </p>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

MEDICAL_TEAM_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/" class="selected">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" task-id="{task_id}" patient-id="{patient_id}" data-type="medical_team" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <h3>Confirm action taken?</h3>
                <p>Press the button below to confirm that you can completed the task {task_name}</p>
                <input value="{task_id}" type="hidden" name="taskId"/>
                <input value="0" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <p class="obsSubmit">
                    <a id="confirmSubmit" class="button submitButton" href="{task_url}">Confirm action</a>
                </p>
                <p class="obsConfirm">
                    <a class="button cancelButton" href="{cancel_url}" id="cancelSubmit">Cancel action</a>
                </p>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""


GCS_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="gcs" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsSelectField" id="parent_eyes">
                        <div class="input-header">
                            <label for="eyes">Eye response</label>
                        </div>
                       <div class="input-body">
                            <select name="eyes" id="eyes">
                                <option value="">Please select</option>
                                <option value="4">Spontaneous</option>
                                <option value="3">Speech</option>
                                <option value="2">Pain</option>
                                <option value="1">None</option>
                                <option value="C">Swelling</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_verbal">
                        <div class="input-header">
                            <label for="verbal">Verbal response</label>
                        </div>
                       <div class="input-body">
                            <select name="eyes" id="verbal">
                                <option value="">Please select</option>
                                <option value="5">Orientated</option>
                                <option value="4">Confused</option>
                                <option value="3">Inappropriate words</option>
                                <option value="2">Incomprehensible sounds</option>
                                <option value="1">None</option>
                                <option value="T">Intubated</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_motor">
                        <div class="input-header">
                            <label for="motor">Motor response</label>
                        </div>
                       <div class="input-body">
                            <select name="eyes" id="motor">
                                <option value="">Please select</option>
                                <option value="6">Obeys commands</option>
                                <option value="5">Localises to pain</option>
                                <option value="4">Reflexion to pain</option>
                                <option value="3">Abnormal reflexion</option>
                                <option value="2">Extension to pain</option>
                                <option value="1">None</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

BLOOD_PRODUCT_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="blood_product" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsField" id="parent_vol">
                        <div class="input-header">
                            <label for="vol">Vol (ml)</label>
                            <input step="0.1" name="vol" max="10000.0" min="0.1" type="number" id="vol"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_product">
                        <div class="input-header">
                            <label for="product">Blood Product</label>
                        </div>
                       <div class="input-body">
                            <select name="eyes" id="product">
                                <option value="">Please select</option>
                                <option value="rbc">RBC</option>
                                <option value="ffp">FFP</option>
                                <option value="platelets">Platelets</option>
                                <option value="has">Human Albumin Sol</option>
                                <option value="dli">DLI</option>
                                <option value="stem">Stem Cells</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""


BLOOD_SUGAR_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="blood_sugar" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsField" id="parent_blood_sugar">
                        <div class="input-header">
                            <label for="blood_sugar">Blood Sugar (mmol/L)</label>
                            <input step="0.1" name="blood_sugar" max="99.9" min="1.0" type="number" id="blood_sugar"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

HEIGHT_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="height" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsField" id="parent_height">
                        <div class="input-header">
                            <label for="height">Height</label>
                            <input step="0.1" name="height" max="3.0" min="0.1" type="number" id="height"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

WEIGHT_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="weight" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsField" id="parent_weight">
                        <div class="input-header">
                            <label for="weight">Weight</label>
                            <input step="0.1" name="weight" max="999.9" min="1.0" type="number" id="weight"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

PBP_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="pbp" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <h3 class="block">Lying/Sitting Blood Pressure</h3>
                <div>
                    <div class="block obsField" id="parent_systolic_sitting">
                        <div class="input-header">
                            <label for="systolic_sitting">Sitting Blood Pressure Systolic</label>
                            <input step="1" name="systolic_sitting" max="300" min="1" type="number" id="systolic_sitting"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_diastolic_sitting">
                        <div class="input-header">
                            <label for="diastolic_sitting">Sitting Blood Pressure Diastolic</label>
                            <input step="1" name="diastolic_sitting" max="280" min="1" type="number" id="diastolic_sitting"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <h3 class="block valHide" id="standing_title">Standing Blood Pressure</h3>
                <div>
                    <div class="block obsField valHide" id="parent_systolic_standing">
                        <div class="input-header">
                            <label for="systolic_standing">Standing Blood Pressure Systolic</label>
                            <input step="1" name="systolic_standing" max="300" min="1" type="number" id="systolic_standing" class="exclude"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_diastolic_standing">
                        <div class="input-header">
                            <label for="diastolic_standing">Standing Blood Pressure Diastolic</label>
                            <input step="1" name="diastolic_standing" max="280" min="1" type="number" id="diastolic_standing" class="exclude"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""


STOOLS_PATIENT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="stools" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsSelectField" id="parent_bowel_open">
                        <div class="input-header">
                            <label for="bowel_open">Bowel Open</label>
                        </div>
                       <div class="input-body">
                            <select name="bowel_open" id="bowel_open">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_nausea">
                        <div class="input-header">
                            <label for="nausea">Nausea</label>
                        </div>
                       <div class="input-body">
                            <select name="nausea" id="nausea">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_vomiting">
                        <div class="input-header">
                            <label for="vomiting">Vomiting</label>
                        </div>
                       <div class="input-body">
                            <select name="vomiting" id="vomiting">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_quantity">
                        <div class="input-header">
                            <label for="quantity">Quantity</label>
                        </div>
                       <div class="input-body">
                            <select name="quantity" id="quantity">
                                <option value="">Please select</option>
                                <option value="large">Large</option>
                                <option value="medium">Medium</option>
                                <option value="small">Small</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_colour">
                        <div class="input-header">
                            <label for="colour">Colour</label>
                        </div>
                       <div class="input-body">
                            <select name="colour" id="colour">
                                <option value="">Please select</option>
                                <option value="brown">Brown</option>
                                <option value="yellow">Yellow</option>
                                <option value="black">Black/Tarry</option>
                                <option value="red">Red (fresh blood)</option>
                                <option value="clay">Clay</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_bristol_type">
                        <div class="input-header">
                            <label for="bristol_type">Bristol Type</label>
                        </div>
                       <div class="input-body">
                            <select name="bristol_type" id="bristol_type">
                                <option value="" >Please select</option>
                                <option value="1">Type 1</option>
                                <option value="2">Type 2</option>
                                <option value="3">Type 3</option>
                                <option value="4">Type 4</option>
                                <option value="5">Type 5</option>
                                <option value="6">Type 6</option>
                                <option value="7">Type 7</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_offensive">
                        <div class="input-header">
                            <label for="offensive">Offensive</label>
                        </div>
                       <div class="input-body">
                            <select name="offensive" id="offensive">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_strain">
                        <div class="input-header">
                            <label for="strain">Strain</label>
                        </div>
                       <div class="input-body">
                            <select name="strain" id="strain">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_laxatives">
                        <div class="input-header">
                            <label for="laxatives">Laxatives</label>
                        </div>
                       <div class="input-body">
                            <select name="laxatives" id="laxatives">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_samples">
                        <div class="input-header">
                            <label for="samples">Lab Samples</label>
                        </div>
                       <div class="input-body">
                            <select name="samples" id="samples">
                                <option value="">Please select</option>
                                <option value="none">None</option>
                                <option value="micro">Micro</option>
                                <option value="virol">Virol</option>
                                <option value="m+v">M+V</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_rectal_exam">
                        <div class="input-header">
                            <label for="rectal_exam">Rectal Exam</label>
                        </div>
                       <div class="input-body">
                            <select name="rectal_exam" id="rectal_exam">
                                <option value="">Please select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <input value="{patient_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""

NEWS_PATIENT_HTML = """
<!DOCTYPE html>
<html>
   <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
            <div class="header-main block">
                <img class="logo" src="/mobile/src/img/logo.png"/>
                <ul class="header-meta">
                    <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                </ul>
            </div>
            <ul class="header-menu two-col">
                <li><a id="taskNavItem" href="/mobile/tasks/">Tasks</a></li>
                <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
            </ul>
        </div>
        <div class="content">
            <h2 id="patientName" class="block">
                <a href="/mobile/patient/{patient_id}">{patient_name}<i class="icon-info"></i></a>
            </h2>
            <form class="block" patient-id="{patient_id}" data-type="ews" action="{task_url}" method="POST" data-source="task" id="obsForm">
                <div>
                    <div class="block obsField" id="parent_respiration_rate">
                        <div class="input-header">
                            <label for="respiration_rate">Respiration Rate</label>
                            <input step="1" name="respiration_rate" max="59" min="1" type="number" id="respiration_rate"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_indirect_oxymetry_spo2">
                        <div class="input-header">
                            <label for="indirect_oxymetry_spo2">O2 Saturation</label>
                            <input step="1" name="indirect_oxymetry_spo2" max="100" min="51" type="number" id="indirect_oxymetry_spo2"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_body_temperature">
                        <div class="input-header">
                            <label for="body_temperature">Body Temperature</label>
                            <input step="0.1" name="body_temperature" max="44.9" min="27.1" type="number" id="body_temperature"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_blood_pressure_systolic">
                        <div class="input-header">
                            <label for="blood_pressure_systolic">Blood Pressure Systolic</label>
                            <input step="1" name="blood_pressure_systolic" max="300" min="1" type="number" id="blood_pressure_systolic"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_blood_pressure_diastolic">
                        <div class="input-header">
                            <label for="blood_pressure_diastolic">Blood Pressure Diastolic</label>
                            <input step="1" name="blood_pressure_diastolic" max="280" min="1" type="number" id="blood_pressure_diastolic"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField" id="parent_pulse_rate">
                        <div class="input-header">
                            <label for="pulse_rate">Pulse Rate</label>
                            <input step="1" name="pulse_rate" max="250" min="1" type="number" id="pulse_rate"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_avpu_text">
                        <div class="input-header">
                            <label for="avpu_text">AVPU</label>
                        </div>
                       <div class="input-body">
                           <select name="avpu_text" id="avpu_text">
                                <option value="">Please Select</option>
                                <option value="A">Alert</option>
                                <option value="V">Voice</option>
                                <option value="P">Pain</option>
                                <option value="U">Unresponsive</option>
                            </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField" id="parent_oxygen_administration_flag">
                        <div class="input-header">
                            <label for="oxygen_administration_flag">Patient on supplemental O2</label>
                        </div>
                       <div class="input-body">
                           <select name="oxygen_administration_flag" id="oxygen_administration_flag">
                                <option value="">Please Select</option>
                                <option value="False">No</option>
                                <option value="True">Yes</option>
                           </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <div>
                    <div class="block obsSelectField valHide" id="parent_device_id">
                        <div class="input-header">
                            <label for="device_id">O2 Device</label>
                        </div>
                        <div class="input-body">
                            <select name="device_id" class="exclude" id="device_id">
                                {device_options}
                            </select>
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_flow_rate">
                        <div class="input-header">
                            <label for="flow_rate">Flow Rate</label>
                            <input class="exclude" step="0.1" name="flow_rate" max="100.0"  type="number" id="flow_rate"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_concentration">
                        <div class="input-header">
                            <label for="concentration">Concentration</label>
                            <input class="exclude" step="1" name="concentration" max="100"  type="number" id="concentration"/>

                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_cpap_peep">
                        <div class="input-header">
                            <label for="cpap_peep">CPAP: PEEP (cmH2O)</label>
                            <input class="exclude" step="1" name="cpap_peep" max="1000"  type="number" id="cpap_peep"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_niv_backup">
                        <div class="input-header">
                            <label for="niv_backup">NIV: Back-up rate (br/min)</label>
                            <input class="exclude" step="1" name="niv_backup" max="100"  type="number" id="niv_backup"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_niv_ipap">
                        <div class="input-header">
                            <label for="niv_ipap">NIV: IPAP (cmH2O)</label>
                            <input class="exclude" step="1" name="niv_ipap" max="100"  type="number" id="niv_ipap"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="block obsField valHide" id="parent_niv_epap">
                        <div class="input-header">
                            <label for="niv_epap">NIV: EPAP (cmH2O)</label>
                            <input class="exclude" step="1" name="niv_epap" max="100"  type="number" id="niv_epap"/>
                        </div>
                        <div class="input-body">
                            <span class="errors"></span>
                            <span class="help"></span>
                        </div>
                    </div>
                </div>
                <input value="{task_id}" type="hidden" name="taskId"/>
                <input value="{timestamp}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
            <script type="text/javascript" src="/mobile/src/js/jquery.js"></script>
            <script type="text/javascript" src="/mobile/src/js/routes.js"></script>
            <script type="text/javascript" src="/mobile/src/js/validation.js"></script>
            <script type="text/javascript" src="/mobile/src/js/observation.js"></script>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""


# add jquery to header
# add frontend_routes to header
# check frontend_routes has been added correctly
# call the score endpoint with data
# on success check the results were as expected
AJAX_SCORE_CALCULATION_CODE = "frontend_routes.ews_score().ajax({{" \
                              "data:'respiration_rate={respiration_rate}&pulse_rate={pulse_rate}&indirect_oxymetry_spo2={spo2}&body_temperature={body_temp}&blood_pressure_systolic={bp}&avpu_text={avpu}&oxygen_administration_flag={oxygen_flag}'," \
                              "success:function(data){{" \
                              "if(data.score=={score}&&data.clinical_risk=={clinical_risk}&&data.three_in_one=={three_in_one}){{" \
                              "console.log('ok');" \
                              "}}else{{" \
                              "console.log('error');" \
                              "}}" \
                              "}},error:function(err){{" \
                              "console.log('error');" \
                              "}}}});"

# an array of dictionaries to help with testing score endpoint

AJAX_SCORE_CALCULATION_DATA = [
    {
        'respiration_rate': 18,
        'pulse_rate': 65,
        'body_temperature': 37.5,
        'indirect_oxymetry_spo2': 99,
        'blood_pressure_systolic': 120,
        'avpu_text': 'A',
        'oxygen_administration_flag': False,
        'score': 0,
        'clinical_risk': '"None"',
        'three_in_one': 'false',
    },
    {
        'respiration_rate': 11,
        'pulse_rate': 65,
        'body_temperature': 37.5,
        'indirect_oxymetry_spo2': 99,
        'blood_pressure_systolic': 120,
        'avpu_text': 'A',
        'oxygen_administration_flag': False,
        'score': 1,
        'clinical_risk': '"Low"',
        'three_in_one': 'false',
    },
    {
        'respiration_rate': 11,
        'pulse_rate': 65,
        'body_temperature': 37.5,
        'indirect_oxymetry_spo2': 99,
        'blood_pressure_systolic': 120,
        'avpu_text': 'V',
        'oxygen_administration_flag': False,
        'score': 4,
        'clinical_risk': '"Medium"',
        'three_in_one': 'true',
    },
    {
        'respiration_rate': 24,
        'pulse_rate': 130,
        'body_temperature': 36.0,
        'indirect_oxymetry_spo2': 93,
        'blood_pressure_systolic': 100,
        'avpu_text': 'A',
        'oxygen_administration_flag': True,
        'score': 11,
        'clinical_risk': '"High"',
        'three_in_one': 'false',
    },
]

TAKE_TASK_AJAX = "frontend_routes.json_take_task({task_id}).ajax({{" \
                             "success:function(data){{" \
                             "if(data.status.toString() === 'true'){{" \
                             "console.log('ok');" \
                             "}}else{{" \
                             "console.log('error');" \
                             "}}" \
                             "}},error:function(err){{" \
                             "console.log('error');" \
                             "}}}});"

CANCEL_TAKE_TASK_AJAX = "frontend_routes.json_cancel_take_task({task_id}).ajax({{" \
                 "success:function(data){{" \
                 "if(data.status.toString() === 'true'){{" \
                 "console.log('ok');" \
                 "}}else{{" \
                 "console.log('error');" \
                 "}}" \
                 "}},error:function(err){{" \
                 "console.log('error');" \
                 "}}}});"

PARTIAL_REASONS_AJAX = "frontend_routes.json_partial_reasons().ajax({" \
                        "dataType:'json'," \
                        "success:function(data){" \
                        "console.log('ok');" \
                        "},error:function(err){" \
                        "console.log('error');" \
                        "}});"

TASK_CANCELLATION_REASONS_AJAX = "frontend_routes.ajax_task_cancellation_options().ajax({" \
                                 "dataType:'json'," \
                                 "success:function(data){" \
                                 "console.log('ok');" \
                                 "},error:function(err){" \
                                 "console.log('error');" \
                                 "}});"

