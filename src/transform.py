from pathlib import Path
import pandas as pd

SOURCE_FILE = Path("data/source/QLFS202602.csv")

def remove_unnecessary_columns(df):
    """
    Removes unnecessary columns from the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    columns_to_remove (list): List of column names to remove.

    Returns:
    pd.DataFrame: DataFrame with unnecessary columns removed.
    """
    columns_to_keep = ["UQNO", "PERSONNO", "SURVEYDATE", "Province", "Metro_code", "Geo_Type_Code", "Stratum", "Q13GENDER", "Q14AGE", "Q16MARITALSTATUS", "Q17EDUCATION", "Q15POPULATION", "Q18FIELD", 
                       "Q19ATTE", "Status", "Lfs_Status", "Unempl_Status", "InactReason", "Indus", "Occup","PrevIndus", "PrevOccup", "Sector", "Infempl", "Long_term_unempl", "Underempl", "Neet",
                       "Graduates", "Education_status", "Age_grp1", "Hrswrk", "Weight"]
    df = df[columns_to_keep]
    
    return df 

def remove_unnecessary_records(df):
    df = df.dropna(subset=["Weight"])
    df = df[df["Weight"] > 0]
        
    return df 

def rename_cols(df):
    """
    Renames columns in the DataFrame to more descriptive names.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: DataFrame with renamed columns.
    """
    df = df.rename(columns={
        "UQNO": "Unique_Questionnaire_Number",
        "PERSONNO": "Person_Number",
        "SURVEYDATE": "Survey_Date",
        "Province": "Province",
        "Metro_code": "Metro_Code",
        "Geo_Type_Code": "Geo_Type_Code",
        "Stratum": "Stratum",
        "Q13GENDER": "Gender",
        "Q14AGE": "Age",
        "Q16MARITALSTATUS": "Marital_Status",
        "Q17EDUCATION": "Education_Level",
        "Q15POPULATION": "Population_Group",
        "Q18FIELD": "Field_of_Study",
        "Q19ATTE": "Attendance_Status",
        "Status": "Employment_Status",
        "Lfs_Status": "Labour_Force_Status",
        "Unempl_Status": "Unemployment_Status",
        "InactReason": "Reason_for_Inactivity",
        "Indus": "Industry_Code",
        "Occup": "Occupation_Code",
        "PrevIndus": "Previous_Industry_Code",
        "PrevOccup": "Previous_Occupation_Code",
        "Sector": "Sector_Code",
        "Infempl": "Informal_Employment_Status",
        "Long_term_unempl": "Long_Term_Unemployment_Status",
        "Underempl": "Underemployment_Status",
        "Neet": "'Not in Education, Employment, or Training' Status",
        'Graduates': 'Graduate Status',
        'Education_status': 'Education Status',
        'Age_grp1': 'Age Group',
        'Hrswrk': 'Hours Worked',
        'Weight': 'Weight'
    })
    
    return df

def convert_data_types(df):
    """
    Converts data types of specific columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: DataFrame with converted data types.
    """
    if "SURVEYDATE" in df.columns:
        df["SURVEYDATE"] = pd.to_datetime(df["SURVEYDATE"], errors='coerce')

    numeric_columns = [ "PERSONNO", "Metro_code", "Geo_Type_Code", "Stratum", "Q14AGE", "Hrswrk", "Weight" ]

    for column in numeric_columns: 
        df[column] = pd.to_numeric( df[column], errors="coerce" )
    
    return df

def change_to_category(df):
    """
    Converts specific columns in the DataFrame to categorical data type.
    """

    categorical_columns = [ "Province", "Q13GENDER", "Q16MARITALSTATUS", "Q17EDUCATION", "Q15POPULATION", "Q18FIELD", "Q19ATTE", "Status", "Lfs_Status", "Unempl_Status", "InactReason", "Indus", "Occup", "PrevIndus", "PrevOccup", "Sector", "Infempl", "Long_term_unempl", "Underempl", "Neet", "Graduates", "Education_status", "Age_grp1" ]

    for column in categorical_columns:
        if column in df.columns: 
            df[column] = df[column].astype("category")
    
    return df

def transform(df):
    """
    Transforms the DataFrame by applying a series of data cleaning and transformation steps.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: Transformed DataFrame.
    """
    df = remove_unnecessary_columns(df)
    df = remove_unnecessary_records(df)
    df = convert_data_types(df)
    df = change_to_category(df)
    df = rename_cols(df)

    # print(df)
    
    return df

# labor_data = pd.read_csv(SOURCE_FILE)
# new_data = transform(labor_data)
# print(new_data["PERSONNO"])

