# Created by colinwren at 21/04/16
Feature: Escalations
  As a Nurse
  In order to ensure that I am made aware of any ill patients
  I want the system to prompt HCA staff members to inform me of these patients

  Scenario: Nurse task to confirm escalation happened
    Given I am logged in on the mobile as a Nurse
    When a HCA submits an EWS observation for a patient with a Low, Medium or High clinical risk
    Then I see a task for me to confirm that the HCA informed me of the patient's clinical risk


  Scenario Outline: HCA prompted to inform nurse of clinical risk after observation
    Given I am logged in as a HCA
    And I submit a NEWS Observation for a patient with a <risk> clinical risk
    And I confirm the calculated clinical risk to be <risk string>
    When I am shown the triggered tasks popup
    Then I should see these triggered tasks:
      | tasks                      |
      | Inform Nurse About Patient |

    Examples:
      | risk   | risk string |
      | low    | Low Risk    |
      | medium | Medium Risk |
      | high   | High Risk   |

  Scenario Outline: HCA prompted to inform nurse of clinical risk shown in task list for HCA
    Given I am logged in as a HCA
    And I submit a NEWS Observation for a patient with a <risk> clinical risk who has been in hospital for <stay duration> days
    And I confirm the calculated clinical risk to be <risk string>
    When I go to the task list
    Then I should see the following new notifications for the patient
      | tasks                      |
      | Inform Nurse About Patient |

    Examples:
      | risk   | risk string |
      | low    | Low Risk    |
      | medium | Medium Risk |
      | high   | High Risk   |