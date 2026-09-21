from pathlib import Path
import pandas as pd

SOURCE_FILE = Path("data/source/QLFS202602.csv")
labor_data = pd.read_csv(SOURCE_FILE)

def remove_unneccessary_columns(df):
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

def remove_uneccessary_records(df):
    df = df.dropna(subset=["Weight"])
    df = df[df["Weight"] > 0]
        
    return df 