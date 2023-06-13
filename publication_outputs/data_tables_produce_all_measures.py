from data_tables_read_in_data import *


def pivot_data(df, table_refs, enquiry_type, piv_on):
    df = df[df["TABLE_REFERENCE"].isin(table_refs)]
    df = df[df["ENQUIRY_TYPE"].isin(enquiry_type)]
    return df.pivot_table(
        values="VALUE",
        index=[
            "GEOGRAPHY",
            "ONS_CODE",
            "LA_CODE",
            "LA_NAME",
            "REGION_CODE",
            "REGION_NAME",
            "COUNCIL_TYPE",
            "18-64",
            "65-74",
            "75-84",
            "85+",
            "Total adult population",
        ],
        columns=piv_on,
        aggfunc=np.sum,
    )


def rates_per_100K(df, numerator, denominator):
    return (df[numerator] / df[denominator]) * 100000


def create_geography_breakdown(df, groupby_col):
    return df.groupby(groupby_col).sum(numeric_only=False).reset_index()


def add_columns(df, ons_code, cassr_code, cassr_name, ct_region):
    df["ONS area code"] = ons_code
    df["CASSR Code"] = cassr_code
    df["CASSR Name"] = cassr_name
    df["Council Type / Region Name"] = ct_region
    return df


def reorder_columns(df):
    first_cols = [
        "ONS area code",
        "CASSR Code",
        "CASSR Name",
        "Council Type / Region Name",
    ]
    last_cols = [col for col in df.columns if col not in first_cols]
    return df[first_cols + last_cols].reset_index()


def my_round5(n):
    lower = (n // 5) * 5
    upper = lower + 5
    if (n - lower) < (upper - n):
        return int(lower)
    return int(upper)


def produce_all_table_measures(sac_df):
    sac_tables = sac_df[
        [
            "GEOGRAPHY",
            "ONS_CODE",
            "LA_CODE",
            "LA_NAME",
            "REGION_CODE",
            "REGION_NAME",
            "COUNCIL_TYPE",
            "18-64",
            "65-74",
            "75-84",
            "85+",
            "Total adult population",
            "TABLE_REFERENCE",
            "ENQUIRY_TYPE",
            "CATEGORY",
            "SUBCATEGORY",
            "COLUMN_NAME",
            "ROW_NAME",
            "VALUE",
        ]
    ]
    piv_on_cols = pivot_data(
        sac_tables,
        ["SG1f", "SG2a", "SG2b", "SG2c", "SG2e", "SG3a", "SG4a", "SG5a"],
        [
            "Concluded Section 42 Enquiries",
            "Safeguarding Concerns",
            "Section 42 Enquiries",
            "Other Enquiries",
            "Count of Safeguarding Adult Reviews",
        ],
        "COLUMN_NAME",
    )
    piv_on_cols = piv_on_cols.reset_index()
    piv_on_rows = pivot_data(
        sac_tables,
        ["SG2b", "SG1a", "SG1b", "SG1c", "SG1d", "SG1e"],
        ["Concluded Section 42 Enquiries", "Section 42 Enquiries"],
        "ROW_NAME",
    )
    all_measures = pd.merge(
        piv_on_cols, piv_on_rows, left_on="LA_CODE", right_on="LA_CODE", how="left"
    )
    return all_measures


def format_england_breakdown(all_measures):
    england_measures = create_geography_breakdown(all_measures, "GEOGRAPHY")
    england_measures = add_columns(
        england_measures, "E92000001", "-", "-", england_measures["GEOGRAPHY"]
    )
    england_measures = reorder_columns(england_measures)
    return england_measures


def format_council_type_breakdown(all_measures):
    council_type_measures = create_geography_breakdown(all_measures, "COUNCIL_TYPE")
    council_type_measures = add_columns(
        council_type_measures, "-", "-", "-", council_type_measures["COUNCIL_TYPE"]
    )
    council_type_measures = reorder_columns(council_type_measures)
    return council_type_measures


def format_region_breakdown(all_measures):
    region_measures = create_geography_breakdown(
        all_measures, ["REGION_CODE", "REGION_NAME"]
    )
    region_measures = add_columns(
        region_measures,
        region_measures["REGION_CODE"],
        "-",
        "-",
        region_measures["REGION_NAME"],
    )
    region_measures = reorder_columns(region_measures)
    return region_measures


def format_local_authority_breakdown(all_measures):
    la_measures = create_geography_breakdown(
        all_measures, ["ONS_CODE", "LA_CODE", "LA_NAME", "REGION_NAME"]
    )
    la_measures = add_columns(
        la_measures,
        la_measures["ONS_CODE"],
        la_measures["LA_CODE"],
        la_measures["LA_NAME"],
        la_measures["REGION_NAME"],
    )
    la_measures = reorder_columns(la_measures)
    la_measures = la_measures.sort_values("CASSR Code")
    return la_measures


def append_all_breakdowns(
    england_measures, council_type_measures, region_measures, la_measures
):
    sac_unrounded = pd.concat(
        [england_measures, council_type_measures, region_measures, la_measures], axis=0
    )
    sac_unrounded = sac_unrounded.drop(
        [
            "index",
            "GEOGRAPHY",
            "ONS_CODE",
            "LA_CODE",
            "LA_NAME",
            "REGION_CODE",
            "REGION_NAME",
            "COUNCIL_TYPE",
        ],
        axis=1,
    )
    sac_unrounded["GEOGRAPHY"] = "ENGLAND"
    return sac_unrounded


def add_additional_measures(sac_unrounded):
    sac_unrounded["FY Key"] = params["year_key"]
    sac_unrounded["Year"] = params["reporting_year"]
    sac_unrounded["SG1a 85+"] = sac_unrounded["SG1a 85-94"] + sac_unrounded["SG1a 95+"]
    sac_unrounded["Total Enquiries"] = (
        sac_unrounded["SG1f Total Number of Section 42 Safeguarding Enquiries"]
        + sac_unrounded["SG1f Total Number of Other Safeguarding Enquiries"]
    )
    sac_unrounded["Proportion S42"] = (
        sac_unrounded["SG1f Total Number of Section 42 Safeguarding Enquiries"]
        / sac_unrounded["Total Enquiries"]
    ) * 100
    sac_unrounded["Conversion Rate"] = (
        sac_unrounded["Total Enquiries"]
        / sac_unrounded["SG1f Total Number of Safeguarding Concerns"]
    ) * 100
    sac_unrounded["Total Concluded Enquiries"] = (
        sac_unrounded["SG3a Yes, they lacked capacity"]
        + sac_unrounded["SG3a No, they did not lack capacity"]
        + sac_unrounded["SG3a Not recorded"]
        + sac_unrounded["SG3a Don't know"]
    )
    return sac_unrounded


def add_england_proportions(sac_df, sac_unrounded):
    england_proportions = (
        sac_df[["GEOGRAPHY", "eprop_18_64", "eprop_65_74", "eprop_75_84", "eprop_85+"]]
    ).head(1)
    return pd.merge(sac_unrounded, england_proportions, on="GEOGRAPHY", how="left")


def calculate_all_rates_per_100k(sac_unrounded):
    sac_unrounded["18-64 rate"] = rates_per_100K(sac_unrounded, "SG1a 18-64", "18-64")
    sac_unrounded["65-74 rate"] = rates_per_100K(sac_unrounded, "SG1a 65-74", "65-74")
    sac_unrounded["75-84 rate"] = rates_per_100K(sac_unrounded, "SG1a 75-84", "75-84")
    sac_unrounded["85+ rate"] = rates_per_100K(sac_unrounded, "SG1a 85+", "85+")
    sac_unrounded["Concerns per 100K"] = rates_per_100K(
        sac_unrounded,
        "SG1f Total Number of Safeguarding Concerns",
        "Total adult population",
    )
    sac_unrounded["Section 42 per 100K"] = rates_per_100K(
        sac_unrounded,
        "SG1f Total Number of Section 42 Safeguarding Enquiries",
        "Total adult population",
    )
    sac_unrounded["Other Enquiries per 100K"] = rates_per_100K(
        sac_unrounded,
        "SG1f Total Number of Other Safeguarding Enquiries",
        "Total adult population",
    )
    sac_unrounded["Total Enquiries per 100K"] = rates_per_100K(
        sac_unrounded, "Total Enquiries", "Total adult population"
    )
    return sac_unrounded


def calculate_age_standardised_rate(sac_unrounded):
    sac_unrounded["Age standardised rate"] = (
        (sac_unrounded["18-64 rate"] * sac_unrounded["eprop_18_64"])
        + (sac_unrounded["65-74 rate"] * sac_unrounded["eprop_65_74"])
        + (sac_unrounded["75-84 rate"] * sac_unrounded["eprop_75_84"])
        + (sac_unrounded["85+ rate"] * sac_unrounded["eprop_85+"])
    )
    return sac_unrounded


def produce_sac_unrounded():
    sac_df = read_in_data()
    all_measures = produce_all_table_measures(sac_df)
    england_measures = format_england_breakdown(all_measures)
    council_type_measures = format_council_type_breakdown(all_measures)
    region_measures = format_region_breakdown(all_measures)
    la_measures = format_local_authority_breakdown(all_measures)
    sac_unrounded = append_all_breakdowns(
        england_measures, council_type_measures, region_measures, la_measures
    )
    sac_unrounded = add_additional_measures(sac_unrounded)
    sac_unrounded = add_england_proportions(sac_df, sac_unrounded)
    sac_unrounded = calculate_all_rates_per_100k(sac_unrounded)
    sac_unrounded = calculate_age_standardised_rate(sac_unrounded)
    return sac_unrounded


def export_unrounded_csv(sac_unrounded):
    return sac_unrounded.to_csv(params["unrounded_csv_output_location"], index=False)

