from data_tables_read_in_data import *
from pbi_current_and_map import exclude_cassr_codes
from data_tables_produce_all_measures import my_round5


def local_authorities_with_sars(sac_df):
    number_of_las_with_sars = sac_df[sac_df["TABLE_REFERENCE"] == "SG5a"]
    number_of_las_with_sars = (
        (number_of_las_with_sars[["LA_CODE", "VALUE"]]).groupby("LA_CODE").sum()
    )
    return len(number_of_las_with_sars[number_of_las_with_sars["VALUE"] > 0])


def return_sars_data(sac_df):
    sac_sars = sac_df[
        [
            "GEOGRAPHY",
            "REGION_CODE",
            "TABLE_REFERENCE",
            "ENQUIRY_TYPE",
            "CATEGORY",
            "SUBCATEGORY",
            "COLUMN_NAME",
            "ROW_NAME",
            "VALUE",
        ]
    ]
    sac_sars = sac_sars[sac_sars["TABLE_REFERENCE"].isin(["SG5a", "SG5b"])]
    sac_sars = sac_sars[
        sac_sars["ENQUIRY_TYPE"].isin(
            [
                "Count of Safeguarding Adult Reviews",
                "Count of Individuals Involved in Safeguarding Adult Reviews",
            ]
        )
    ]
    return sac_sars.pivot_table(
        values="VALUE",
        index=["GEOGRAPHY", "REGION_CODE"],
        columns="COLUMN_NAME",
        aggfunc=np.sum,
    )


def add_additional_sars_measures(sac_sars):
    sac_sars["Number of SARS"] = (
        sac_sars["SG5a Where no individuals died"]
        + sac_sars["SG5a Where one or more individuals died"]
    )
    sac_sars["Number of people involved with SARS"] = (
        sac_sars["SG5b Who suffered serious harm and died"]
        + sac_sars["SG5b Who suffered serious harm and survived"]
    )
    sac_sars["FY Key"] = params["year_key"]
    sac_sars["Year"] = params["reporting_year"]
    return sac_sars.reset_index()


def create_region_sars_counts(sac_sars):
    sac_sars_region = sac_sars.drop(["GEOGRAPHY"], axis=1)
    sac_sars_region = sac_sars_region.melt(
        id_vars=["FY Key", "Year", "REGION_CODE"],
        var_name="Measure",
        value_name="Value",
    )
    sac_sars_region = sac_sars_region[sac_sars_region["Measure"] == "Number of SARS"]
    sac_sars_region = sac_sars_region.rename(columns={"REGION_CODE": "Code"})
    return sac_sars_region


def create_england_sars_counts(sac_sars, number_of_las_with_sars):
    sac_sars_england = sac_sars.groupby("GEOGRAPHY").sum(numeric_only=False).reset_index()
    sac_sars_england = sac_sars_england.drop(["REGION_CODE","GEOGRAPHY", "FY Key"], axis=1)
    sac_sars_england["FY Key"] = params["year_key"]
    sac_sars_england["Year"] = params["reporting_year"]
    sac_sars_england["Code"] = "E92000001"
    sac_sars_england["Number of LAs supplying data"] = params["number_of_las"]
    sac_sars_england["Number of LAs with SARS"] = number_of_las_with_sars
    return sac_sars_england.melt(
        id_vars=["FY Key", "Year", "Code"], var_name="Measure", value_name="Value"
    )


def apply_sars_rounding_and_suppression(sac_sars):
    sac_sars.loc[sac_sars["Value"] < 5, "Value"] = 0
    sac_sars["Value"] = sac_sars["Value"].apply(my_round5)
    return sac_sars


def create_and_export_pbi_sars():
    sac_df = read_in_data()
    number_of_las_with_sars = local_authorities_with_sars(sac_df)
    sac_sars = return_sars_data(sac_df)
    sac_sars = add_additional_sars_measures(sac_sars)
    sac_sars = sac_sars.drop(
        ["SG5a Where no individuals died", "SG5a Where one or more individuals died"],
        axis=1,
    )
    sac_sars = sac_sars.rename(
        columns={
            "SG5b Who suffered serious harm and died": "Number of individuals who died",
            "SG5b Who suffered serious harm and survived": "Number of individuals who suffered harm and survived",
        }
    )
    sac_sars_region = create_region_sars_counts(sac_sars)
    sac_sars_england = create_england_sars_counts(sac_sars, number_of_las_with_sars)
    sac_sars = pd.concat([sac_sars_england, sac_sars_region], axis=0)
    sac_sars = apply_sars_rounding_and_suppression(sac_sars)
    sac_sars.loc[
        sac_sars["Measure"] == "Number of LAs supplying data", "Value"
    ] = params["number_of_las"]
    return sac_sars.to_csv(params["pbi_sars_output_location"], index=False)