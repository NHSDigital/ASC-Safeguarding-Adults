from data_tables_read_in_data import *
from data_tables_produce_all_measures import *
from data_tables_export_outputs import *
from pbi_current_and_map import *
from pbi_risk_table import *
from pbi_safeguarding_adult_reviews import *
import os

start_time = datetime.now()

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def run_tables_and_csv():
    sac_df = read_in_data()
    all_measures = produce_all_table_measures(sac_df)
    england_measures = format_england_breakdown(all_measures)
    council_type_measures = format_council_type_breakdown(all_measures)
    region_measures = format_region_breakdown(all_measures)
    la_measures = format_local_authority_breakdown(all_measures)
    sac_unrounded = append_all_breakdowns(england_measures,council_type_measures,region_measures,la_measures)
    sac_unrounded = add_additional_measures(sac_unrounded)
    sac_unrounded = add_england_proportions(sac_df,sac_unrounded)
    sac_unrounded = calculate_all_rates_per_100k(sac_unrounded)
    sac_unrounded = calculate_age_standardised_rate(sac_unrounded)
    export_unrounded_csv(sac_unrounded)
    sac_rounded = apply_rounding_and_suppression(sac_unrounded)
    sac_rounded = create_msp_dummy_values(sac_rounded,sac_unrounded)
    sac_rounded = apply_msp_rounding_and_suppression(sac_rounded)
    range1,range2a,range2b,range2c,range2d,range3a,range3b,range4a,range4b,range5a,range5b,range6a,range6b,range7a,range7b,range8a,range8b,range9 = create_table_ranges(sac_rounded)
    export_table_ranges_to_excel(range1,range2a,range2b,range2c,range2d,range3a,range3b,range4a,range4b,range5a,range5b,range6a,range6b,range7a,range7b,range8a,range8b,range9)
    sac_csv = produce_csv_output(sac_df)
    sac_csv = csv_rounding_and_suppression(sac_csv)
    export_csv_file(sac_csv)

def run_power_bi():
    sac_pbi = create_and_export_pbi_current()
    create_and_export_pbi_map(sac_pbi)
    create_and_export_pbi_risk_table()
    create_and_export_pbi_sars()

run_tables_and_csv()
run_power_bi()

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
