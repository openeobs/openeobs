__author__ = 'colin'

# URL structure
URL_PREFIX = '/mobile/'
URLS = {'patient_list': URL_PREFIX+'patients/',
        'single_patient': URL_PREFIX+'patient/',
        'task_list': URL_PREFIX+'tasks/',
        'single_task': URL_PREFIX+'task/',
        'stylesheet': URL_PREFIX+'src/css/main.css',
        'new_stylesheet': URL_PREFIX+'src/css/new.css',
        'logo': URL_PREFIX+'src/img/logo.png',
        'logout': URL_PREFIX+'logout/',
        'task_form_action': URL_PREFIX+'task/submit/',
        'patient_form_action': URL_PREFIX+'patient/submit/',
        }

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
            </ul>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
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
                            <p class="taskInfo">{7}<br/></p>
                        </div>
                    </a>
                </li>
            </ul>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
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
                <a href="{0}">{1}<i class="icon-info"></i></a>
            </h2>
            <form source="task" data-type="ews" action="/mobile/task/submit/{2}" data-id="{2}" method="POST" id="obsForm">
                <div>
                    <div id="parent_respiration_rate" class="block obsField">
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
                    <div id="parent_indirect_oxymetry_spo2" class="block obsField">
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
                    <div id="parent_body_temperature" class="block obsField">
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
                    <div id="parent_blood_pressure_systolic" class="block obsField">
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
                    <div id="parent_blood_pressure_diastolic" class="block obsField">
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
                    <div id="parent_pulse_rate" class="block obsField">
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
                    <div id="parent_avpu_text" class="block obsSelectField">
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
                    <div id="parent_oxygen_administration_flag" class="block obsSelectField">
                        <div class="input-header">
                            <label for="oxygen_administration_flag">Patient on supplemental O2</label>
                        </div>
                       <div class="input-body">
                           <select name="oxygen_administration_flag" id="oxygen_administration_flag">
                                <option value="">Please Select</option>
                                <option value="True">Yes</option>
                                <option value="False">No</option>
                           </select>
                           <span class="errors"></span>
                           <span class="help"></span>
                       </div>
                   </div>
                </div>
                <input value="{2}" type="hidden" name="taskId"/>
                <input value="{3}" type="hidden" name="startTimestamp" id="startTimestamp"/>
                <div class="block obsSubmit">
                    <input type="submit" id="submitButton" value="Submit"/>
                </div>
            </form>
        </div>
        <div class="footer block">
            <p class="user">norah</p>
        </div>
    </body>
</html>
"""
