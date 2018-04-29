Feature: Encodage de notes
  Nous allons verifier que l'encodage de notre fonctionne correctement

  Scenario: Change the start date of the academic calendar and
    check if the new start date is available

    Given I am a Super User
    And There is an Academic Calendar
    And Login
    And I am on the Academic Calendar page
    When I change the start date in the form
    Then the start date on the detail view should be equal

  Scenario: Change the end date of the academic calendar and
    check if the new end date is available

    Given I am a Super User
    And There is an Academic Calendar
    And Login
    And I am on the Academic Calendar page
    When I change the end date in the form
    Then the end date on the detail view should be equal

  Scenario: Check if there is a future scores encoding period

    Given I am a Program Manager
    And There is an Academic Calendar in the future
    And I am the Program Manager of this Academic Calendar
    And There is a Session Exam
    And Login
    When I am on the Scores Encoding page
    Then The scores encoding period will be open in the future

