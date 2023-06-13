import pandas as pd
import numpy as np
from datetime import datetime
import sqlalchemy as sa
import json

def load_parameters(file):
    f = open(file)
    return json.load(f)

params = load_parameters('params.json')

def load_sql_script_from_txt(dir):
    f = open(dir, 'r')
    return sa.text(f.read())

def read_in_data():
    CONN = sa.create_engine(f"mssql+pyodbc://{params['servername']}/{params['database']}?driver=SQL+Server",fast_executemany=True)
    sql_script = load_sql_script_from_txt(params['sql_script_location'])
    all_sac_data = pd.read_sql_query(sql_script,CONN,params = {"year":params['year_key']})
    mapping_file = pd.read_csv(params['mapping_file_location'])
    mapping_file['LA_CODE'] = mapping_file['LA_CODE'].astype('str')
    question_ref_info = pd.read_csv(params['question_reference_location'])
    sac_df = pd.merge(all_sac_data,mapping_file,left_on ='CASSR_CODE',right_on='LA_CODE',how='left')
    sac_df = pd.merge(sac_df,question_ref_info,left_on='SAC_QUESTION_REFERENCE',right_on='SAC_QUESTION_REFERENCE',how='left')
    return sac_df