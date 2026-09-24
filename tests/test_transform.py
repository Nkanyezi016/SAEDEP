import pandas as pd

from src.transform import transform


def test_column_names_are_transformed():

    df = pd.DataFrame({
        "UQNO": [1],
        "PERSONNO": [1],
        "SURVEYDATE": ["2026-01-01"],
        "Province": ["Gauteng"],
        "Metro_code": [1],
        "Geo_Type_Code": [1],
        "Stratum": [1],
        "Q13GENDER": ["Male"],
        "Q14AGE": [25],
        "Q16MARITALSTATUS": ["Single"],
        "Q17EDUCATION": ["Degree"],
        "Q15POPULATION": ["African"],
        "Q18FIELD": ["Mathematics"],
        "Q19ATTE": ["Yes"],
        "Status": ["Employed"],
        "Lfs_Status": ["Labour Force"],
        "Unempl_Status": ["Not Applicable"],
        "InactReason": ["Not Applicable"],
        "Indus": [1],
        "Occup": [1],
        "PrevIndus": [1],
        "PrevOccup": [1],
        "Sector": [1],
        "Infempl": ["No"],
        "Long_term_unempl": ["No"],
        "Underempl": ["No"],
        "Neet": ["No"],
        "Graduates": ["Yes"],
        "Education_status": ["Completed"],
        "Age_grp1": ["25-34"],
        "Hrswrk": [40],
        "Weight": [1.5],
    })

    result = transform(df)

    assert "Unique_Questionnaire_Number" in result.columns
    assert "Person_Number" in result.columns
    assert "Survey_Date" in result.columns
    assert "Gender" in result.columns
    assert "Age" in result.columns
    assert "Marital_Status" in result.columns
    assert "Education_Level" in result.columns
    assert "Employment_Status" in result.columns


def test_old_column_names_are_removed():
    df = pd.DataFrame({
        "UQNO": [1],
        "PERSONNO": [1],
        "SURVEYDATE": ["2026-01-01"],
        "Province": ["Gauteng"],
        "Metro_code": [1],
        "Geo_Type_Code": [1],
        "Stratum": [1],
        "Q13GENDER": ["Male"],
        "Q14AGE": [25],
        "Q16MARITALSTATUS": ["Single"],
        "Q17EDUCATION": ["Degree"],
        "Q15POPULATION": ["African"],
        "Q18FIELD": ["Mathematics"],
        "Q19ATTE": ["No"],
        "Status": ["Employed"],
        "Lfs_Status": ["Employed"],
        "Unempl_Status": ["Not unemployed"],
        "InactReason": ["None"],
        "Indus": ["Education"],
        "Occup": ["Professional"],
        "PrevIndus": ["Education"],
        "PrevOccup": ["Professional"],
        "Sector": ["Formal"],
        "Infempl": ["No"],
        "Long_term_unempl": ["No"],
        "Underempl": ["No"],
        "Neet": ["No"],
        "Graduates": ["Yes"],
        "Education_status": ["Completed"],
        "Age_grp1": ["25-34"],
        "Hrswrk": [40],
        "Weight": [1.0],
    })

    result = transform(df)

    # Old names should be gone
    assert "UQNO" not in result.columns
    assert "PERSONNO" not in result.columns
    assert "Q13GENDER" not in result.columns
    assert "Q14AGE" not in result.columns

    # New names should exist
    assert "Unique_Questionnaire_Number" in result.columns
    assert "Person_Number" in result.columns
    assert "Gender" in result.columns
    assert "Age" in result.columns