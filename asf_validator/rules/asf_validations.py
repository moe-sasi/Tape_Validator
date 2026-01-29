# Source: Existing asf_validations.py

import pandas as pd
import numpy as np
import pdb # For debugging purposes

# Originator Doc Code
def validate_originator_doc_code(originator_doc_code):
    """
    Returns True if the Originator Doc Code is missing (blank), indicating a validation error.
    """
    return originator_doc_code == ""

# Originator DTI
def validate_originator_dti(originator_dti):
    """
    Returns True if the Originator DTI is blank, less than or equal to 0, or greater than 0.6 — all considered invalid.
    """
    return originator_dti == "" or originator_dti <= 0 or originator_dti > 0.6

# Bankruptcy flag
def validate_months_bankruptcy(months_bankruptcy):
    """
    Returns True if Months Bankruptcy is populated (non-blank).
    """
    return (months_bankruptcy != "") and (not pd.isna(months_bankruptcy))

# Primary Borrower FICO
def validate_original_primary_borrower_fico(original_primary_borrower_fico):
    """
    Returns True if FICO is blank, zero, below 350, or above 950.
    """
    try:
        fico = float(original_primary_borrower_fico)
        return fico == 0 or fico < 350 or fico > 950
    except:
        return True

# Flag if borrower's FICO score is less than or equal to 660
def validate_borrower_fico_at_or_below_660(borrower_fico_score):
    """
    Returns True if FICO is less than or equal to 660.
    """
    try:
        return borrower_fico_score <= 660
    except:
        return True


# Buydowns
def validate_buy_down_period(buy_down_period):
    """
    Returns True if Buy Down Period is a non-zero value (numeric or string).
    """

    # return buy_down_period != 0 and str(buy_down_period) != "0"
    return buy_down_period > 0

# Cash-out amount
def validate_cash_out_amount(cash_out_amount, loan_purpose, original_loan_amount):
    """
    Returns True if:
    - Cash Out Amount is 0 or blank AND Loan Purpose is in [1,2,3,4], OR
    - Cash Out Amount > 1% of Original Loan Amount AND Loan Purpose is NOT in [1,2,3,4].
    """
    try:
        zero = cash_out_amount in [0, "", None]
        in_group = loan_purpose in [1, 2, 3, 4]
        big = abs(float(cash_out_amount)) > abs(float(original_loan_amount)) * 0.01
        not_in_group = loan_purpose not in [1, 2, 3, 4]
        return (zero and in_group) or (big and not_in_group)
    except:
        return True

# Channel Check
def validate_channel(channel):
    """
    Returns True if Channel is not 1, 2, or 5 (as number or string).
    """
    return str(channel) not in {"1", "2", "5"}

# City
def validate_city(city):
    """
    Returns True if City is blank.
    """
    return city == ""

# 9. CLTV < LTV
def validate_cltv_less_than_ltv(original_cltv, original_ltv):
    """
    Returns True if CLTV is blank or less than LTV.
    """
    try:
        return original_cltv == "" or round(float(original_cltv), 4) < round(float(original_ltv), 4)
    except:
        return True
        
# 10. CLTV Components
def validate_cltv_components(
    original_loan_amount,
    junior_mortgage_balance,
    sales_price,
    original_appraised_property_value,
    original_cltv,
    lien_position
):
    """
    Returns True if CLTV is not consistent with components.
    Computed CLTV = (Loan + Junior Lien) / lesser of Sales Price or Appraised Value
    """
    try:
        jm = 0 if junior_mortgage_balance in ["", None] else float(junior_mortgage_balance)
        numerator = float(original_loan_amount) + jm

        sp = float(sales_price) if sales_price not in ["", 0, None] else None
        apv = float(original_appraised_property_value)
        denominator = min(sp, apv) if sp else apv

        computed_cltv = round(numerator / denominator, 4)
        reported_cltv = round(float(original_cltv), 5)

        return abs(computed_cltv - reported_cltv) > 0.0001
    except:
        return True

# 11. Co-Borrower Other Income
# Flag if Co-Borrower Other Income is blank when there are 2 or more borrowers
def validate_co_borrower_other_income(co_borrower_other_income, total_number_of_borrowers):
    """
    Returns True if Co-Borrower Other Income is blank while there are 2 or more borrowers.
    """
    return co_borrower_other_income == "" and total_number_of_borrowers >= 2

# df["flag_co_borrower_other_income"] = df.apply(lambda row: validate_co_borrower_other_income(row["Co-Borrower Other Income"], row["Total Number of Borrowers"]), axis=1)

# 12. Current Interest Rate
# Flag if Amortization Type is 1 and the Current Interest Rate is either different from Original, blank, or zero
def validate_current_interest_rate(amortization_type, original_interest_rate, current_interest_rate):
    """
    Returns True if Amortization Type is 1 and Current Interest Rate is blank, 0, or differs from Original Interest Rate.
    """
    try:
        return amortization_type == 1 and (
            current_interest_rate == "" or current_interest_rate == 0 or current_interest_rate != original_interest_rate
        )
    except:
        return True

# df["flag_current_interest_rate"] = df.apply(lambda row: validate_current_interest_rate(row["Amortization Type"], row["Original Interest Rate"], row["Current Interest Rate"]), axis=1)

# 13. Original Interest Rate
# Flag if Original Interest Rate is blank or zero, or exceeds lifetime ceiling for certain Amortization Types
def validate_original_interest_rate(original_interest_rate, lifetime_max_rate_ceiling, amortization_type):
    """
    Returns True if:
    - Original Interest Rate is blank or 0, OR
    - Original Interest Rate > Lifetime Max Rate and Amortization Type is 2.
    """
    try:
        if pd.isna(original_interest_rate) or original_interest_rate in ["", 0, None]:
            return True
        return float(original_interest_rate) > float(lifetime_max_rate_ceiling) and int(amortization_type) == 2
    except:
        return True
# df["flag_original_interest_rate"] = df.apply(lambda row: validate_original_interest_rate(row["Original Interest Rate"], row["Lifetime Maximum Rate (Ceiling)"], row["Amortization Type"]), axis=1)

# 14. Primary Servicer
# Flag if Primary Servicer is blank
def validate_primary_servicer(primary_servicer):
    """
    Returns True if Primary Servicer is missing (blank).
    """
    return primary_servicer == ""

# df["flag_primary_servicer"] = df["Primary Servicer"].apply(validate_primary_servicer)

# 16. DTI Consistency
# Flag if DTI differs significantly from calculated monthly debt / income ratio
def validate_dti_consistency(originator_dti, monthly_debt_all_borrowers, all_borrower_total_income):
    """
    Returns True if the reported DTI differs from the calculated DTI (monthly debt / total income) by more than 0.00006.
    """
    try:
        calculated_dti = round(monthly_debt_all_borrowers / all_borrower_total_income, 4)
        return abs(originator_dti - calculated_dti) > 0.00006
    except:
        return True

# df["flag_dti_consistency"] = df.apply(lambda row: validate_dti_consistency(row["Originator DTI"], row["Monthly Debt All Borrowers"], row["All Borrower Total Income"]), axis=1)

# 17. Escrow Indicator
# Flag if Escrow Indicator is blank
def validate_escrow_indicator(escrow_indicator):
    """
    Returns True if Escrow Indicator is missing (blank).
    """
    return escrow_indicator == ""

# df["flag_escrow_indicator"] = df["Escrow Indicator"].apply(validate_escrow_indicator)

# 18. FICO Model Used
# Flag if FICO Model Used is blank
def validate_fico_model_used(fico_model_used):
    """
    Returns True if FICO Model Used is missing (blank).
    """
    return fico_model_used == ""

# df["flag_fico_model_used"] = df["FICO Model Used"].apply(validate_fico_model_used)

# 19. First Adj Cap
# Flag if Initial Interest Rate Cap is missing while Amortization Type equals 2 (adjustable rate)
def validate_first_adj_cap(initial_interest_rate_cap_change_up, amortization_type):
    """
    Returns True if Initial Interest Rate Cap (Change Up) is blank and Amortization Type is 2.
    """
    return initial_interest_rate_cap_change_up == "" and amortization_type == 2

# df["flag_first_adj_cap"] = df.apply(lambda row: validate_first_adj_cap(row["Initial Interest Rate Cap (Change Up)"], row["Amortization Type"]), axis=1)

# 20. First Payment Date 
# Flag if First Payment Date is blank, before Origination Date, or not on the 1st day of the month
def validate_first_payment_date(first_payment_date_of_loan, origination_date):
    """
    Returns True if:
    - First Payment Date is blank,
    - Origination Date is after First Payment Date,
    - or First Payment Date does not fall on the 1st day of the month.
    """
    try:
        return (
            first_payment_date_of_loan == "" or
            origination_date > first_payment_date_of_loan or
            first_payment_date_of_loan.day != 1
        )
    except:
        return True

# df["flag_first_payment_date"] = df.apply(lambda row: validate_first_payment_date(row["First Payment Date of Loan"], row["Origination Date"]), axis=1)

# 21. Foreclosure Flag
# Flag if Months Foreclosure is not blank
def validate_months_foreclosure(months_foreclosure):
    """
    Returns True if Months Foreclosure is populated (i.e., not blank).
    """
    return (months_foreclosure != "") and (not pd.isna(months_foreclosure))

# df["flag_months_foreclosure"] = df["Months Foreclosure"].apply(validate_months_foreclosure)

# 22. Index Type
# Flag if Index Type is blank while Amortization Type is 2 (ARM)
def validate_index_type(index_type, amortization_type):
    """
    Returns True if Index Type is blank and Amortization Type is 2 (adjustable).
    """
    return index_type == "" and amortization_type == 2

# df["flag_index_type"] = df.apply(lambda row: validate_index_type(row["Index Type"], row["Amortization Type"]), axis=1)

# 23. Length of Employment: Borrower
# Flag if Borrower has no employment length value when required by employment verification and not self-employed
def validate_length_employment_borrower(length_of_employment_borrower, borrower_employment_verification, self_employment_flag):
    """
    Returns True if:
    - Employment length is blank or 0,
    - AND Employment verification level is 3,
    - AND borrower is not self-employed.
    """
    return (
        length_of_employment_borrower in ["", 0, None] and
        borrower_employment_verification == 3 and
        self_employment_flag == 0
    )

# df["flag_length_employment_borrower"] = df.apply(lambda row: validate_length_employment_borrower(row["Length of Employment: Borrower"], row["Borrower Employment Verification"], row["Self-employment Flag"]), axis=1)

# 24. Length of Employment: Co-Borrower
# Flag if Co-Borrower employment info is missing when required by employment verification and not self-employed
def validate_length_employment_co_borrower(length_of_employment_co_borrower, total_number_of_borrowers, self_employment_flag, co_borrower_employment_verification):
    """
    Returns True if:
    - Co-Borrower employment length is blank,
    - AND number of borrowers > 1,
    - AND not self-employed,
    - AND Co-Borrower employment verification = 3.
    """
    try:
        return (
            length_of_employment_co_borrower == "" and
            float(total_number_of_borrowers) > 1 and
            self_employment_flag == 0 and
            co_borrower_employment_verification == 3
        )
    except:
        return True

# df["flag_length_employment_co_borrower"] = df.apply(lambda row: validate_length_employment_co_borrower(row["Length of Employment: Co-Borrower"], row["Total Number of Borrowers"], row["Self-employment Flag"], row["Co-Borrower Employment Verification"]), axis=1)


# 25. Lien Status
# Flag if Lien Position is not 1 or 2
def validate_lien_position(lien_position):
    """
    Returns True if Lien Position is not 1 or 2.
    """
    try:
        return int(lien_position) not in [1, 2]
    except:
        return True

# df["flag_lien_position"] = df["Lien Position"].apply(validate_lien_position)

# 26. Lifetime Maximum Rate (Ceiling)
# Flag if Lifetime Maximum Rate is blank when Amortization Type is 2 (ARM)
def validate_lifetime_max_rate_ceiling(lifetime_max_rate_ceiling, amortization_type):
    """
    Returns True if Lifetime Maximum Rate (Ceiling) is blank and Amortization Type is 2.
    """
    return lifetime_max_rate_ceiling == "" and amortization_type == 2

# df["flag_lifetime_max_rate_ceiling"] = df.apply(lambda row: validate_lifetime_max_rate_ceiling(row["Lifetime Maximum Rate (Ceiling)"], row["Amortization Type"]), axis=1)

# 27. Lifetime Minimum Rate (Floor)
# Flag if Lifetime Floor is blank, zero, or less than Margin when Amortization Type is 2
def validate_lifetime_min_rate_floor(gross_margin, lifetime_min_rate_floor, amortization_type):
    """
    Returns True if:
    - Amortization Type is 2, AND
    - Lifetime Minimum Rate is blank, 0, or less than the Gross Margin.
    """
    try:
        return amortization_type == 2 and (
            lifetime_min_rate_floor in ["", 0, None] or
            float(gross_margin) > float(lifetime_min_rate_floor)
        )
    except:
        return True

# df["flag_lifetime_min_rate_floor"] = df.apply(lambda row: validate_lifetime_min_rate_floor(row["Gross Margin"], row["Lifetime Minimum Rate (Floor)"], row["Amortization Type"]), axis=1)

# 28. Missing Loan Purpose
# Flag if Loan Purpose is blank
def validate_loan_purpose(loan_purpose):
    """
    Returns True if Loan Purpose is missing (blank).
    """
    return loan_purpose == ""

# df["flag_loan_purpose"] = df["Loan Purpose"].apply(validate_loan_purpose)

# 29. Missing Sales Price (for HELOC)
# Flag if HELOC Indicator = 7 and Sales Price is blank or zero
def validate_sales_price_for_heloc(heloc_indicator, sales_price):
    """
    Returns True if HELOC Indicator is 7 and Sales Price is blank or zero.
    """
    return heloc_indicator == 7 and sales_price in ["", 0, None]

# df["flag_sales_price_for_heloc"] = df.apply(lambda row: validate_sales_price_for_heloc(row["HELOC Indicator"], row["Sales Price"]), axis=1)


# 25. Lien Status
# Flag if Lien Position is not 1 or 2
def validate_lien_position_v2(lien_position):
    """
    Returns True if Lien Position is not 1 or 2.
    """
    try:
        return int(lien_position) not in [1, 2]
    except:
        return True

# df["flag_lien_position"] = df["Lien Position"].apply(validate_lien_position)

# 26. Lifetime Maximum Rate (Ceiling)
# Flag if Lifetime Maximum Rate is blank when Amortization Type is 2 (ARM)
def validate_lifetime_max_rate_ceiling_v2(lifetime_max_rate_ceiling, amortization_type):
    """
    Returns True if Lifetime Maximum Rate (Ceiling) is blank and Amortization Type is 2.
    """
    return lifetime_max_rate_ceiling == "" and amortization_type == 2

# df["flag_lifetime_max_rate_ceiling"] = df.apply(lambda row: validate_lifetime_max_rate_ceiling(row["Lifetime Maximum Rate (Ceiling)"], row["Amortization Type"]), axis=1)

# 27. Lifetime Minimum Rate (Floor)
# Flag if Lifetime Floor is blank, zero, or less than Margin when Amortization Type is 2
def validate_lifetime_min_rate_floor_v2(gross_margin, lifetime_min_rate_floor, amortization_type):
    """
    Returns True if:
    - Amortization Type is 2, AND
    - Lifetime Minimum Rate is blank, 0, or less than the Gross Margin.
    """
    try:
        return amortization_type == 2 and (
            lifetime_min_rate_floor in ["", 0, None] or
            float(gross_margin) > float(lifetime_min_rate_floor)
        )
    except:
        return True

# df["flag_lifetime_min_rate_floor"] = df.apply(lambda row: validate_lifetime_min_rate_floor(row["Gross Margin"], row["Lifetime Minimum Rate (Floor)"], row["Amortization Type"]), axis=1)

# 28. Missing Loan Purpose
# Flag if Loan Purpose is blank
def validate_loan_purpose_v2(loan_purpose):
    """
    Returns True if Loan Purpose is missing (blank).
    """
    return loan_purpose == ""

# df["flag_loan_purpose"] = df["Loan Purpose"].apply(validate_loan_purpose)

# 29. Missing Sales Price (for HELOC)
# Flag if HELOC Indicator = 7 and Sales Price is blank or zero
def validate_sales_price_for_heloc_v2(heloc_indicator, sales_price):
    """
    Returns True if HELOC Indicator is 7 and Sales Price is blank or zero.
    """
    return heloc_indicator == 7 and sales_price in ["", 0, None]

# df["flag_sales_price_for_heloc"] = df.apply(lambda row: validate_sales_price_for_heloc(row["HELOC Indicator"], row["Sales Price"]), axis=1)


# 35. Monthly Debt All Borrowers
# Flag if Monthly Debt is missing or zero
def validate_monthly_debt_all_borrowers(monthly_debt_all_borrowers):
    """
    Returns True if Monthly Debt All Borrowers is blank or zero.
    """
    return monthly_debt_all_borrowers in ["", 0, None]

# df["flag_monthly_debt_all_borrowers"] = df["Monthly Debt All Borrowers"].apply(validate_monthly_debt_all_borrowers)

# 36. Mortgage Insurance Company Name
# Flag if Mortgage Insurance Company Name is not 0
def validate_mi_company_name(mortgage_insurance_company_name):
    """
    Returns True if Mortgage Insurance Company Name is anything other than "".
    """
    try:
        # return mortgage_insurance_company_name not in ["", "0", 0]
        return ~np.isnan(mortgage_insurance_company_name)
    except:
        return True

# df["flag_mi_company_name"] = df["Mortgage Insurance Company Name"].apply(validate_mi_company_name)

# 37. Mortgage Insurance Percent
# Flag if Mortgage Insurance Percent is blank
def validate_mi_percent(mortgage_insurance_percent):
    """
    Returns True if Mortgage Insurance Percent is blank.
    """
    return mortgage_insurance_percent == ""

# df["flag_mi_percent"] = df["Mortgage Insurance Percent"].apply(validate_mi_percent)

# 38. Number of Mortgaged Properties
# Flag if Number of Mortgaged Properties is blank or less than 1
def validate_number_of_mortgaged_properties(number_of_mortgaged_properties, loan_purpose):
    """
    Returns True if Number of Mortgaged Properties is blank or less than 1 or loan purpose is a first time home purchase (6) and number of mortgaged properties is greater than 1.
    """
    try:
        return number_of_mortgaged_properties in ["", None] or float(number_of_mortgaged_properties) < 1 or (loan_purpose == 6 and number_of_mortgaged_properties > 1 )
    except:
        return True

# df["flag_number_of_mortgaged_properties"] = df["Number of Mortgaged Properties"].apply(validate_number_of_mortgaged_properties)

# 39. Occupancy
# Flag if Occupancy field is blank
def validate_occupancy(occupancy):
    """
    Returns True if Occupancy is missing (blank).
    """
    return occupancy == ""

# df["flag_occupancy"] = df["Occupancy"].apply(validate_occupancy)

# 40. Original Appraised Property Value
# Flag if Original Appraised Property Value is missing or less than Current Loan Amount
def validate_original_appraised_property_value(original_appraised_property_value, current_loan_amount):
    """
    Returns True if Original Appraised Property Value is blank or less than Current Loan Amount.
    """
    try:
        return original_appraised_property_value == "" or float(original_appraised_property_value) < float(current_loan_amount)
    except:
        return True

# df["flag_original_appraised_value"] = df.apply(lambda row: validate_original_appraised_property_value(row["Original Appraised Property Value"], row["Current Loan Amount"]), axis=1)

# 41. Original Balance
# Flag if Original Loan Amount is blank or zero
def validate_original_loan_amount(original_loan_amount):
    """
    Returns True if Original Loan Amount is blank or zero.
    """
    return original_loan_amount in ["", 0, None]

# 41a. Original Loan Amount Range
# Flag if Original Loan Amount is < 10,000 or > 10,000,000
def validate_original_loan_amount_out_of_range(original_loan_amount):
    """
    Returns True if Original Loan Amount is below 10,000 or above 10,000,000.
    """
    try:
        return float(original_loan_amount) < 10000 or float(original_loan_amount) > 10000000
    except:
        return True

# df["flag_original_loan_amount"] = df["Original Loan Amount"].apply(validate_original_loan_amount)

# 42. Original LTV
# Flag if computed LTV doesn't match reported value or exceeds 100%, or if it's blank/zero
def validate_original_ltv(original_loan_amount, sales_price, original_appraised_property_value, original_ltv):
    """
    Returns True if:
    - Reported LTV is blank or zero,
    - Reported LTV exceeds 100%,
    - OR if calculated LTV differs from reported by more than 0.001.
    """
    try:
        sp = float(sales_price) if sales_price not in ["", 0, None] else None
        apv = float(original_appraised_property_value)
        denominator = min(sp, apv) if sp else apv
        calculated_ltv = round(float(original_loan_amount) / denominator, 4)
        return (
            original_ltv in ["", 0, None] or
            float(original_ltv) / 100 > 1 or
            abs(calculated_ltv - round(float(original_ltv), 4)) > 0.001
        )
    except:
        return True

# df["flag_original_ltv"] = df.apply(lambda row: validate_original_ltv(row["Original Loan Amount"], row["Sales Price"], row["Original Appraised Property Value"], row["Original LTV"]), axis=1)

# 43. Original Property Valuation Date is Missing
# Flag if Original Property Valuation Date is blank
def validate_original_property_valuation_date(original_property_valuation_date):
    """
    Returns True if Original Property Valuation Date is blank.
    """
    return pd.isna(original_property_valuation_date) or  (original_property_valuation_date in ("", None))

# df["flag_original_property_valuation_date"] = df["Original Property Valuation Date"].apply(validate_original_property_valuation_date)

# 44. 180 Days Between Valuation and Origination
# Flag if more than 180 days between Original Property Valuation Date and Origination Date
def validate_valuation_age(original_property_valuation_date, origination_date):
    """
    Returns True if there are 180 or more days between Valuation Date and Origination Date.
    """
    try:
        return (origination_date - original_property_valuation_date).days >= 180
    except:
        return True

# df["flag_valuation_age"] = df.apply(lambda row: validate_valuation_age(row["Original Property Valuation Date"], row["Origination Date"]), axis=1)


# 45. Property Valuation After Origination
# Flag if Property Valuation Date is after Origination Date
def validate_valuation_after_origination(original_property_valuation_date, origination_date):
    """
    Returns True if the Original Property Valuation Date occurs after the Origination Date.
    """
    try:
        return original_property_valuation_date > origination_date
    except:
        return True

# df["flag_valuation_after_origination"] = df.apply(lambda row: validate_valuation_after_origination(row["Original Property Valuation Date"], row["Origination Date"]), axis=1)

# 46. Original Property Valuation Type
# Flag if Original Property Valuation Type is missing
def validate_original_property_valuation_type(original_property_valuation_type):
    """
    Returns True if Original Property Valuation Type is blank.
    """
    return  pd.isna(original_property_valuation_type) or  (original_property_valuation_type == "")

# df["flag_original_property_valuation_type"] = df["Original Property Valuation Type"].apply(validate_original_property_valuation_type)

# 46a. Original Appraisal 24+ months old
# Flag if Original Property Valuation Date is 24 months or older than Interest Paid Through Date
def validate_original_appraisal_24_months_old(
    original_property_valuation_date,
    interest_paid_through_date,
):
    """
    Returns True if Original Property Valuation Date is 24 months or older than Interest Paid Through Date.
    """
    try:
        if pd.isna(original_property_valuation_date) or pd.isna(interest_paid_through_date):
            return True
        valuation_date = pd.to_datetime(original_property_valuation_date)
        paid_through_date = pd.to_datetime(interest_paid_through_date)
        cutoff_date = paid_through_date - pd.DateOffset(months=24)
        return valuation_date <= cutoff_date
    except:
        return True

# 47. Original Term to Maturity
# Flag if Original Term to Maturity is out of bounds, missing, zero, or not equal to Original Amortization Term
def validate_original_term_to_maturity_vs_amortization(original_term_to_maturity, original_amortization_term):
    """
    Returns True if:
    - Original Term is <120 or >480 months,
    - OR blank/zero,
    - OR not equal to the Original Amortization Term.
    """
    try:
        return (
            original_term_to_maturity in ["", 0, None] or
            original_term_to_maturity < 120 or
            original_term_to_maturity > 480 or
            original_term_to_maturity != original_amortization_term
        )
    except:
        return True

# df["flag_term_to_maturity"] = df.apply(lambda row: validate_original_term_to_maturity_vs_amortization(row["Original Term to Maturity"], row["Original Amortization Term"]), axis=1)

# 48. Origination Date
# Flag if Origination Date is zero
def validate_origination_date(origination_date):
    """
    Returns True if Origination Date is zero.
    """
    return origination_date == 0

# df["flag_origination_date"] = df["Origination Date"].apply(validate_origination_date)

# 49. Originator
# Flag if Originator field is blank
def validate_originator(originator):
    """
    Returns True if Originator is blank.
    """
    return originator == ""

# df["flag_originator"] = df["Originator"].apply(validate_originator)

# # 50. Property Valuation After Origination
# # Flag if Property Valuation Date is after Origination Date
# def validate_valuation_after_origination(original_property_valuation_date, origination_date):
#     """
#     Returns True if the Original Property Valuation Date occurs after the Origination Date.
#     """
#     try:
#         return original_property_valuation_date > origination_date
#     except:
#         return True

# df["flag_valuation_after_origination"] = df.apply(lambda row: validate_valuation_after_origination(row["Original Property Valuation Date"], row["Origination Date"]), axis=1)

# # 51. Original Property Valuation Type
# # Flag if Original Property Valuation Type is missing
# def validate_original_property_valuation_type(original_property_valuation_type):
#     """
#     Returns True if Original Property Valuation Type is blank.
#     """
#     return original_property_valuation_type == ""

# df["flag_original_property_valuation_type"] = df["Original Property Valuation Type"].apply(validate_original_property_valuation_type)

# 52. Original Term
# Flag if Original Term to Maturity is invalid or inconsistent with Original Amortization Term
def validate_original_term(original_term_to_maturity, original_amortization_term):
    """
    Returns True if:
    - Original Term is <120 or >480 months,
    - OR blank/zero,
    - OR not equal to the Original Amortization Term.
    """
    try:
        return (
            original_term_to_maturity in ["", 0, None] or
            original_term_to_maturity < 120 or
            original_term_to_maturity > 480 or
            original_term_to_maturity != original_amortization_term
        )
    except:
        return True

# df["flag_original_term"] = df.apply(lambda row: validate_original_term(row["Original Term to Maturity"], row["Original Amortization Term"]), axis=1)

# 53. Origination Date
# Flag if Origination Date is zero
def validate_origination_date_v2(origination_date):
    """
    Returns True if Origination Date is zero.
    """
    return origination_date == 0

# df["flag_origination_date"] = df["Origination Date"].apply(validate_origination_date)

# 54. Originator
# Flag if Originator field is blank
def validate_originator_v2(originator):
    """
    Returns True if Originator is blank.
    """
    return originator == ""

# df["flag_originator"] = df["Originator"].apply(validate_originator)

# 55. Payment String
# Flag if Current Payment Status is blank
def validate_current_payment_status(current_payment_status):
    """
    Returns True if Current Payment Status is blank.
    """
    return current_payment_status == ""

# df["flag_current_payment_status"] = df["Current Payment Status"].apply(validate_current_payment_status)

# 56. Percent of Down Payment
# Complex rule involving Loan Purpose and % Down Payment
def validate_percent_down_payment(percent_down_payment, loan_purpose):
    """
    Returns True if:
    - % Down Payment > 100 when Loan Purpose is 6 or 7,
    - OR % Down Payment > 0 when Loan Purpose is in [1,2,3,4,8,9],
    - OR % Down Payment is missing when Loan Purpose is 6 or 7.
    """
    try:
        if loan_purpose in [6, 7] and percent_down_payment == "":
            return True
        if loan_purpose in [6, 7] and float(percent_down_payment) > 100:
            return True
        if loan_purpose in [1, 2, 3, 4, 8, 9] and float(percent_down_payment) > 0:
            return True
        return False
    except:
        return True

# df["flag_percent_down_payment"] = df.apply(lambda row: validate_percent_down_payment(row["Percentage of Down Payment from Borrower Own Funds"], row["Loan Purpose"]), axis=1)

# 57. Periodic Cap
# Flag if Periodic Cap fields are missing or inconsistent based on Amortization Type
def validate_periodic_cap(amortization_type, cap_up, cap_down):
    """
    Returns True if:
    - Amortization Type is 2 and cap_up is blank or 0,
    - OR Amortization Type is 1 and cap_down is non-zero.
    """
    try:
        if amortization_type == 2 and pd.isna(cap_up):
            return True
        if amortization_type == 1 and not pd.isna(cap_down):
            return True
        return False
    except:
        return True

# df["flag_periodic_cap"] = df.apply(lambda row: validate_periodic_cap(row["Amortization Type"], row["Initial Interest Rate Cap (Change Up)"], row["Initial Interest Rate Cap (Change Down)"]), axis=1)

# 58. Pledge Amount
# Flag if pledged assets are missing or exceed 50% of appraised value
def validate_pledge_amount(original_pledged_assets, original_appraised_property_value):
    """
    Returns True if Original Pledged Assets is blank or > 50% of Appraised Value.
    """
    try:
        return (
            original_pledged_assets == "" or
            float(original_pledged_assets) > float(original_appraised_property_value) * 0.5
        )
    except:
        return True

# df["flag_pledge_amount"] = df.apply(lambda row: validate_pledge_amount(row["Original Pledged Assets"], row["Original Appraised Property Value"]), axis=1)

# 59. P&I
# Flag if Current Payment Amount Due is blank, 0, or off by >20% from expected P&I using PMT formula
import numpy_financial as npf

def pmt(rate, nper, pv):
    """
    PMT function similar to Excel: returns the fixed monthly payment.
    """
    try:
        return npf.pmt(rate, nper, pv)
    except:
        return None

def validate_principal_interest(current_payment_amount_due, current_interest_rate, original_amortization_term, original_loan_amount):
    """
    Returns True if P&I payment is blank, zero, or deviates >20% from expected based on interest rate and loan term.
    """
    try:
        expected = round(pmt(current_interest_rate / 12, original_amortization_term, -original_loan_amount), 2)
        actual = round(current_payment_amount_due, 2)
        return current_payment_amount_due in ["", 0, None] or abs(actual - expected) > expected * 0.2
    except:
        return True

# df["flag_principal_interest"] = df.apply(lambda row: validate_principal_interest(row["Current Payment Amount Due"], row["Current Interest Rate"], row["Original Amortization Term"], row["Original Loan Amount"]), axis=1)

# 60. Prepayment Penalty Calculation
# Flag if Prepayment Type is 1 and Calculation is blank or zero
def validate_prepayment_penalty_calc(prepayment_penalty_type, prepayment_penalty_calculation):
    """
    Returns True if Prepayment Penalty Type = 1 and Calculation is blank or 0.
    """
    return prepayment_penalty_type == 1 and prepayment_penalty_calculation in ["", 0, None]

# df["flag_prepayment_penalty_calc"] = df.apply(lambda row: validate_prepayment_penalty_calc(row["Prepayment Penalty Type"], row["Prepayment Penalty Calculation"]), axis=1)



# 61. Prepayment Penalty Type
# Flag if Prepayment Penalty Type is blank when Total Term is non-zero
def validate_prepayment_penalty_type(prepayment_penalty_type, prepayment_penalty_total_term):
    """
    Returns True if Prepayment Penalty Type is blank and Total Term is not blank or zero.
    """
    return prepayment_penalty_type == "" and prepayment_penalty_total_term not in ["", 0, None]

# df["flag_prepayment_penalty_type"] = df.apply(lambda row: validate_prepayment_penalty_type(row["Prepayment Penalty Type"], row["Prepayment Penalty Total Term"]), axis=1)

# 62. Prepayment Term
# Flag if Prepayment Term is missing or not in allowed set when Amortization Type is 2
def validate_prepayment_term(amortization_type, prepayment_penalty_total_term):
    """
    Returns True if Amortization Type is 2 and Prepayment Term is missing or not in {60,48,36,24,12,18}.
    """
    valid_terms = {60, 48, 36, 24, 12, 18}
    try:
        return amortization_type == 2 and (prepayment_penalty_total_term in ["", None] or int(prepayment_penalty_total_term) not in valid_terms)
    except:
        return True

# df["flag_prepayment_term"] = df.apply(lambda row: validate_prepayment_term(row["Amortization Type"], row["Prepayment Penalty Total Term"]), axis=1)

# 63. Primary Borrower Other Income
# Flag if Primary Borrower Other Income is blank
def validate_primary_borrower_other_income(primary_borrower_other_income):
    """
    Returns True if Primary Borrower Other Income is blank.
    """
    return primary_borrower_other_income == ""

# df["flag_primary_borrower_other_income"] = df["Primary Borrower Other Income"].apply(validate_primary_borrower_other_income)

# 64. Initial Period Cap
# Flag if either Initial Cap Up or Down is blank when Amortization Type is 2
def validate_initial_period_cap(amortization_type, cap_down, cap_up):
    """
    Returns True if Amortization Type is 2 and either cap field is blank.
    """
    return amortization_type == 2 and (cap_down == "" or cap_up == "")

# df["flag_initial_period_cap"] = df.apply(lambda row: validate_initial_period_cap(row["Amortization Type"], row["Initial Interest Rate Cap (Change Down)"], row["Initial Interest Rate Cap (Change Up)"]), axis=1)

# 65. Property Type
# Flag if Property Type is blank
def validate_property_type(property_type):
    """
    Returns True if Property Type is blank.
    """
    return property_type == ""

# df["flag_property_type"] = df["Property Type"].apply(validate_property_type)

# 66. Original Appraised Property Value
# Flag if Original Appraised Property Value is blank or zero
def validate_original_appraised_value(original_appraised_property_value):
    """
    Returns True if Original Appraised Property Value is blank or zero.
    """
    return original_appraised_property_value in ["", 0, None]

# df["flag_original_appraised_value"] = df["Original Appraised Property Value"].apply(validate_original_appraised_value)

# 67. Scheduled UPB
# Flag if Current Loan Amount is blank, zero, or exceeds Original Loan Amount
def validate_scheduled_upb(current_loan_amount, original_loan_amount):
    """
    Returns True if Current Loan Amount is blank/zero or greater than Original Loan Amount.
    """
    try:
        return current_loan_amount in ["", 0, None] or float(current_loan_amount) > float(original_loan_amount)
    except:
        return True

# df["flag_scheduled_upb"] = df.apply(lambda row: validate_scheduled_upb(row["Current Loan Amount"], row["Original Loan Amount"]), axis=1)

# 68. Purpose ID vs Sales Price
# Flag inconsistencies between Loan Purpose and Sales Price
def validate_purpose_id_vs_sales_price(loan_purpose, sales_price):
    """
    Returns True if:
    - Loan Purpose is 6 or 7 and Sales Price is missing/zero,
    - OR not 6 or 7 and Sales Price is present
    """
    try:
        
        lp = int(loan_purpose)
        sp_blank = (sales_price in ["", 0, None]) | (pd.isna(sales_price))
        sp_present = not sp_blank
        if lp in [6, 7] and sp_blank:
            return True
        if lp not in [6, 7] and sp_present:
            return True
        return False
    except:
        return True

# df["flag_purpose_id_vs_sales_price"] = df.apply(lambda row: validate_purpose_id_vs_sales_price(row["Loan Purpose"], row["Sales Price"], row["GQ"]), axis=1)

# 69. First Rate Adjustment Frequency
# Flag if Initial Fixed Rate Period is missing or not in allowed set for ARM
def validate_first_rate_adjustment_frequency(amortization_type, initial_fixed_rate_period):
    """
    Returns True if Amortization Type is 2 and Initial Fixed Rate Period is missing or not in allowed values.
    """
    valid_periods = {1, 6, 12, 24, 36, 60, 84, 120}
    try:
        return amortization_type == 2 and (initial_fixed_rate_period == "" or int(initial_fixed_rate_period) not in valid_periods)
    except:
        return True

# df["flag_first_rate_adjustment_frequency"] = df.apply(lambda row: validate_first_rate_adjustment_frequency(row["Amortization Type"], row["Initial Fixed Rate Period"]), axis=1)

# 70. Rounding Flag
# Flag if ARM Round Flag is blank for adjustable-rate loans
def validate_rounding_flag(amortization_type, arm_round_flag):
    """
    Returns True if Amortization Type is 2 and ARM Round Flag is blank.
    """
    return amortization_type == 2 and arm_round_flag == ""

# df["flag_rounding_flag"] = df.apply(lambda row: validate_rounding_flag(row["Amortization Type"], row["ARM Round Flag"]), axis=1)


# 71. Rounding Interval
# Flag if ARM Round Factor is blank for adjustable-rate loans
def validate_rounding_interval(amortization_type, arm_round_factor):
    """
    Returns True if Amortization Type is 2 and ARM Round Factor is blank.
    """
    return amortization_type == 2 and arm_round_factor == ""

# df["flag_rounding_interval"] = df.apply(lambda row: validate_rounding_interval(row["Amortization Type"], row["ARM Round Factor"]), axis=1)

# 72. Self Employed
# Flag if Self-employment Flag is missing or not 0/1
def validate_self_employed(self_employment_flag):
    """
    Returns True if Self-employment Flag is blank or not 0 or 1.
    """
    return self_employment_flag == "" or self_employment_flag not in [0, 1]

# df["flag_self_employed"] = df["Self-employment Flag"].apply(validate_self_employed)

# 73. Seller Loan Number
# Flag if Loan Number has 4 or fewer characters
def validate_seller_loan_number(loan_number):
    """
    Returns True if Loan Number has 4 or fewer characters.
    """
    try:
        return len(str(loan_number)) <= 4
    except:
        return True

# df["flag_seller_loan_number"] = df["Loan Number"].apply(validate_seller_loan_number)

# 74. Servicing Fee
# Flag if Servicing Fee % is missing, zero, or out of range (0.0005–0.005)
def validate_servicing_fee(servicing_fee):
    """
    Returns True if Servicing Fee % is blank, zero, or outside 0.0005–0.005 range.
    """
    try:
        return servicing_fee in ["", 0, None] or not (0.0005 <= float(servicing_fee) <= 0.005)
    except:
        return True

# df["flag_servicing_fee"] = df["Servicing Fee %"].apply(validate_servicing_fee)

# 75. State
# Flag if State is blank or not exactly two characters
def validate_state(state):
    """
    Returns True if State is blank or not two characters.
    """
    try:
        return state == "" or len(str(state)) != 2
    except:
        return True

# df["flag_state"] = df["State"].apply(validate_state)

# 76. Total Income
# Flag if sum of income components does not match All Borrower Total Income
def validate_total_income(pbw, cbw, pbo, cbo, abti):
    """
    Returns True if All Borrower Total Income does not match sum of wage and other incomes.
    """
    try:
        expected = sum(float(x or 0) for x in [pbw, cbw, pbo, cbo])
        return round(abs(expected - float(abti)), 0) > 0
    except:
        return True

# df["flag_total_income"] = df.apply(lambda row: validate_total_income(row["Primary Borrower Wage Income"], row["Co-Borrower Wage Income"], row["Primary Borrower Other Income"], row["Co-Borrower Other Income"], row["All Borrower Total Income"]), axis=1)

# 77. Total Number of Borrowers
# Flag if Total Number of Borrowers is missing or less than 1
def validate_total_number_of_borrowers(total_number_of_borrowers):
    """
    Returns True if Total Number of Borrowers is blank or less than 1.
    """
    try:
        return total_number_of_borrowers in ["", None] or float(total_number_of_borrowers) < 1
    except:
        return True

# df["flag_total_number_of_borrowers"] = df["Total Number of Borrowers"].apply(validate_total_number_of_borrowers)

# 78. UPB
# Flag if Current Loan Amount is blank
def validate_upb(current_loan_amount):
    """
    Returns True if Current Loan Amount is blank.
    """
    return current_loan_amount == ""

# df["flag_upb"] = df["Current Loan Amount"].apply(validate_upb)

# 79. Liquid Reserves
# Flag if reserves are blank/zero and loan type does not include 'CLOSED END SECOND'
def validate_liquid_reserves(liquid_cash_reserves, loan_type_ls):
    """
    Returns True if Liquid/Cash Reserves is blank or 0 and loan type does not contain 'CLOSED END SECOND'.
    """
    try:
        return liquid_cash_reserves in ["", 0, None] and "CLOSED END SECOND" not in str(loan_type_ls).upper()
    except:
        return True

# df["flag_liquid_reserves"] = df.apply(lambda row: validate_liquid_reserves(row["Liquid / Cash Reserves"], row["LOAN_TYPE_LS"]), axis=1)

# 80. Zip Code
# Flag if Postal Code is not 5 digits
def validate_zip_code(postal_code):
    """
    Returns True if Postal Code is blank or not 5 digits.
    """
    try:
        if postal_code is None or (isinstance(postal_code, str) and not postal_code.strip()):
            return True
        if pd.isna(postal_code):
            return True

        if isinstance(postal_code, (int, np.integer)):
            postal_code = f"{postal_code:05d}"
        elif isinstance(postal_code, float) and postal_code.is_integer():
            postal_code = f"{int(postal_code):05d}"
        else:
            postal_code = str(postal_code).strip()

        return len(postal_code) != 5
    except:
        return True

# df["flag_zip_code"] = df["Postal Code"].apply(validate_zip_code)


# This document contains Python functions converted from Excel formulas
# Each function includes a descriptive comment and is ready for use with df.apply(..., axis=1)

# Validations #50 through #80 are already present above.

# 81. Borrower Years In Industry
# Flag if Borrower Years in Industry is blank
def validate_borrower_years_in_industry(borrower_years_in_industry):
    """
    Returns True if Borrower Years in Industry is blank.
    """
    return borrower_years_in_industry == ""

# df["flag_borrower_years_in_industry"] = df["Borrower - Yrs at in Industry"].apply(validate_borrower_years_in_industry)

# 82. Original Price
# Flag if Original Appraised Property Value is blank
def validate_original_price(original_appraised_property_value):
    """
    Returns True if Original Appraised Property Value is blank.
    """
    return original_appraised_property_value == ""

# df["flag_original_price"] = df["Original Appraised Property Value"].apply(validate_original_price)

# 83. All Borrower Total Income
# Flag if All Borrower Total Income is blank or <= 0
def validate_all_borrower_total_income(all_borrower_total_income):
    """
    Returns True if All Borrower Total Income is blank or less than or equal to 0.
    """
    try:
        return all_borrower_total_income in ["", None] or float(all_borrower_total_income) <= 0
    except:
        return True

# df["flag_all_borrower_total_income"] = df["All Borrower Total Income"].apply(validate_all_borrower_total_income)

# 84. All Borrower Wage Income
# Flag if wage income does not match sum of borrower and co-borrower wages
def validate_all_borrower_wage_income(pbw, cbw, abw):
    """
    Returns True if All Borrower Wage Income is blank or does not equal sum of PBW and CBW (within tolerance).
    """
    try:
        expected = float(pbw or 0) + float(cbw or 0)
        return abw == "" or abs(expected - float(abw)) > 1
    except:
        return True

# df["flag_all_borrower_wage_income"] = df.apply(lambda row: validate_all_borrower_wage_income(row["Primary Borrower Wage Income"], row["Co-Borrower Wage Income"], row["All Borrower Wage Income"]), axis=1)

# 85. Borrower Income Verification Level
# Flag if Borrower Income Verification Level is blank
def validate_borrower_income_verification(borrower_income_verification_level):
    """
    Returns True if Borrower Income Verification Level is blank.
    """
    return borrower_income_verification_level == ""

# df["flag_borrower_income_verification"] = df["Borrower Income Verification Level"].apply(validate_borrower_income_verification)

# 86. Borrower Employment Verification
# Flag if Borrower Employment Verification is blank
def validate_borrower_employment_verification(borrower_employment_verification):
    """
    Returns True if Borrower Employment Verification is blank.
    """
    return borrower_employment_verification == ""

# df["flag_borrower_employment_verification"] = df["Borrower Employment Verification"].apply(validate_borrower_employment_verification)

# 87. Borrower Asset Verification
# Flag if Borrower Asset Verification is blank
def validate_borrower_asset_verification(borrower_asset_verification):
    """
    Returns True if Borrower Asset Verification is blank.
    """
    return borrower_asset_verification == ""

# df["flag_borrower_asset_verification"] = df["Borrower Asset Verification"].apply(validate_borrower_asset_verification)

# 88. Junior Drawn Amount
# Flag if Junior Mortgage Drawn Amount > Junior Mortgage Balance
def validate_junior_drawn_amount(junior_drawn_amount, junior_mortgage_balance):
    """
    Returns True if Junior Mortgage Drawn Amount exceeds Junior Mortgage Balance.
    """
    try:
        return float(junior_drawn_amount) > float(junior_mortgage_balance)
    except:
        return True

# df["flag_junior_drawn_amount"] = df.apply(lambda row: validate_junior_drawn_amount(row["Junior Mortgage Drawn Amount"], row["Junior Mortgage Balance"]), axis=1)

# 89. Total Income < 0
# Flag if All Borrower Total Income is less than 0
def validate_total_income_negative(all_borrower_total_income):
    """
    Returns True if All Borrower Total Income is negative.
    """
    try:
        return float(all_borrower_total_income or 0) < 0
    except:
        return True

# df["flag_total_income_negative"] = df["All Borrower Total Income"].apply(validate_total_income_negative)

# 90. Borrower Yrs Employment > Yrs in Industry
# Flag if Borrower employment length exceeds years in industry
def validate_borrower_employment_gt_industry(length_of_employment_borrower, borrower_years_in_industry):
    """
    Returns True if Borrower Employment Length > Years in Industry.
    """
    try:
        return round(float(length_of_employment_borrower), 2) > round(float(borrower_years_in_industry), 2)
    except:
        return True

# df["flag_borrower_employment_gt_industry"] = df.apply(lambda row: validate_borrower_employment_gt_industry(row["Length of Employment: Borrower"], row["Borrower - Yrs at in Industry"]), axis=1)


# This document contains Python functions converted from Excel formulas
# Each function includes a descriptive comment and is ready for use with df.apply(..., axis=1)

# Validations #50 through #90 are already present above.

# 91. Co-Borrower Yrs Employment > Yrs in Industry
# Flag if Co-Borrower employment length exceeds years in industry
def validate_coborrower_employment_gt_industry(length_of_employment_coborrower, coborrower_years_in_industry):
    """
    Returns True if Co-Borrower Employment Length > Years in Industry.
    """
    try:
        return float(length_of_employment_coborrower) > float(coborrower_years_in_industry)
    except:
        return True

# df["flag_coborrower_employment_gt_industry"] = df.apply(lambda row: validate_coborrower_employment_gt_industry(row["Length of Employment: Co-Borrower"], row["Co-Borrower - Yrs at in Industry"]), axis=1)

# 92. Application Date
# Flag if Application Date is after Origination or more than 10 years ago or blank
def validate_application_date(application_received_date, origination_date):
    """
    Returns True if:
    - Application Date is after Origination Date,
    - or is blank,
    - or more than 10 years before today.
    """
    from datetime import datetime
    import pandas as pd
    
    application_received_date = pd.to_datetime(application_received_date)
    origination_date = pd.to_datetime(origination_date)
    try:
        if (application_received_date == "") or (pd.isna(application_received_date)):
            return True
        if application_received_date > origination_date:
            return True
        return (datetime.now().year - application_received_date.year) > 10
    except:
        return True

# df["flag_application_date"] = df.apply(lambda row: validate_application_date(row["Application Received Date"], row["Origination Date"]), axis=1)

# 93. OLTV > 90%
# Flag if OLTV is > 90% and Loan Type is not 'SELECT 90 30 YR'
def validate_oltv_high_for_nonselect(original_cltv, loan_type_ls):
    """
    Returns True if OLTV > 90% and Loan Type is not 'SELECT 90 30 YR'.
    """
    try:
        return float(original_cltv) > 0.9 and str(loan_type_ls).strip().upper() != "SELECT 90 30 YR"
    except:
        return True

# df["flag_oltv_high_for_nonselect"] = df.apply(lambda row: validate_oltv_high_for_nonselect(row["Original CLTV"], row["LOAN_TYPE_LS"]), axis=1)

# 94. Large cash-out amounts
# Flag if Cash Out Amount exceeds Original Loan Amount
def validate_large_cash_out(cash_out_amount, original_loan_amount):
    """
    Returns True if Cash Out Amount > Original Loan Amount.
    """
    try:
        return float(cash_out_amount) > float(original_loan_amount)
    except:
        return True

# df["flag_large_cash_out"] = df.apply(lambda row: validate_large_cash_out(row["Cash Out Amount"], row["Original Loan Amount"]), axis=1)

# 95. Broker Indicator
# Flag if Channel = 2 and Broker Indicator is blank
def validate_broker_indicator(channel, broker_indicator):
    """
    Returns True if Channel = 2 and Broker Indicator is blank.
    """
    return str(channel) == "2" and broker_indicator in ["", None]

# df["flag_broker_indicator"] = df.apply(lambda row: validate_broker_indicator(row["Channel"], row["Broker Indicator"]), axis=1)

# 96. Missing Length of employment both borrowers
# Flag if 2+ borrowers and both employment lengths are missing/zero with verification level 3
def validate_missing_employment_both_borrowers(total_borrowers, b1_len_emp, b2_len_emp, b1_emp_ver, b2_emp_ver): # ["Total Number of Borrowers", "Length of Employment: Borrower", "Length of Employment: Co-Borrower", "Borrower Employment Verification", "Co-Borrower Employment Verification"]),employment Flag", "Co-Borrower Employment Verification"]
    """
    Returns True if:
    - 2+ borrowers,
    - AND both employment lengths are blank or zero,
    - AND either borrower or co-borrower has verification code 3.
    """
    try:
        return (
            int(total_borrowers) >= 2 and
            (pd.isna(b1_len_emp) or b1_len_emp in ["", 0, None]) and
            (pd.isna(b2_len_emp) or b2_len_emp in ["", 0, None]) and
            (int(b1_emp_ver) == 3 or int(b2_emp_ver) == 3)
        )
    except:
        return True

# df["flag_missing_employment_both_borrowers"] = df.apply(lambda row: validate_missing_employment_both_borrowers(row["Total Number of Borrowers"], row["Length of Employment: Borrower"], row["Length of Employment: Co-Borrower"], row["Borrower Employment Verification"], row["Co-Borrower Employment Verification"]), axis=1)

# 97. Years In Home
# Flag if Years in Home is missing or < 0 for certain Loan Purposes and Occupancy
def validate_years_in_home(loan_purpose, years_in_home, occupancy):
    """
    Returns True if:
    - Loan Purpose not in [6, 7, 10],
    - AND Years in Home is blank or < 0,
    - AND Occupancy is not 2.
    """
    try:
        return (
            float(loan_purpose) not in [6, 7, 10] and
            (pd.isna(years_in_home) or years_in_home == "" or float(years_in_home) < 0) and
            float(occupancy) != 2
        )
    except:
        return True

# df["flag_years_in_home"] = df.apply(lambda row: validate_years_in_home(row["Loan Purpose"], row["Years in Home"], row["Occupancy"]), axis=1)

# 98. Review Type
# Flag if DD Review Type is blank or 'Purchase Review'
def validate_review_type(dd_review_type):
    """
    Returns True if Review Type is blank or 'Purchase Review'.
    """
    return dd_review_type in ["", "Purchase Review"]

# df["flag_review_type"] = df["DD Review Type"].apply(validate_review_type)

# 99. Negative Reserves
# Flag if Liquid / Cash Reserves < 0
def validate_negative_reserves(liquid_cash_reserves):
    """
    Returns True if reserves are negative.
    """
    try:
        return float(liquid_cash_reserves) < 0
    except:
        return True

# df["flag_negative_reserves"] = df["Liquid / Cash Reserves"].apply(validate_negative_reserves)

# 100. APOR/Safe Harbor
# Flag if required string is not present based on Application Date
def validate_apor_safe_harbor(application_date, atrqm_status):
    """
    Returns True if:
    - Application Date is between Jan 10, 2014 and Jun 30, 2021 and 'Safe Harbor' not found,
    - OR Application Date >= Jul 1, 2021 and 'APOR' not found.
    """
    from datetime import datetime
    import pandas as pd
    
    application_date = pd.to_datetime(application_date)
    
    try:
        check_str = str(atrqm_status).upper()
        safe_harbor_start = datetime(2014, 1, 10)
        safe_harbor_end = datetime(2021, 6, 30)
        apor_start = datetime(2021, 7, 1)

        if safe_harbor_start <= application_date <= safe_harbor_end:
            return "SAFE HARBOR" not in check_str
        elif application_date >= apor_start:
            return "APOR" not in check_str
        else:
            return True  # application date is before safe harbor allowed
    except:
        return True


# df["flag_apor_safe_harbor"] = df.apply(lambda row: validate_apor_safe_harbor(row["Application Received Date"], row["ATRQMStatus"]), axis=1)


# This document contains Python functions converted from Excel formulas
# Each function includes a descriptive comment and is ready for use with df.apply(..., axis=1)

# Validations #50 through #100 are already present above.

# 101. Property Address
# Flag if Property Address is blank
def validate_property_address(property_address):
    """
    Returns True if Property Address is blank.
    """
    return property_address == ""

# df["flag_property_address"] = df["Property Address"].apply(validate_property_address)

# 102. Seller Loan Number
# Flag if Seller Loan Number is blank
def validate_seller_loan_number_field(seller_loan_number):
    """
    Returns True if Seller Loan Number is blank.
    """
    return seller_loan_number == ""

# df["flag_seller_loan_number"] = df["Seller Loan Number"].apply(validate_seller_loan_number_field)

# 103. Lien Position
# Flag if Lien Position is 2 and Loan Type does not contain 'SECOND'
def validate_lien_position_vs_loan_type(lien_position, loan_type_ls):
    """
    Returns True if Lien Position is 2 and Loan Type does not include 'SECOND'.
    """
    return lien_position == 2 and "SECOND" not in str(loan_type_ls).upper()

# df["flag_lien_position_vs_loan_type"] = df.apply(lambda row: validate_lien_position_vs_loan_type(row["Lien Position"], row["LOAN_TYPE_LS"]), axis=1)

# 104. First Payment < Maturity Date
# Flag if First Payment Date is after Maturity Date
def validate_first_payment_before_maturity(first_payment_date, maturity_date):
    """
    Returns True if First Payment Date is after Maturity Date.
    """
    try:
        return first_payment_date > maturity_date
    except:
        return True

# df["flag_first_payment_before_maturity"] = df.apply(lambda row: validate_first_payment_before_maturity(row["First Payment Date of Loan"], row["Maturity Date"]), axis=1)

# 105. Negative incomes
# Flag if any income value is negative
def validate_negative_incomes(*incomes):
    """
    Returns True if any of the provided income fields are negative.
    """
    try:
        return any(float(val) < 0 for val in incomes if val not in ["", None])
    except:
        return True

# df["flag_negative_incomes"] = df.apply(lambda row: validate_negative_incomes(
#     row["Primary Borrower Wage Income"], row["Co-Borrower Wage Income"],
#     row["Primary Borrower Other Income"], row["Co-Borrower Other Income"],
#     row["All Borrower Wage Income"], row["All Borrower Total Income"]), axis=1)

# 106. Current Bal > Original Bal
# Flag if Current Loan Amount exceeds Original Loan Amount
def validate_current_gt_original_balance(current_loan_amount, original_loan_amount):
    """
    Returns True if Current Loan Amount > Original Loan Amount.
    """
    try:
        return float(current_loan_amount) > float(original_loan_amount)
    except:
        return True

# df["flag_current_gt_original_balance"] = df.apply(lambda row: validate_current_gt_original_balance(row["Current Loan Amount"], row["Original Loan Amount"]), axis=1)

# 106A. Age = 0 and Current Bal <> Original Bal
# Flag if Age is 0 and Current Loan Amount differs from Original Loan Amount
def validate_age_zero_current_balance_diff(
    original_amortization_term,
    maturity_date,
    interest_paid_through_date,
    current_loan_amount,
    original_loan_amount,
):
    """
    Returns True if:
    - Age = Original Amortization Term - months_between(Maturity Date, Interest Paid Through Date) equals 0,
    - AND Current Loan Amount != Original Loan Amount.
    """
    try:
        if original_amortization_term in ["", None] or pd.isna(original_amortization_term):
            return True
        if maturity_date in ["", None] or pd.isna(maturity_date):
            return True
        if interest_paid_through_date in ["", None] or pd.isna(interest_paid_through_date):
            return True

        maturity_dt = pd.to_datetime(maturity_date)
        paid_through_dt = pd.to_datetime(interest_paid_through_date)
        if pd.isna(maturity_dt) or pd.isna(paid_through_dt):
            return True

        months_between = (maturity_dt.year - paid_through_dt.year) * 12 + (
            maturity_dt.month - paid_through_dt.month
        )
        age = float(original_amortization_term) - months_between
        if round(age, 6) == 0:
            return float(current_loan_amount) != float(original_loan_amount)
        return False
    except:
        return True

# df["flag_age_zero_current_balance_diff"] = df.apply(lambda row: validate_age_zero_current_balance_diff(
#     row["Original Amortization Term"], row["Maturity Date"], row["Interest Paid Through Date"],
#     row["Current Loan Amount"], row["Original Loan Amount"]), axis=1)

# 107. Margin < Floor
# Flag if Gross Margin is less than Lifetime Minimum Rate (Floor)
def validate_margin_less_than_floor(gross_margin, lifetime_min_rate_floor):
    """
    Returns True if Gross Margin < Lifetime Minimum Rate (Floor).
    """
    try:
        return gross_margin < lifetime_min_rate_floor
    except:
        return True

# df["flag_margin_less_than_floor"] = df.apply(lambda row: validate_margin_less_than_floor(row["Gross Margin"], row["Lifetime Minimum Rate (Floor)"]), axis=1)

# 108. Amort Term > Term to Maturity
# Flag if Original Amortization Term is greater than Original Term to Maturity
def validate_amort_term_gt_term_to_maturity(original_amortization_term, original_term_to_maturity):
    """
    Returns True if Original Amortization Term > Original Term to Maturity.
    """
    try:
        return float(original_amortization_term) > float(original_term_to_maturity)
    except:
        return True

# df["flag_amort_term_gt_term_to_maturity"] = df.apply(lambda row: validate_amort_term_gt_term_to_maturity(row["Original Amortization Term"], row["Original Term to Maturity"]), axis=1)

# 109. Missing Subsequent Payment Reset Period
# Flag if field is missing or zero when Amortization Type is 2
def validate_missing_subsequent_payment_reset(amortization_type, subsequent_payment_reset_period):
    """
    Returns True if Amortization Type is 2 and Reset Period is blank or 0.
    """
    return amortization_type == 2 and subsequent_payment_reset_period in ["", 0, None]

# df["flag_missing_subsequent_payment_reset"] = df.apply(lambda row: validate_missing_subsequent_payment_reset(row["Amortization Type"], row["Subsequent Payment Reset Period"]), axis=1)

# 110. Sales price with incorrect loan purpose
# Flag if Sales Price is present but Loan Purpose is not 6 or 7
def validate_sales_price_incorrect_purpose(sales_price, loan_purpose):
    """
    Returns True if Sales Price is nonzero and Loan Purpose is not 6 or 7.
    """
    try:
        return float(sales_price) > 0 and loan_purpose not in [6, 7]
    except:
        return True

# df["flag_sales_price_incorrect_purpose"] = df.apply(lambda row: validate_sales_price_incorrect_purpose(row["Sales Price"], row["Loan Purpose"]), axis=1)

# 111. T&I <= 0
# Flag if Current 'Other' Monthly Payment is blank or 0 and Escrow Indicator is not 0 or 99
def validate_ti_payment(current_other_monthly_payment, escrow_indicator):
    """
    Returns True if T&I is blank or zero AND Escrow Indicator is not 0 or 99.
    """
    try:
        return current_other_monthly_payment in ["", 0, None] and escrow_indicator not in [0, 99]
    except:
        return True

# df["flag_ti_payment"] = df.apply(lambda row: validate_ti_payment(row["Current ‘Other’ Monthly Payment"], row["Escrow Indicator"]), axis=1)

# 114. OCLTV < OLTV
# Flag if OCLTV differs from OLTV and there is no Junior Lien and Loan Type does not include 'SECOND'
def validate_ocltv_vs_oltv(original_cltv, original_ltv, junior_mortgage_balance, loan_type_ls):
    """
    Returns True if:
    - Junior Mortgage Balance is 0 or blank,
    - AND OLTV != OCLTV,
    - AND Loan Type does not contain 'SECOND'.
    """
    try:
        return (
            junior_mortgage_balance in ["", 0, None] and
            round(float(original_cltv), 4) != round(float(original_ltv), 4) and
            "SECOND" not in str(loan_type_ls).upper()
        )
    except:
        return True

# df["flag_oclTV_vs_oltv"] = df.apply(lambda row: validate_oclTV_vs_oltv(row["Original CLTV"], row["Original LTV"], row["Junior Mortgage Balance"], row["LOAN_TYPE_LS"]), axis=1)

# 115. HELOC Ind
# Flag if HELOC Indicator is 1 and HELOC Draw Period is missing or zero
def validate_heloc_indicator(heloc_indicator, heloc_draw_period):
    """
    Returns True if HELOC Indicator is 1 and HELOC Draw Period is blank or 0.
    """
    return heloc_indicator == 1 and heloc_draw_period in ["", 0, None]

# df["flag_heloc_indicator"] = df.apply(lambda row: validate_heloc_indicator(row["HELOC Indicator"], row["HELOC Draw Period"]), axis=1)

# 116. Purchase with Years in Home
# Flag if Loan Purpose is Purchase (7) and Years in Home > 0
def validate_purchase_with_years_in_home(loan_purpose, years_in_home):
    """
    Returns True if Loan Purpose = 7 (Purchase) and Years in Home > 0.
    """
    try:
        return int(loan_purpose) == 7 and float(years_in_home) > 0
    except:
        return True

# df["flag_purchase_with_years_in_home"] = df.apply(lambda row: validate_purchase_with_years_in_home(row["Loan Purpose"], row["Years in Home"]), axis=1)

# 117. Paid Thru < First Pay
# Flag if Interest Paid Through Date is before First Payment Date and balances are unequal
# def validate_paid_thru_lt_first_pay(interest_paid_through_date, first_payment_date, original_loan_amount, current_loan_amount):
#     """
#     Returns True if:
#     - Interest Paid Through Date < First Payment Date, and
#     - Original Loan Amount != Current Loan Amount
#     """
#     try:
#         return interest_paid_through_date < first_payment_date and original_loan_amount != current_loan_amount
#     except:
#         return True

# df["flag_paid_thru_lt_first_pay"] = df.apply(lambda row: validate_paid_thru_lt_first_pay(row["Interest Paid Through Date"], row["First Payment Date of Loan"], row["Original Loan Amount"], row["Current Loan Amount"]), axis=1)


# 118. Refinance with Years in Home < 1
# Flag if Loan Purpose is Purchase (9 or 3) and Years in Home < 1
def validate_refi_with_less_than_1_year_in_home(loan_purpose, years_in_home, occupancy):
    """
    Returns True if Loan Purpose in (3 - Cash out or 9 Refi)  and Years in Home < 1.
    """
    try:
        return int(loan_purpose) in ( 3, 9) and (float(years_in_home)) < 1 and (int(occupancy) == 1)
    except:
        return True

__all__ = [name for name, value in globals().items() if name.startswith("validate_") and callable(value)]
if "pmt" in globals():
    __all__.append("pmt")
