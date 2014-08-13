__author__ = 'colin'

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
