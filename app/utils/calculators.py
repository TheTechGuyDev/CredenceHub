# ─────────────────────────────────────────
# CREDENCEHUB — DEAL CALCULATORS
# CredenceHub Analysis Engine — industry-standard real estate mathematics
# Methodology for MAO and MLV calculations
# ─────────────────────────────────────────


def safe_float(value, default=0.0):
    try:
        return float(value) if value not in (None, '', 'None') else default
    except (ValueError, TypeError):
        return default


def calculate_deal(strategy, inputs):
    calculators = {
        'wholesale': calculate_wholesale,
        'fix_flip': calculate_fix_flip,
        'brrrr': calculate_brrrr,
        'construction': calculate_construction,
        'commercial': calculate_commercial,
        'infill': calculate_infill,
    }
    calc_fn = calculators.get(strategy)
    if calc_fn:
        return calc_fn(inputs)
    return {}


# ── 1A. Wholesale ──
# Uses industry-standard MAO methodology
def calculate_wholesale(inputs):
    """
    CredenceHub Multifamily Formula (per client specification, v2)

    Gross Scheduled Rent  = (Monthly Rent per Unit x Total Units) x 12
    Gross Rental Income   = Gross Scheduled Rent + Ancillary Income
    Effective Gross Income (EGI) = Gross Rental Income - Vacancy Factor (floor: 5%)

    Operating Expenses — two modes:
      Quick Screening: EGI x 35%
      Itemized: Property Taxes + Insurance + Utilities + Property Management
                + Repairs & Maintenance + Landscaping + Payroll/Admin
      (Mortgage principal & interest is explicitly excluded — it's debt
      service, not an operating expense.)

    Net Operating Income (NOI) = EGI - Total Operating Expenses

    Annual Debt Service (ADS) = Monthly Mortgage Payment (P&I) x 12
      Monthly Mortgage Payment: P = L x [c(1+c)^n / ((1+c)^n - 1)]
        L = Purchase Price - Down Payment
        c = Annual Interest Rate / 12
        n = Amortization Years x 12

    Debt Service Coverage Ratio (DSCR) = NOI / Annual Debt Service
      (Most lenders require a minimum of 1.20x-1.25x)

    Cash Flow            = NOI - Annual Debt Service
    Cash on Cash Return  = Cash Flow / Down Payment x 100%
    Deal Cap Rate        = NOI / Purchase Price x 100%

    Decision Framework:
      1. Cash Flow must be positive
      2. Cash on Cash Return must beat the bank
      3. Deal Cap Rate must be higher than Market Cap Rate
    """
    purchase_price = safe_float(inputs.get('purchase_price'))
    down_payment = safe_float(inputs.get('down_payment'))

    # Gross Rental Income
    monthly_rent_per_unit = safe_float(inputs.get('monthly_rent_per_unit'))
    total_units = safe_float(inputs.get('total_units'), 1)
    ancillary_income = safe_float(inputs.get('ancillary_income'))

    gross_scheduled_rent = (monthly_rent_per_unit * total_units) * 12
    gross_rental_income = gross_scheduled_rent + ancillary_income

    # Effective Gross Income — vacancy factor has an enforced 5% floor
    vacancy_factor_pct_input = safe_float(inputs.get('vacancy_factor_pct'), 5)
    vacancy_factor_pct = max(vacancy_factor_pct_input, 5)
    effective_gross_income = gross_rental_income - (gross_rental_income * vacancy_factor_pct / 100)

    # Operating Expenses — Quick Screening vs Itemized
    opex_mode = inputs.get('opex_mode', 'quick')
    if opex_mode == 'itemized':
        property_taxes = safe_float(inputs.get('property_taxes'))
        insurance = safe_float(inputs.get('insurance'))
        utilities = safe_float(inputs.get('utilities'))
        property_management = safe_float(inputs.get('property_management'))
        repairs_maintenance = safe_float(inputs.get('repairs_maintenance'))
        landscaping = safe_float(inputs.get('landscaping'))
        payroll_admin = safe_float(inputs.get('payroll_admin'))
        total_operating_expenses = (
            property_taxes + insurance + utilities + property_management
            + repairs_maintenance + landscaping + payroll_admin
        )
    else:
        total_operating_expenses = effective_gross_income * 0.35

    # Net Operating Income
    noi = effective_gross_income - total_operating_expenses

    # Annual Debt Service — standard commercial loan amortization
    interest_rate = safe_float(inputs.get('interest_rate'), 6)
    amortization_years = safe_float(inputs.get('amortization_years'), 25)

    loan_amount = purchase_price - down_payment
    monthly_rate = interest_rate / 100 / 12
    n_payments = amortization_years * 12

    if monthly_rate > 0 and n_payments > 0:
        monthly_mortgage_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** n_payments
        ) / ((1 + monthly_rate) ** n_payments - 1)
    elif n_payments > 0:
        monthly_mortgage_payment = loan_amount / n_payments
    else:
        monthly_mortgage_payment = 0

    annual_debt_service = monthly_mortgage_payment * 12

    # Debt Service Coverage Ratio
    dscr = (noi / annual_debt_service) if annual_debt_service > 0 else 0

    # Core formulas
    cash_flow = noi - annual_debt_service
    coc_return = (cash_flow / down_payment * 100) if down_payment > 0 else 0
    cap_rate = (noi / purchase_price * 100) if purchase_price > 0 else 0

    # Decision Framework
    bank_rate_pct = safe_float(inputs.get('bank_rate_pct'), 5)
    market_cap_rate_pct = safe_float(inputs.get('market_cap_rate_pct'), 6)
    passes_cash_flow = cash_flow > 0
    passes_coc = coc_return > bank_rate_pct
    passes_cap_rate = cap_rate > market_cap_rate_pct
    passes_dscr = dscr >= 1.20
    deal_score = sum([passes_cash_flow, passes_coc, passes_cap_rate])

    return {
        'gross_scheduled_rent': round(gross_scheduled_rent, 2),
        'ancillary_income': round(ancillary_income, 2),
        'gross_rental_income': round(gross_rental_income, 2),
        'vacancy_factor_pct': round(vacancy_factor_pct, 2),
        'effective_gross_income': round(effective_gross_income, 2),
        'opex_mode': opex_mode,
        'operating_expenses': round(total_operating_expenses, 2),
        'noi': round(noi, 2),
        'loan_amount': round(loan_amount, 2),
        'monthly_mortgage_payment': round(monthly_mortgage_payment, 2),
        'annual_debt_service': round(annual_debt_service, 2),
        'dscr': round(dscr, 2),
        'passes_dscr': passes_dscr,
        'cash_flow': round(cash_flow, 2),
        'coc_return': round(coc_return, 2),
        'cap_rate': round(cap_rate, 2),
        'bank_rate_pct': round(bank_rate_pct, 2),
        'market_cap_rate_pct': round(market_cap_rate_pct, 2),
        'passes_cash_flow': passes_cash_flow,
        'passes_coc': passes_coc,
        'passes_cap_rate': passes_cap_rate,
        'deal_score': deal_score,
        'is_deal_viable': deal_score == 3,
    }


# ── 1B. Fix & Flip ──
def calculate_fix_flip(inputs):
    """
    CredenceHub Fix & Flip Formula (per client specification)

    MAO (Maximum Allowable Offer) = (ARV x 0.70) - Estimated Repair Costs
    MPP (Maximum Purchase Price)  = ARV - Repair Costs - Holding Costs
                                     - Closing Costs - Target Net Profit
    Total Net Profit              = ARV - Total Project Cost
    """
    purchase_price = safe_float(inputs.get('purchase_price'))
    rehab_cost = safe_float(inputs.get('rehab_cost'))
    arv = safe_float(inputs.get('arv'))
    hold_months = safe_float(inputs.get('hold_months'), 6)
    interest_rate = safe_float(inputs.get('interest_rate'), 0)
    loan_amount = safe_float(inputs.get('loan_amount'), 0)
    selling_costs_pct = safe_float(inputs.get('selling_costs_pct'), 8)
    closing_costs = safe_float(inputs.get('closing_costs'), 3000)
    target_net_profit = safe_float(inputs.get('target_net_profit'), 0)
    financing_method = inputs.get('financing_method', 'cash')

    selling_costs = arv * (selling_costs_pct / 100)
    holding_costs = (loan_amount * (interest_rate / 100) / 12) * hold_months if loan_amount > 0 else 0
    total_investment = purchase_price + rehab_cost + holding_costs + selling_costs
    profit = arv - total_investment
    roi = (profit / (purchase_price + rehab_cost) * 100) if (purchase_price + rehab_cost) > 0 else 0
    annualized_roi = (roi / hold_months * 12) if hold_months > 0 else 0
    cash_invested = purchase_price + rehab_cost - loan_amount
    coc_return = (profit / cash_invested * 100) if cash_invested > 0 else 0
    break_even_arv = total_investment

    # MAO — 70% Rule
    mao = (arv * 0.70) - rehab_cost
    is_good_deal = purchase_price <= mao

    # MPP — Maximum Purchase Price backed into from a target profit
    mpp = arv - rehab_cost - holding_costs - closing_costs - target_net_profit

    # Total Net Profit
    total_project_cost = purchase_price + rehab_cost + holding_costs + closing_costs
    total_net_profit = arv - total_project_cost

    return {
        'profit': round(profit, 2),
        'roi': round(roi, 2),
        'annualized_roi': round(annualized_roi, 2),
        'coc_return': round(coc_return, 2),
        'break_even_arv': round(break_even_arv, 2),
        'total_investment': round(total_investment, 2),
        'selling_costs': round(selling_costs, 2),
        'holding_costs': round(holding_costs, 2),
        'cash_invested': round(cash_invested, 2),
        'mao': round(max(mao, 0), 2),
        'mao_check_70': round(max(mao, 0), 2),
        'mpp': round(mpp, 2),
        'closing_costs': round(closing_costs, 2),
        'target_net_profit': round(target_net_profit, 2),
        'total_project_cost': round(total_project_cost, 2),
        'total_net_profit': round(total_net_profit, 2),
        'is_good_deal': is_good_deal,
    }


# ── 1C. BRRRR ──
def calculate_brrrr(inputs):
    """
    CredenceHub BRRRR Formula (per client specification)

    1. Acquisition & Screening
       BRRRR MAO = (ARV x Refinance LTV %) - Estimated Repair Costs

    2. Cost Calculations
       Initial Cash Invested = Down Payment + Acquisition Costs + Rehab Costs + Holding Costs
       Holding Costs = (Monthly Loan Interest + Property Taxes + Insurance + Utilities) x Months to Refinance

    3. Refinance Metrics
       Refinance Loan Amount = ARV x Refinance LTV %

    4. Cash Left in Deal
       Cash Left in Deal = Initial Cash Invested
                            - (Refinance Loan Amount - Initial Debt Payoff - Refinance Closing Costs)
    """
    purchase_price = safe_float(inputs.get('purchase_price'))
    rehab_cost = safe_float(inputs.get('rehab_cost'))
    arv = safe_float(inputs.get('arv'))
    refinance_ltv = safe_float(inputs.get('refinance_ltv'), 75)

    # 1. Acquisition & Screening
    mao = (arv * (refinance_ltv / 100)) - rehab_cost

    # 2. Cost Calculations
    down_payment = safe_float(inputs.get('down_payment'))
    acquisition_costs = safe_float(inputs.get('acquisition_costs'))
    monthly_loan_interest = safe_float(inputs.get('monthly_loan_interest'))
    property_taxes = safe_float(inputs.get('property_taxes'))
    insurance = safe_float(inputs.get('insurance'))
    utilities = safe_float(inputs.get('utilities'))
    months_to_refinance = safe_float(inputs.get('months_to_refinance'), 6)

    holding_costs = (monthly_loan_interest + property_taxes + insurance + utilities) * months_to_refinance
    initial_cash_invested = down_payment + acquisition_costs + rehab_cost + holding_costs

    # 3. Refinance Metrics
    refinance_loan_amount = arv * (refinance_ltv / 100)

    # 4. Cash Left in Deal
    initial_debt_payoff = safe_float(inputs.get('initial_debt_payoff'), purchase_price)
    refinance_closing_costs = safe_float(inputs.get('refinance_closing_costs'))
    cash_left_in_deal = initial_cash_invested - (refinance_loan_amount - initial_debt_payoff - refinance_closing_costs)

    # Supplementary post-refinance rental metrics (not part of the client's 4
    # formulas — kept as useful bonus context on the results panel).
    monthly_rent = safe_float(inputs.get('monthly_rent'))
    monthly_expenses = safe_float(inputs.get('monthly_expenses'))
    interest_rate = safe_float(inputs.get('interest_rate'), 6)
    loan_term_years = safe_float(inputs.get('loan_term_years'), 25)

    monthly_rate = interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    if monthly_rate > 0:
        mortgage_payment = refinance_loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / \
                           ((1 + monthly_rate) ** n_payments - 1)
    else:
        mortgage_payment = refinance_loan_amount / n_payments if n_payments > 0 else 0

    monthly_cashflow = monthly_rent - monthly_expenses - mortgage_payment
    annual_cashflow = monthly_cashflow * 12
    coc_return = (annual_cashflow / cash_left_in_deal * 100) if cash_left_in_deal > 0 else 0
    gross_yield = (monthly_rent * 12 / arv * 100) if arv > 0 else 0
    infinite_return = cash_left_in_deal <= 0

    return {
        'mao': round(max(mao, 0), 2),
        'initial_cash_invested': round(initial_cash_invested, 2),
        'holding_costs': round(holding_costs, 2),
        'refinance_loan_amount': round(refinance_loan_amount, 2),
        'refinance_amount': round(refinance_loan_amount, 2),
        'cash_left_in_deal': round(cash_left_in_deal, 2),
        'capital_left_in': round(max(cash_left_in_deal, 0), 2),
        'capital_recycled': round(refinance_loan_amount, 2),
        'total_invested': round(initial_cash_invested, 2),
        'equity_in_deal': round(arv - refinance_loan_amount, 2),
        'mortgage_payment': round(mortgage_payment, 2),
        'monthly_cashflow': round(monthly_cashflow, 2),
        'annual_cashflow': round(annual_cashflow, 2),
        'coc_return': round(coc_return, 2),
        'gross_yield': round(gross_yield, 2),
        'infinite_return': infinite_return,
    }


# ── 1D. New Construction — CredenceHub Methodology ──
# Spec Build + Build to Rent analysis
def calculate_construction(inputs):
    exit_strategy = inputs.get('exit_strategy', 'spec_build')

    if exit_strategy == 'build_to_rent':
        return _calculate_build_to_rent(inputs)
    else:
        return _calculate_spec_build(inputs)


# ── 1E. Infill & Development ──
def calculate_infill(inputs):
    """
    Same underlying methodology as New Construction (Spec Build): land + build
    cost weighed against resale value, scoped for smaller urban infill lots
    (single lot, teardown/rebuild, laneway/garden suite, small multi-unit, etc).

    CredenceHub Infill Formula
    MLV = (ARV x (1 - Target Profit Margin)) - Construction Cost
          - Soft Costs - Holding Costs - Financing Costs - Selling Costs
    MAO = MLV - Assignment Fee (if wholesaling the lot)
    """
    arv = safe_float(inputs.get('arv'))
    target_profit_margin = safe_float(inputs.get('target_profit_margin'), 25) / 100
    construction_cost = safe_float(inputs.get('construction_cost'))
    soft_costs = safe_float(inputs.get('soft_costs'))
    holding_costs = safe_float(inputs.get('holding_costs'))
    financing_costs = safe_float(inputs.get('financing_costs'))
    selling_costs_pct = safe_float(inputs.get('selling_costs_pct'), 6) / 100
    assignment_fee = safe_float(inputs.get('assignment_fee'), 0)
    floor_area = safe_float(inputs.get('floor_area'), 1)
    contingency_pct = safe_float(inputs.get('contingency_pct'), 0)

    selling_costs = arv * selling_costs_pct
    contingency = (construction_cost + soft_costs) * (contingency_pct / 100)
    total_other_costs = construction_cost + soft_costs + holding_costs + financing_costs + selling_costs + contingency

    profit_factor = 1 - target_profit_margin
    adjusted_arv = arv * profit_factor
    maximum_land_value = adjusted_arv - total_other_costs

    land_cost = safe_float(inputs.get('land_cost'), 0)
    total_cost = land_cost + total_other_costs
    developer_profit = arv - total_cost
    actual_profit_margin = (developer_profit / arv * 100) if arv > 0 else 0
    roi = (developer_profit / total_cost * 100) if total_cost > 0 else 0
    cost_per_sqft = total_cost / floor_area if floor_area > 0 else 0

    mao = maximum_land_value - assignment_fee

    return {
        'maximum_land_value': round(max(maximum_land_value, 0), 2),
        'mao': round(max(mao, 0), 2),
        'adjusted_arv': round(adjusted_arv, 2),
        'total_other_costs': round(total_other_costs, 2),
        'selling_costs': round(selling_costs, 2),
        'contingency': round(contingency, 2),
        'developer_profit': round(developer_profit, 2),
        'actual_profit_margin': round(actual_profit_margin, 2),
        'target_profit_margin_pct': round(target_profit_margin * 100, 1),
        'roi': round(roi, 2),
        'cost_per_sqft': round(cost_per_sqft, 2),
        'total_cost': round(total_cost, 2),
        'is_deal_viable': maximum_land_value > 0,
    }


def _calculate_spec_build(inputs):
    """
    CredenceHub Land Development Formula (per client specification)

    MAO / MLP (Maximum Allowable Offer / Maximum Land Price)
      = ARV x (1 - Net Profit Margin %) - Construction Costs - Soft Costs - Holding Costs

    MAO = MLP - Assignment Fee (if wholesaling the land)
    """
    arv = safe_float(inputs.get('arv'))
    target_profit_margin = safe_float(inputs.get('target_profit_margin'), 25) / 100
    construction_cost = safe_float(inputs.get('construction_cost'))
    soft_costs = safe_float(inputs.get('soft_costs'))
    holding_costs = safe_float(inputs.get('holding_costs'))
    assignment_fee = safe_float(inputs.get('assignment_fee'), 0)
    floor_area = safe_float(inputs.get('floor_area'), 1)
    contingency_pct = safe_float(inputs.get('contingency_pct'), 0)

    contingency = (construction_cost + soft_costs) * (contingency_pct / 100)
    total_other_costs = construction_cost + soft_costs + holding_costs + contingency

    # CredenceHub Core Formula
    profit_factor = 1 - target_profit_margin
    adjusted_arv = arv * profit_factor
    maximum_land_value = adjusted_arv - total_other_costs

    # If developer is buying the land directly
    land_cost = safe_float(inputs.get('land_cost'), 0)
    total_cost = land_cost + total_other_costs
    developer_profit = arv - total_cost
    actual_profit_margin = (developer_profit / arv * 100) if arv > 0 else 0
    roi = (developer_profit / total_cost * 100) if total_cost > 0 else 0
    cost_per_sqft = total_cost / floor_area if floor_area > 0 else 0

    # Wholesaler MAO = MLP - Assignment Fee
    mao = maximum_land_value - assignment_fee

    return {
        'exit_strategy': 'spec_build',
        'maximum_land_value': round(max(maximum_land_value, 0), 2),
        'mao': round(max(mao, 0), 2),
        'adjusted_arv': round(adjusted_arv, 2),
        'total_other_costs': round(total_other_costs, 2),
        'contingency': round(contingency, 2),
        'developer_profit': round(developer_profit, 2),
        'actual_profit_margin': round(actual_profit_margin, 2),
        'target_profit_margin_pct': round(target_profit_margin * 100, 1),
        'roi': round(roi, 2),
        'cost_per_sqft': round(cost_per_sqft, 2),
        'total_cost': round(total_cost, 2),
        'is_deal_viable': maximum_land_value > 0,
    }


def _calculate_build_to_rent(inputs):
    """
    CredenceHub Build to Rent (Build and Hold)
    NOI = Gross Annual Rent - Annual Operating Expenses
    As-Built Value = NOI / Market Cap Rate
    MLV = (As-Built Value x (1 - Desired Equity Margin))
          - Construction Cost - Soft Costs - Holding Costs - Financing Costs
    """
    gross_annual_rent = safe_float(inputs.get('gross_annual_rent'))
    annual_operating_expenses = safe_float(inputs.get('annual_operating_expenses'))
    market_cap_rate = safe_float(inputs.get('market_cap_rate'), 8) / 100
    desired_equity_margin = safe_float(inputs.get('desired_equity_margin'), 20) / 100
    construction_cost = safe_float(inputs.get('construction_cost'))
    soft_costs = safe_float(inputs.get('soft_costs'))
    holding_costs = safe_float(inputs.get('holding_costs'))
    financing_costs = safe_float(inputs.get('financing_costs'))
    assignment_fee = safe_float(inputs.get('assignment_fee'), 0)
    floor_area = safe_float(inputs.get('floor_area'), 1)
    contingency_pct = safe_float(inputs.get('contingency_pct'), 0)

    # CredenceHub Build to Rent Core Formula
    noi = gross_annual_rent - annual_operating_expenses
    as_built_value = noi / market_cap_rate if market_cap_rate > 0 else 0
    equity_factor = 1 - desired_equity_margin
    contingency = (construction_cost + soft_costs) * (contingency_pct / 100)
    total_other_costs = construction_cost + soft_costs + holding_costs + financing_costs + contingency
    maximum_land_value = (as_built_value * equity_factor) - total_other_costs

    # MAO for wholesaler
    mao = maximum_land_value - assignment_fee

    # If land cost is known
    land_cost = safe_float(inputs.get('land_cost'), 0)
    total_cost = land_cost + total_other_costs
    built_in_equity = as_built_value - total_cost
    equity_pct = (built_in_equity / as_built_value * 100) if as_built_value > 0 else 0
    cost_per_sqft = total_cost / floor_area if floor_area > 0 else 0
    gross_yield = (gross_annual_rent / as_built_value * 100) if as_built_value > 0 else 0
    monthly_cashflow_estimate = (noi / 12) - (total_cost * 0.005)

    return {
        'exit_strategy': 'build_to_rent',
        'noi': round(noi, 2),
        'as_built_value': round(as_built_value, 2),
        'maximum_land_value': round(max(maximum_land_value, 0), 2),
        'mao': round(max(mao, 0), 2),
        'total_other_costs': round(total_other_costs, 2),
        'contingency': round(contingency, 2),
        'built_in_equity': round(built_in_equity, 2),
        'equity_pct': round(equity_pct, 2),
        'desired_equity_margin_pct': round(desired_equity_margin * 100, 1),
        'cap_rate': round(market_cap_rate * 100, 2),
        'gross_yield': round(gross_yield, 2),
        'monthly_cashflow_estimate': round(monthly_cashflow_estimate, 2),
        'cost_per_sqft': round(cost_per_sqft, 2),
        'total_cost': round(total_cost, 2),
        'is_deal_viable': maximum_land_value > 0,
    }


# ── 1E. Commercial ──
def calculate_commercial(inputs):
    purchase_price = safe_float(inputs.get('purchase_price'))
    noi = safe_float(inputs.get('noi'))
    cap_rate_input = safe_float(inputs.get('cap_rate'))
    vacancy_rate = safe_float(inputs.get('vacancy_rate'), 5)
    gross_income = safe_float(inputs.get('gross_income'))
    operating_expenses = safe_float(inputs.get('operating_expenses'))
    loan_amount = safe_float(inputs.get('loan_amount'))
    interest_rate = safe_float(inputs.get('interest_rate'), 6)
    loan_term_years = safe_float(inputs.get('loan_term_years'), 25)
    down_payment = purchase_price - loan_amount

    actual_noi = noi if noi > 0 else (
        gross_income * (1 - vacancy_rate / 100)
    ) - operating_expenses
    cap_rate = (actual_noi / purchase_price * 100) if purchase_price > 0 else cap_rate_input
    grm = (purchase_price / gross_income) if gross_income > 0 else 0

    monthly_rate = interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    if monthly_rate > 0 and loan_amount > 0:
        mortgage_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** n_payments
        ) / ((1 + monthly_rate) ** n_payments - 1)
    else:
        mortgage_payment = 0

    annual_debt_service = mortgage_payment * 12
    cash_flow = actual_noi - annual_debt_service
    coc_return = (cash_flow / down_payment * 100) if down_payment > 0 else 0
    dscr = (actual_noi / annual_debt_service) if annual_debt_service > 0 else 0

    irr_5yr = _estimate_irr_5yr(
        down_payment, cash_flow,
        purchase_price, actual_noi, cap_rate
    )

    return {
        'noi': round(actual_noi, 2),
        'cap_rate': round(cap_rate, 2),
        'grm': round(grm, 2),
        'cash_flow': round(cash_flow, 2),
        'coc_return': round(coc_return, 2),
        'dscr': round(dscr, 2),
        'mortgage_payment': round(mortgage_payment, 2),
        'annual_debt_service': round(annual_debt_service, 2),
        'irr_5yr': round(irr_5yr, 2),
        'down_payment': round(down_payment, 2),
    }


def _estimate_irr_5yr(initial_investment, annual_cashflow, purchase_price, noi, cap_rate):
    if initial_investment <= 0:
        return 0
    appreciation_rate = 0.03
    exit_value = purchase_price * (1 + appreciation_rate) ** 5
    total_cashflow = annual_cashflow * 5
    total_return = total_cashflow + exit_value - initial_investment
    simple_irr = (total_return / initial_investment / 5) * 100
    return max(0, simple_irr)