Feature: Encodage des notes

  Background:
    Given I am a Program Manager
    And There is an Academic Calendar
    And There are 3 Learning Unit Year
    And There are several Offer Years where I am the Program Manager
      | acronym  |
      | PHYS11BA |
      | ECON2M1  |
      | PHYS1BA  |
      | PHYS2M1  |
      | PHYS2MA  |
    And There are 10 students for "PHYS11BA" and the Learning Unit Year 1
    And There is a Session Exam for "PHYS11BA" and the Learning Unit Year 1
    And Login

  Scenario: Scenario 4
    When I am on the Scores Encoding page
    Then I have the previous Offer Years in the list of Programs
     And There is 1 Learning Unit

  Scenario: Scenario 4 - Part 1
    When I am on the Scores Encoding page
     And I want to encode the Learning Unit Year 1
    Then The decimal scores are not possible
     And The number of enrollments is 10

  Scenario: Scenario 4 - Part 2
    When I am on the Scores Encoding page
     And I want to encode the Learning Unit Year 1
     And I change the note of the first enrollment with 12
     And I save the online encoding
    Then The progression must be 1 on 10
     And The note for this enrollment is 12
     And This enrollment has the plane icon

  Scenario: Scenario 4 - Part 3
    When I am on the Scores Encoding page
    And I want to encode the Learning Unit Year 1
    And I change the notes of the enrollments
    And I save the online encoding
    Then The progression must be 10 on 10
    And The enrollments have the plane icon
    And The enrollments have the computed values

  Scenario: Scenario 5 - Export / Import modified Excel file
    When I am on the Scores Encoding page
    And I search for the "PHYS11BA" offer
    And I download the Excel file of Learning Unit Year 1
    And I upload a modified version of the Excel file
    Then The progression must be 10 on 10
    And The enrollments have the computed values

  Scenario: Scenario 6 - Check the progression
    When I am on the Scores Encoding page
    And I want to encode the Learning Unit Year 1
    And I change the notes of the enrollments
    And I save the online encoding
    Then The progression must be 10 on 10

  Scenario: Scenario 6 - Check the double encoding
    When I am on the Scores Encoding page
    And I want to encode the Learning Unit Year 1
    And I change the notes of the enrollments
    And I save the online encoding
    And I use the double encoding
    And I force the notes of the enrollments
    Then The enrollments have the forced values

  Scenario: Scenario 7 - Print PDF
    When I am on the Scores Encoding page
    And I want to encode the Learning Unit Year 1
    And I change the notes of the enrollments
    And I save the online encoding
    And I am on the Scores Encoding page
    Then I load the PDF file of the Learning Unit Year 1

