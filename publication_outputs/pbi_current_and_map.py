from data_tables_produce_all_measures import *

def pbi_current_measures(sac_unrounded):
    sac_pbi = sac_unrounded[(sac_unrounded['Council Type / Region Name'] == 'ENGLAND')|(sac_unrounded['CASSR Code']!= '-')]
    sac_pbi.loc[sac_pbi['Council Type / Region Name'] == 'ENGLAND','CASSR Code'] = '1010'
    sac_pbi.loc[sac_pbi['Council Type / Region Name'] == 'ENGLAND','CASSR Name'] = 'England'
    return sac_pbi[['FY Key','Year','CASSR Code','18-64 rate','65-74 rate','75-84 rate','85+ rate','Concerns per 100K','Section 42 per 100K','Other Enquiries per 100K','Total Enquiries per 100K','SG1f Total Number of Safeguarding Concerns','SG1f Total Number of Section 42 Safeguarding Enquiries','SG1f Total Number of Other Safeguarding Enquiries','Total Enquiries','Conversion Rate','Proportion S42','SG2a Discriminatory Abuse','SG2a Domestic Abuse','SG2a Financial or Material Abuse','SG2a Modern Slavery','SG2a Neglect and Acts of Omission','SG2a Organisational Abuse','SG2a Physical Abuse','SG2a Psychological Abuse','SG2a Self-Neglect','SG2a Sexual Abuse','SG2a Sexual Exploitation']]

def apply_pbi_current_rounding_and_suppression(sac_pbi):
    not_to_be_rounded_columns = ['FY Key','Year','CASSR Code',
                                '18-64 rate','65-74 rate','75-84 rate','85+ rate','Concerns per 100K',
                                'Section 42 per 100K','Other Enquiries per 100K','Total Enquiries per 100K',
                                'Conversion Rate','Proportion S42','FY Key','Year']
    rate_columns = ['18-64 rate','65-74 rate','75-84 rate','85+ rate','Concerns per 100K',
                    'Section 42 per 100K','Other Enquiries per 100K','Conversion Rate','Total Enquiries per 100K',
                    'Proportion S42']
    rounding_columns = [col for col in sac_pbi.columns if col not in not_to_be_rounded_columns]
    for col in rounding_columns:
        sac_pbi.loc[sac_pbi[col] < 5, col] = 0
    for col in rounding_columns:
        sac_pbi[col] = sac_pbi[col].apply(my_round5)
    for col in rate_columns:
        sac_pbi[col] = sac_pbi[col].round(0)
    return sac_pbi

def format_final_pbi_current(sac_pbi):
    first_cols = ['FY Key','Year','CASSR Code']
    last_cols = [col for col in sac_pbi.columns if col not in first_cols]
    sac_pbi = sac_pbi[first_cols+last_cols]
    sac_pbi = sac_pbi.rename(columns={"SG1f Total Number of Other Safeguarding Enquiries": "Total Number of Other Safeguarding Enquiries",
                                      "SG1f Total Number of Safeguarding Concerns":"Total Number of Safeguarding Concerns",
                                      "SG1f Total Number of Section 42 Safeguarding Enquiries":"Total Number of Section 42 Safeguarding Enquiries",
                                      "SG2a Discriminatory Abuse":"Discriminatory Abuse",
                                      "SG2a Domestic Abuse":"Domestic Abuse",
                                      "SG2a Financial or Material Abuse":"Financial or Material Abuse",
                                      "SG2a Modern Slavery":"Modern Slavery",
                                      "SG2a Neglect and Acts of Omission":"Neglect and Acts of Omission",
                                      "SG2a Organisational Abuse":"Organisational Abuse",
                                      "SG2a Physical Abuse":"Physical Abuse",
                                      "SG2a Psychological Abuse":"Psychological Abuse",
                                      "SG2a Self-Neglect":"Self Neglect",
                                      "SG2a Sexual Abuse":"Sexual Abuse",
                                      "SG2a Sexual Exploitation":"Sexual Exploitation",
                                      "18-64 rate":"18-64 S42 per 100K",
                                      "65-74 rate":"65-74 S42 per 100K",
                                      "75-84 rate":"75-84 S42 per 100K",
                                      "85+ rate":"85+ S42 per 100K"})
    return sac_pbi.melt(id_vars=['FY Key','Year','CASSR Code'], var_name='Measure', value_name='Value')

def exclude_cassr_codes(df,cassr_codes):
    df = df[~df['CASSR Code'].isin (cassr_codes)]
    return df

def calculate_quartiles(df):
    df.loc[(df['Value'] >= np.percentile(df['Value'], 0)) & 
                         (df['Value'] <= np.percentile(df['Value'], 25)), 'Map Quartile'] = '1st to 25th percentile'
    df.loc[(df['Value'] > np.percentile(df['Value'], 25)) & 
                         (df['Value'] <= np.percentile(df['Value'], 50)), 'Map Quartile'] = '26th to 50th percentile'
    df.loc[(df['Value'] > np.percentile(df['Value'], 50)) & 
                         (df['Value'] <= np.percentile(df['Value'], 75)), 'Map Quartile'] = '51st to 75th percentile'
    df.loc[(df['Value'] > np.percentile(df['Value'], 75)) & (
        df['Value'] <= np.percentile(df['Value'], 100)), 'Map Quartile'] = '76th to 100th percentile'
    return df

def calculate_all_map_quartiles(sac_map):
    sac_map_concerns = sac_map[(sac_map['Measure'] == "Concerns per 100K")]
    sac_map_concerns = calculate_quartiles(sac_map_concerns)
    sac_map_s42 = sac_map[(sac_map['Measure'] == "Section 42 per 100K")]
    sac_map_s42 = calculate_quartiles(sac_map_s42)
    sac_map_other = sac_map[((sac_map['Measure'] == "Other Enquiries per 100K")) & (sac_map['Value'] != 0)]
    sac_map_other = calculate_quartiles(sac_map_other)
    sac_map_other_not_provided = sac_map[((sac_map['Measure'] == "Other Enquiries per 100K")) & (sac_map['Value'] == 0)]
    sac_map_other_not_provided['Map Quartile'] = 'No enquiries recorded'
    return pd.concat([sac_map_concerns,sac_map_s42,sac_map_other,sac_map_other_not_provided],axis=0).reset_index()

def format_final_pbi_map(sac_map):
    sac_map = sac_map[['FY Key','Year','CASSR Code','Measure','Value','Map Quartile']]
    return sac_map.replace({'Measure': {'Concerns per 100K':'1. Safeguarding Concerns per 100,000 adults',
                                        'Section 42 per 100K':'2. Section 42 Enquiries per 100,000 adults',
                                        'Other Enquiries per 100K':'3. Other Enquiries per 100,000 adults'}})

def create_and_export_pbi_current():
    sac_unrounded = produce_sac_unrounded()  
    sac_pbi = pbi_current_measures(sac_unrounded)
    sac_pbi = apply_pbi_current_rounding_and_suppression(sac_pbi)
    sac_pbi = format_final_pbi_current(sac_pbi)
    sac_pbi.to_csv(params['pbi_current_output_location'],index = False)
    return sac_pbi

def create_and_export_pbi_map(sac_pbi):
    sac_map = exclude_cassr_codes(sac_pbi,params['excluded_codes'])
    sac_map = calculate_all_map_quartiles(sac_map)
    sac_map = format_final_pbi_map(sac_map)
    return sac_map.to_csv(params['pbi_map_output_location'],index = False)