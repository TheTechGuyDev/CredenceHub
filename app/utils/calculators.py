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
    }
    calc_fn = calculators.get(strategy)
    if calc_fn:
        return calc_fn(inputs)
    return {}


# ── 1A. Wholesale ──
# Uses industry-standard MAO methodology
def calculate_wholesale(inputs):
    purchase_price = safe_float(inputs.get('purchase_price'))
    assignment_fee = safe_float(inputs.get('assignment_fee'))
    arv = safe_float(inputs.get('arv'))
    repair_cost = safe_float(inputs.get('repair_cost'))
    closing_costs = safe_float(inputs.get('closing_costs'), 3000)
    buyer_profit_pct = safe_float(inputs.get('buyer_profit_pct'), 20)
    deal_type = inputs.get('deal_type', 'rehab')

    if deal_type == 'land':
        # Land Wholesale MAO (Maximum Allowable Offer)
        # Wholesaler assigns a land deal to a developer
        # Developer uses Spec Build methodology
        target_profit_margin = safe_float(inputs.get('target_profit_margin'), 25) / 100
        construction_cost = safe_float(inputs.get('construction_cost'))
        soft_costs = safe_float(inputs.get('soft_costs'))
        holding_costs = safe_float(inputs.get('holding_costs'))
        financing_costs = safe_float(inputs.get('financing_costs'))
        selling_costs_pct = safe_float(inputs.get('selling_costs_pct'), 6) / 100
        selling_costs = arv * selling_costs_pct

        # Maximum Land Value developer can pay
        mlv = (arv * (1 - target_profit_margin)) - construction_cost - soft_costs - holding_costs - financing_costs - selling_costs

        # Wholesaler MAO = MLV - Assignment Fee
        mao = mlv - assignment_fee
        wholesale_profit = assignment_fee
        developer_profit = arv * target_profit_margin
        total_developer_costs = construction_cost + soft_costs + holding_costs + financing_costs + selling_costs + mlv

        return {
            'deal_type': 'land',
            'maximum_land_value': round(max(mlv, 0), 2),
            'mao': round(max(mao, 0), 2),
            'wholesale_profit': round(wholesale_profit, 2),
            'developer_profit': round(developer_profit, 2),
            'selling_costs': round(selling_costs, 2),
            'total_developer_costs': round(total_developer_costs, 2),
            'is_deal_viable': mlv > 0,
            'profit_margin_pct': round(target_profit_margin * 100, 1),
        }

    else:
        # Standard MAO for Fix & Flip wholesale
        # MAO = (ARV x repair_factor) - Repair Cost - Assignment Fee
        mao_70 = (arv * 0.70) - repair_cost - assignment_fee
        mao_75 = (arv * 0.75) - repair_cost - assignment_fee
        mao_80 = (arv * 0.80) - repair_cost - assignment_fee

        # Buyer analysis
        buyer_purchase = purchase_price + assignment_fee
        buyer_all_in = buyer_purchase + repair_cost + closing_costs
        buyer_profit = arv - buyer_all_in
        buyer_roi = (buyer_profit / buyer_all_in * 100) if buyer_all_in > 0 else 0
        buyer_profit_at_70 = arv - ((arv * 0.70) + closing_costs)

        # Wholesale profit
        wholesale_profit = assignment_fee
        spread = arv - purchase_price - repair_cost - closing_costs

        return {
            'deal_type': 'rehab',
            'wholesale_profit': round(wholesale_profit, 2),
            'mao_70': round(max(mao_70, 0), 2),
            'mao_75': round(max(mao_75, 0), 2),
            'mao_80': round(max(mao_80, 0), 2),
            'buyer_all_in': round(buyer_all_in, 2),
            'buyer_profit': round(buyer_profit, 2),
            'buyer_roi': round(buyer_roi, 2),
            'buyer_profit_at_70': round(buyer_profit_at_70, 2),
            'spread': round(spread, 2),
            'is_deal_viable': mao_70 > 0 and buyer_profit > 0,
        }


# ── 1B. Fix & Flip ──
def calculate_fix_flip(inputs):
    purchase_price = safe_float(inputs.get('purchase_price'))
    rehab_cost = safe_float(inputs.get('rehab_cost'))
    arv = safe_float(inputs.get('arv'))
    hold_months = safe_float(inputs.get('hold_months'), 6)
    interest_rate = safe_float(inputs.get('interest_rate'), 0)
    loan_amount = safe_float(inputs.get('loan_amount'), 0)
    selling_costs_pct = safe_float(inputs.get('selling_costs_pct'), 8)
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

    # Industry-standard MAO check
    mao_check_70 = (arv * 0.70) - rehab_cost
    is_good_deal = purchase_price <= mao_check_70

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
        'mao_check_70': round(mao_check_70, 2),
        'is_good_deal': is_good_deal,
    }


# ── 1C. BRRRR ──
def calculate_brrrr(inputs):
    purchase_price = safe_float(inputs.get('purchase_price'))
    rehab_cost = safe_float(inputs.get('rehab_cost'))
    arv = safe_float(inputs.get('arv'))
    refinance_ltv = safe_float(inputs.get('refinance_ltv'), 75)
    monthly_rent = safe_float(inputs.get('monthly_rent'))
    monthly_expenses = safe_float(inputs.get('monthly_expenses'))
    interest_rate = safe_float(inputs.get('interest_rate'), 6)
    loan_term_years = safe_float(inputs.get('loan_term_years'), 25)

    total_invested = purchase_price + rehab_cost
    refinance_amount = arv * (refinance_ltv / 100)
    capital_recycled = refinance_amount
    capital_left_in = max(total_invested - refinance_amount, 0)
    equity_in_deal = arv - refinance_amount

    monthly_rate = interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    if monthly_rate > 0:
        mortgage_payment = refinance_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / \
                           ((1 + monthly_rate) ** n_payments - 1)
    else:
        mortgage_payment = refinance_amount / n_payments if n_payments > 0 else 0

    monthly_cashflow = monthly_rent - monthly_expenses - mortgage_payment
    annual_cashflow = monthly_cashflow * 12
    coc_return = (annual_cashflow / capital_left_in * 100) if capital_left_in > 0 else 0
    gross_yield = (monthly_rent * 12 / arv * 100) if arv > 0 else 0
    infinite_return = capital_left_in <= 0

    return {
        'total_invested': round(total_invested, 2),
        'refinance_amount': round(refinance_amount, 2),
        'capital_recycled': round(capital_recycled, 2),
        'capital_left_in': round(capital_left_in, 2),
        'equity_in_deal': round(equity_in_deal, 2),
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


def _calculate_spec_build(inputs):
    """
    CredenceHub Spec Build (Build and Sell)
    MLV = (ARV x (1 - Target Profit Margin)) - Construction Cost
          - Soft Costs - Holding Costs - Financing Costs - Selling Costs
    MAO = MLV - Assignment Fee (if wholesaling the land)
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

    # Wholesaler MAO = MLV - Assignment Fee
    mao = maximum_land_value - assignment_fee

    return {
        'exit_strategy': 'spec_build',
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