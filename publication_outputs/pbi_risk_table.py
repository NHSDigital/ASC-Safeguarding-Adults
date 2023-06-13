from data_tables_read_in_data import *
from pbi_current_and_map import exclude_cassr_codes
from data_tables_produce_all_measures import my_round5

def create_risk_table_dataframe():
    sac_df = read_in_data()
    sac_risk = sac_df[['GEOGRAPHY','COUNCIL_TYPE','REGION_CODE','REGION_NAME','ONS_CODE','LA_CODE','LA_NAME','TABLE_REFERENCE','ENQUIRY_TYPE','CATEGORY','SUBCATEGORY','USED_IN_POWER_BI','VALUE']]
    sac_risk['Year'] = params['reporting_year']
    return sac_risk[(sac_risk['TABLE_REFERENCE'].isin(['SG2a','SG2a_b1','SG2b'])) & (sac_risk['USED_IN_POWER_BI'] == 'Y')]

def add_table_reference_detail(sac_risk):
    sac_risk['Table'] = 'Invalid'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2a','Table'] = 'Type and Source (SG2a)'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2b','Table'] = 'Location and Source (SG2b)'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2a_b1','Table'] = 'Type and Location (SG2ab1)'
    return sac_risk

def add_column_name_detail(sac_risk):
    sac_risk['Column Name'] = 'Invalid'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2a','Column Name'] = 'Source of Risk'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2b','Column Name'] = 'Source of Risk'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2a_b1','Column Name'] = 'Location of Risk'
    return sac_risk

def add_row_name_detail(sac_risk):
    sac_risk['Row Name'] = 'Invalid'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2a','Row Name'] = 'Type of Risk'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2b','Row Name'] = 'Location of Risk'
    sac_risk.loc[sac_risk['TABLE_REFERENCE']=='SG2a_b1','Row Name'] = 'Type of Risk'
    return sac_risk

def rename_output_columns(sac_risk):
    sac_risk.rename(columns={'CATEGORY':'Row','SUBCATEGORY':'Column','LA_CODE':'CASSR','VALUE':'Value'},inplace=True)
    return sac_risk

def create_england_rows(sac_risk):
    sac_england_risk = sac_risk[['Year','CASSR','Table','Column Name','Row Name','Column','Row','Value']]
    sac_england_risk = sac_england_risk.groupby(['Year','Table','Column Name','Row Name','Column','Row']).sum(numeric_only=False)
    sac_england_risk = sac_england_risk.reset_index()
    sac_england_risk['CASSR'] = '1010'
    return pd.concat([sac_england_risk,sac_risk],axis=0)

def apply_risk_table_rounding_and_suppression(sac_risk):
    sac_risk.loc[sac_risk['Value'] < 5, 'Value'] = 0
    sac_risk['Value'] = sac_risk['Value'].apply(my_round5)
    return sac_risk

def format_final_pbi_risk_table(sac_risk):
    return sac_risk[['Year','CASSR','Table','Column Name','Row Name','Column','Row','Value']]

def create_and_export_pbi_risk_table():
    sac_risk = create_risk_table_dataframe()
    sac_risk = sac_risk[(sac_risk['LA_CODE'].notnull())]
    sac_risk = add_table_reference_detail(sac_risk)
    sac_risk = add_column_name_detail(sac_risk)
    sac_risk = add_row_name_detail(sac_risk)
    sac_risk = rename_output_columns(sac_risk)
    sac_risk = create_england_rows(sac_risk)
    sac_risk = apply_risk_table_rounding_and_suppression(sac_risk)
    sac_risk = format_final_pbi_risk_table(sac_risk)
    return sac_risk.to_csv(params['pbi_risk_output_location'],index = False)