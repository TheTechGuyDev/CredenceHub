# ─────────────────────────────────────────
# CREDENCEHUB — DEAL CALCULATORS
# All 5 strategies: Wholesale, Fix & Flip,
# BRRRR, New Construction, Commercial
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
def calculate_wholesale(inputs):
    purchase_price = safe_float(inputs.get('purchase_price'))
    assignment_fee = safe_float(inputs.get('assignment_fee'))
    arv = safe_float(inputs.get('arv'))
    repair_cost = safe_float(inputs.get('repair_cost'))
    closing_costs = safe_float(inputs.get('closing_costs'), 3000)
    buyer_profit_pct = safe_float(inputs.get('buyer_profit_pct'), 20)

    max_offer_70 = (arv * 0.70) - repair_cost
    max_offer_75 = (arv * 0.75) - repair_cost
    wholesale_profit = assignment_fee
    buyer_purchase = purchase_price + assignment_fee
    buyer_all_in = buyer_purchase + repair_cost + closing_costs
    buyer_profit = arv - buyer_all_in
    buyer_roi = (buyer_profit / buyer_all_in * 100) if buyer_all_in > 0 else 0

    return {
        'wholesale_profit': round(wholesale_profit, 2),
        'max_offer_70': round(max_offer_70, 2),
        'max_offer_75': round(max_offer_75, 2),
        'buyer_all_in': round(buyer_all_in, 2),
        'buyer_profit': round(buyer_profit, 2),
        'buyer_roi': round(buyer_roi, 2),
        'spread': round(arv - purchase_price - repair_cost, 2),
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
    capital_left_in = total_invested - refinance_amount
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
    }


# ── 1D. New Construction ──
def calculate_construction(inputs):
    land_cost = safe_float(inputs.get('land_cost'))
    construction_cost = safe_float(inputs.get('construction_cost'))
    soft_costs = safe_float(inputs.get('soft_costs'))
    financing_costs = safe_float(inputs.get('financing_costs'))
    arv = safe_float(inputs.get('arv'))
    floor_area = safe_float(inputs.get('floor_area'), 1)
    contingency_pct = safe_float(inputs.get('contingency_pct'), 10)

    hard_costs = construction_cost
    contingency = (hard_costs + soft_costs) * (contingency_pct / 100)
    total_cost = land_cost + hard_costs + soft_costs + financing_costs + contingency
    profit = arv - total_cost
    roi = (profit / total_cost * 100) if total_cost > 0 else 0
    cost_per_sqft = total_cost / floor_area if floor_area > 0 else 0
    profit_margin = (profit / arv * 100) if arv > 0 else 0

    return {
        'total_cost': round(total_cost, 2),
        'profit': round(profit, 2),
        'roi': round(roi, 2),
        'cost_per_sqft': round(cost_per_sqft, 2),
        'profit_margin': round(profit_margin, 2),
        'contingency': round(contingency, 2),
        'hard_costs': round(hard_costs, 2),
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

    actual_noi = noi if noi > 0 else (gross_income * (1 - vacancy_rate / 100)) - operating_expenses
    cap_rate = (actual_noi / purchase_price * 100) if purchase_price > 0 else cap_rate_input
    grm = (purchase_price / (gross_income or 1)) if gross_income > 0 else 0

    monthly_rate = interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    if monthly_rate > 0 and loan_amount > 0:
        mortgage_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / \
                           ((1 + monthly_rate) ** n_payments - 1)
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