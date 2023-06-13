import xlwings as xw
from data_tables_produce_all_measures import *

def apply_rounding_and_suppression(sac_unrounded):
    not_to_be_rounded_columns = ['GEOGRAPHY','ONS area code','CASSR Code','CASSR Name','Council Type / Region Name','18-64',
                             '65-74','75-84','85+','Total adult population','eprop_18_64','eprop_65_74','eprop_75_84',
                             'eprop_85+','18-64 rate','65-74 rate','75-84 rate','85+ rate','Age standardised rate',
                             'SG4a Yes they were asked and outcomes were expressed', 'SG4a Yes they were asked but no outcomes were expressed',
                             'SG4a No', "SG4a Don't Know", 'SG4a Not Recorded','SG4a Fully Achieved', 'SG4a Partially Achieved',
                             'SG4a Not Achieved','FY Key','Year','Proportion S42','Conversion Rate']
    rate_columns = ['Proportion S42','Conversion Rate','18-64 rate','65-74 rate','75-84 rate','85+ rate','Age standardised rate',]
    rounding_columns = [col for col in sac_unrounded.columns if col not in not_to_be_rounded_columns]
    for col in rounding_columns:
        sac_unrounded.loc[sac_unrounded[col] < 5, col] = 0
    for col in rounding_columns:
        sac_unrounded[col] = sac_unrounded[col].apply(my_round5)
    for col in rounding_columns:
        sac_unrounded.loc[sac_unrounded[col] < 5, col] = '[c]'
    for col in rate_columns:
        sac_unrounded[col] = sac_unrounded[col].round(0)
    return sac_unrounded
    
def create_msp_dummy_values(sac_rounded,sac_unrounded):
    sac_rounded.loc[((sac_unrounded['SG4a Yes they were asked and outcomes were expressed'] == 0) &
            (sac_unrounded['SG4a Yes they were asked but no outcomes were expressed'] == 0) &
            (sac_unrounded['SG4a No'] == 0) &
            (sac_unrounded["SG4a Don't Know"] == 0) &
            (sac_unrounded['SG4a Not Recorded'] == 0)),
            ('SG4a Yes they were asked and outcomes were expressed','SG4a Yes they were asked but no outcomes were expressed','SG4a No',"SG4a Don't Know",'SG4a Not Recorded')] = 999999
    sac_rounded.loc[((sac_unrounded['SG4a Fully Achieved'] == 0) &
            (sac_unrounded['SG4a Partially Achieved'] == 0) &
            (sac_unrounded['SG4a Not Achieved'] == 0)),
            ('SG4a Fully Achieved','SG4a Partially Achieved','SG4a Not Achieved')] = 999999
    return sac_rounded
   
def apply_msp_rounding_and_suppression(sac_rounded):
    msp_columns = ['SG4a Yes they were asked and outcomes were expressed', 'SG4a Yes they were asked but no outcomes were expressed',
    'SG4a No', "SG4a Don't Know", 'SG4a Not Recorded','SG4a Fully Achieved', 'SG4a Partially Achieved',
    'SG4a Not Achieved']
    for col in msp_columns:
        sac_rounded.loc[sac_rounded[col] < 5, col] = 0
    for col in msp_columns:
        sac_rounded[col] = sac_rounded[col].apply(my_round5)
    for col in msp_columns:
        sac_rounded.loc[sac_rounded[col] < 5, col] = '[c]'
    for col in msp_columns:
        sac_rounded.loc[sac_rounded[col] == 1000000, col] = '[x]'
    return sac_rounded

def create_table_ranges(sac_rounded):
    range1 = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', 'SG1f Total Number of Safeguarding Concerns', 'SG1f Total Number of Section 42 Safeguarding Enquiries', 'SG1f Total Number of Other Safeguarding Enquiries', 'Total Enquiries']].values
    range2a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name','Total Concluded Enquiries']].values 
    range2b = sac_rounded[['SG2a Physical Abuse', 'SG2a Sexual Abuse', 'SG2a Psychological Abuse', 'SG2a Financial or Material Abuse', 'SG2a Discriminatory Abuse', 'SG2a Organisational Abuse', 'SG2a Neglect and Acts of Omission', 'SG2a Domestic Abuse', 'SG2a Sexual Exploitation', 'SG2a Modern Slavery', 'SG2a Self-Neglect']].values
    range2c = sac_rounded[['SG2b Own Home', 'SG2b In the Community', 'SG2b Community Service', 'SG2b Care Home - Nursing', 'SG2b Care Home - Residential', 'SG2b Hospital - Acute', 'SG2b Hospital - Mental Health', 'SG2b Hospital - Community', 'SG2b Other']].values
    range2d = sac_rounded[['SG2b Service Provider', 'SG2b Other - Known to individual', 'SG2b Other - Unknown to individual']].values
    range3a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', 'SG2c Risk identified and action taken', 'SG2c Risk identified and no action taken', 'SG2c Risk Assessment inconclusive and action taken', 'SG2c Risk Assessment inconclusive and no action taken','SG2c No risk identified and action taken', 'SG2c No risk identified and no action taken', "SG2c Enquiry ceased at individual's request and no action taken"]].values
    range3b = sac_rounded[['SG2e Risk remained', 'SG2e Risk reduced', 'SG2e Risk removed']].values
    range4a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', '18-64 rate', '65-74 rate', '75-84 rate', '85+ rate', 'Age standardised rate']].values
    range4b = sac_rounded[['18-64', '65-74', '75-84', '85+']].values
    range5a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', 'SG1b Male', 'SG1b Female', 'SG1b Not Known']].values
    range5b = sac_rounded[['SG1c White', 'SG1c Mixed / Multiple', 'SG1c Asian / Asian British', 'SG1c Black / African / Caribbean / Black British', 'SG1c Other Ethnic Group', 'SG1c Refused', 'SG1c Undeclared / Not Known']].values
    range6a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', 'SG1d Physical Support', 'SG1d Sensory Support', 'SG1d Support with Memory and Cognition', 'SG1d Learning Disability Support', 'SG1d Mental Health Support', 'SG1d Social Support', 'SG1d No Support Reason', 'SG1d Not Known']].values
    range6b = sac_rounded[["SG1e Learning, Developmental or Intellectual Disability (Autism excluding Asperger's Syndrome/ High Functioning Autism)","SG1e Learning, Developmental or Intellectual Disability (Asperger's Syndrome/ High Functioning Autism)"]].values
    range7a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', 'SG3a Yes, they lacked capacity', 'SG3a No, they did not lack capacity', "SG3a Don't know", 'SG3a Not recorded']].values
    range7b = sac_rounded[['SG3a Of the enquiries recorded as Yes, in how many of these cases was support provided by an advocate, family or friend']].values
    range8a = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name', 'SG4a Yes they were asked and outcomes were expressed', 'SG4a Yes they were asked but no outcomes were expressed', 'SG4a No', "SG4a Don't Know", 'SG4a Not Recorded']].values
    range8b = sac_rounded[['SG4a Fully Achieved', 'SG4a Partially Achieved', 'SG4a Not Achieved']].values
    range9 = sac_rounded[['ONS area code','CASSR Code','CASSR Name','Council Type / Region Name','SG5a Where one or more individuals died','SG5a Where no individuals died']].values
    return range1,range2a,range2b,range2c,range2d,range3a,range3b,range4a,range4b,range5a,range5b,range6a,range6b,range7a,range7b,range8a,range8b,range9

def export_table_ranges_to_excel(range1,range2a,range2b,range2c,range2d,range3a,range3b,range4a,range4b,range5a,range5b,range6a,range6b,range7a,range7b,range8a,range8b,range9):
    wb = xw.Book(params['data_tables_output_location'])
    sht1 = wb.sheets[3]
    sht2 = wb.sheets[4]
    sht3 = wb.sheets[5]
    sht4 = wb.sheets[6]
    sht5 = wb.sheets[7]
    sht6 = wb.sheets[8]
    sht7 = wb.sheets[9]
    sht8 = wb.sheets[10]
    sht9 = wb.sheets[11]
    sht1.range('A4').value = range1
    sht2.range('A5').value = range2a
    sht2.range('G5').value = range2b
    sht2.range('S5').value = range2c
    sht2.range('AC5').value = range2d
    sht3.range('A5').value = range3a
    sht3.range('M5').value = range3b
    sht4.range('A5').value = range4a
    sht4.range('J5').value = range4b
    sht5.range('A5').value = range5a
    sht5.range('I5').value = range5b
    sht6.range('A5').value = range6a
    sht6.range('N5').value = range6b
    sht7.range('A5').value = range7a
    sht7.range('J5').value = range7b
    sht8.range('A5').value = range8a
    sht8.range('K5').value = range8b 
    sht9.range('A5').value = range9
    return sht1,sht2,sht3,sht4,sht5,sht6,sht7,sht8,sht9

def produce_csv_output(sac_df):
    sac_csv = sac_df[['GEOGRAPHY','COUNCIL_TYPE','REGION_CODE','REGION_NAME','ONS_CODE','LA_CODE','LA_NAME','TABLE_REFERENCE','ENQUIRY_TYPE','CATEGORY','SUBCATEGORY','VALUE']]
    return sac_csv.sort_values(['LA_CODE', 'TABLE_REFERENCE', 'ENQUIRY_TYPE', 'CATEGORY', 'SUBCATEGORY'])

def csv_rounding_and_suppression(sac_csv):
    sac_csv['VALUE'] = sac_csv['VALUE'].fillna(999999)
    sac_csv.loc[sac_csv['VALUE'] < 5, 'VALUE'] = 0
    sac_csv['VALUE'] = sac_csv['VALUE'].apply(my_round5)
    sac_csv.loc[sac_csv['VALUE'] < 5, 'VALUE'] = '[c]'
    sac_csv.loc[sac_csv['VALUE'] == 1000000, 'VALUE'] = '[x]'
    return sac_csv

def export_csv_file(sac_csv):
    return sac_csv.to_csv(params['final_csv_output_location'],index = False)