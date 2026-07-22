"""
CredenceHub — PDF Report Generation

Two branded, print-ready PDF exports built with ReportLab:
  - generate_construction_pdf(): Construction Cost report (Bill of Materials,
    permits, cost summary, cost breakdown chart) — mirrors the on-screen
    Cost Summary tab and the public shared report.
  - generate_deal_pdf(): Project Analysis report (key metrics, deal inputs,
    profit/results breakdown) for any of the 6 strategies.

Both return a BytesIO buffer ready to be sent with Flask's send_file().
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend

# ── Brand palette ──
NAVY = colors.HexColor('#0F2D5E')
GOLD = colors.HexColor('#F5A623')
GREEN = colors.HexColor('#38A169')
BLUE = colors.HexColor('#3182CE')
GRAY = colors.HexColor('#718096')
TEXT_MUTED = colors.HexColor('#718096')
TEXT_PRIMARY = colors.HexColor('#1A202C')
BORDER = colors.HexColor('#E2E8F0')
BG_LIGHT = colors.HexColor('#F7FAFC')

styles = getSampleStyleSheet()

style_title = ParagraphStyle('CHTitle', parent=styles['Heading1'], fontSize=20, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold')
style_subtitle = ParagraphStyle('CHSubtitle', parent=styles['Normal'], fontSize=10, textColor=TEXT_MUTED, spaceAfter=2)
style_section = ParagraphStyle('CHSection', parent=styles['Heading2'], fontSize=13, textColor=NAVY, spaceBefore=14, spaceAfter=8, fontName='Helvetica-Bold')
style_kpi_label = ParagraphStyle('CHKpiLabel', parent=styles['Normal'], fontSize=8, textColor=TEXT_MUTED, fontName='Helvetica-Bold')
style_kpi_value = ParagraphStyle('CHKpiValue', parent=styles['Normal'], fontSize=16, textColor=NAVY, fontName='Helvetica-Bold', spaceBefore=3)
style_disclaimer = ParagraphStyle('CHDisclaimer', parent=styles['Normal'], fontSize=8, textColor=TEXT_MUTED, leading=11)
style_cell = ParagraphStyle('CHCell', parent=styles['Normal'], fontSize=9, textColor=TEXT_PRIMARY)


def _fmt_currency(value):
    try:
        return f"${value:,.0f}"
    except (TypeError, ValueError):
        return "$0"


def _fmt_pct(value):
    try:
        return f"{value:.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def _footer(canvas, doc, report_type):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(0.75 * inch, 0.5 * inch, f"CredenceHub — Real Estate Investment & Construction Analysis")
    canvas.drawRightString(doc.pagesize[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _letterhead(title, subtitle_line, right_lines):
    """Top banner: logo mark, title/subtitle on the left, meta info on the right, gold divider."""
    logo_cell = Table([[Paragraph('<b>CH</b>', ParagraphStyle('logo', fontSize=13, textColor=colors.white, alignment=TA_CENTER))]],
                       colWidths=[0.4 * inch], rowHeights=[0.4 * inch])
    logo_cell.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    title_block = [Paragraph(title, style_title)]
    if subtitle_line:
        title_block.append(Paragraph(subtitle_line, style_subtitle))

    right_block = [Paragraph(line, ParagraphStyle('meta', fontSize=9, textColor=TEXT_MUTED, alignment=TA_RIGHT)) for line in right_lines]

    header_table = Table(
        [[logo_cell, title_block, right_block]],
        colWidths=[0.55 * inch, 4.2 * inch, 2.25 * inch]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))

    divider = HRFlowable(width='100%', thickness=3, color=GOLD, spaceBefore=8, spaceAfter=14)
    return [header_table, divider]


def _kpi_row(items):
    """items: list of (label, value_string) — rendered as bordered cards in a single row."""
    cells = []
    for label, value in items:
        cell_content = [
            Paragraph(label.upper(), style_kpi_label),
            Paragraph(value, style_kpi_value),
        ]
        cells.append(cell_content)
    width = 6.9 / len(items)
    t = Table([cells], colWidths=[width * inch] * len(items))
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.75, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def _pie_chart(labels, values, chart_colors):
    drawing = Drawing(220, 160)
    pie = Pie()
    pie.x = 15
    pie.y = 15
    pie.width = 110
    pie.height = 110
    pie.data = [max(v, 0.01) for v in values]
    pie.labels = None
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = colors.white
    for i, c in enumerate(chart_colors):
        pie.slices[i].fillColor = c

    legend = Legend()
    legend.x = 140
    legend.y = 100
    legend.dx = 8
    legend.dy = 8
    legend.fontName = 'Helvetica'
    legend.fontSize = 8
    legend.colorNamePairs = list(zip(chart_colors, labels))

    drawing.add(pie)
    drawing.add(legend)
    return drawing


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION COST REPORT
# ═══════════════════════════════════════════════════════════

def generate_construction_pdf(project, summary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title=f"{project.name} - Construction Cost Report"
    )

    elements = []
    subtitle = (
        f"{project.building_type.replace('_', ' ').title()} — "
        f"{project.city}, {project.province_state}, {project.country} — "
        f"{project.floor_area_sqft:,.0f} sq ft — {project.finish_level.title()} Finish"
    )
    elements += _letterhead(
        project.name, subtitle,
        ["Generated", datetime.utcnow().strftime('%B %d, %Y'), "Powered by CredenceHub"]
    )

    # KPI row
    elements.append(_kpi_row([
        ('Total Project Cost', _fmt_currency(summary['grand_total'])),
        ('Cost Per Sq Ft', f"${summary['cost_per_sqft']:,.0f}/sqft"),
        ('Hard Costs', _fmt_currency(summary['hard_costs'])),
        ('Soft Costs', _fmt_currency(summary['soft_costs'])),
    ]))
    elements.append(Spacer(1, 16))

    # Bill of Materials
    elements.append(Paragraph('Bill of Materials', style_section))
    for category_name, category_data in summary['categories'].items():
        cat_header = Table(
            [[Paragraph(f"<b><font color='white'>{category_name}</font></b>", style_cell),
              Paragraph(f"<b><font color='#F5A623'>{_fmt_currency(category_data['subtotal'])}</font></b>",
                        ParagraphStyle('sub', parent=style_cell, alignment=TA_RIGHT))]],
            colWidths=[4.9 * inch, 2.0 * inch]
        )
        cat_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NAVY),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))

        rows = [['Item', 'Qty', 'Unit', 'Unit Cost', 'Total']]
        for item in category_data['bom_items']:
            rows.append([
                item.name, f"{item.quantity:,.1f}", item.unit,
                f"${item.unit_cost:,.2f}", _fmt_currency(item.quantity * item.unit_cost)
            ])
        item_table = Table(rows, colWidths=[2.5 * inch, 0.9 * inch, 0.9 * inch, 1.2 * inch, 1.4 * inch])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_LIGHT),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, 0), TEXT_MUTED),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(KeepTogether([cat_header, item_table, Spacer(1, 10)]))

    # Permits table
    elements.append(Paragraph('Permits &amp; Required Documents', style_section))
    permit_rows = [['Permit', 'Est. Fee', 'Processing', 'Status']]
    for p in summary['permit_items']:
        permit_rows.append([
            p.name, _fmt_currency(p.estimated_fee), p.processing_time,
            'Required' if p.is_required else 'Optional'
        ])
    permit_table = Table(permit_rows, colWidths=[2.8 * inch, 1.1 * inch, 1.7 * inch, 1.2 * inch])
    permit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(permit_table)
    elements.append(Spacer(1, 16))

    # Cost summary + chart side by side
    summary_rows = [
        ['Land Cost', _fmt_currency(summary['land_cost'])],
        ['Materials', _fmt_currency(summary['total_materials'])],
        ['Labour (est.)', _fmt_currency(summary['labor_cost'])],
        ['Permits & Fees', _fmt_currency(summary['soft_costs'])],
        ['Contingency', _fmt_currency(summary['contingency'])],
    ]
    summary_table = Table(summary_rows, colWidths=[1.8 * inch, 1.3 * inch])
    summary_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    grand_total_row = Table([['Grand Total', _fmt_currency(summary['grand_total'])]], colWidths=[1.8 * inch, 1.3 * inch])
    grand_total_row.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('TEXTCOLOR', (1, 0), (1, 0), GOLD),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    chart = _pie_chart(
        ['Land', 'Materials', 'Labour', 'Permits', 'Contingency'],
        [summary['land_cost'], summary['total_materials'], summary['labor_cost'], summary['soft_costs'], summary['contingency']],
        [NAVY, GOLD, GREEN, BLUE, GRAY]
    )

    side_by_side = Table(
        [[[summary_table, Spacer(1, 4), grand_total_row], chart]],
        colWidths=[3.2 * inch, 3.5 * inch]
    )
    side_by_side.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(side_by_side)
    elements.append(Spacer(1, 14))

    # Disclaimer
    elements.append(Paragraph(
        "<b>Disclaimer:</b> These estimates are based on regional cost benchmarks and are intended as "
        "planning guides only. Actual costs may vary based on market conditions, contractor pricing, and "
        "site-specific factors. Always obtain multiple contractor quotes before committing to a project budget.",
        style_disclaimer
    ))

    doc.build(elements, onFirstPage=lambda c, d: _footer(c, d, 'construction'),
               onLaterPages=lambda c, d: _footer(c, d, 'construction'))
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════════════
# PROJECT (DEAL) ANALYSIS REPORT
# ═══════════════════════════════════════════════════════════

# Human-readable labels for known input/output keys across all 6 strategies.
# Anything not listed here falls back to a title-cased version of the key.
LABEL_OVERRIDES = {
    'arv': 'After Repair Value (ARV)', 'mao': 'Max Allowable Offer (MAO)',
    'mao_70': 'MAO at 70% Rule', 'mao_75': 'MAO at 75% Rule', 'mao_80': 'MAO at 80% Rule',
    'mao_check_70': 'MAO Check (70% Rule)', 'roi': 'ROI', 'coc_return': 'Cash-on-Cash Return',
    'noi': 'Net Operating Income', 'ltv': 'Loan-to-Value', 'dscr': 'DSCR',
    'grm': 'Gross Rent Multiplier', 'irr_5yr': '5-Year IRR', 'mlv': 'Maximum Land Value (MLV)',
    'rehab_cost': 'Renovation Cost', 'arv_land': 'Land ARV',
}

RESULTS_BY_STRATEGY = {
    'fix_flip': [
        ('Projected Profit', 'profit', True, True), ('Total Investment', 'total_investment', True, False),
        ('ROI', 'roi', False, False), ('Annualized ROI', 'annualized_roi', False, False),
        ('Cash-on-Cash Return', 'coc_return', False, False), ('Break-Even ARV', 'break_even_arv', True, False),
        ('MAO Check (70% Rule)', 'mao_check_70', True, False), ('Selling Costs', 'selling_costs', True, False),
        ('Holding Costs', 'holding_costs', True, False),
    ],
    'brrrr': [
        ('Refinance Amount', 'refinance_amount', True, False), ('Capital Recycled', 'capital_recycled', True, True),
        ('Capital Left In Deal', 'capital_left_in', True, False), ('Equity In Deal', 'equity_in_deal', True, True),
        ('Mortgage Payment', 'mortgage_payment', True, False), ('Monthly Cash Flow', 'monthly_cashflow', True, True),
        ('Annual Cash Flow', 'annual_cashflow', True, False), ('Cash-on-Cash Return', 'coc_return', False, False),
        ('Gross Yield', 'gross_yield', False, False),
    ],
    'construction': [
        ('Maximum Land Value (MLV)', 'maximum_land_value', True, True), ('Max Allowable Offer (MAO)', 'mao', True, True),
        ('Adjusted ARV', 'adjusted_arv', True, False), ('Developer Profit', 'developer_profit', True, True),
        ('Actual Profit Margin', 'actual_profit_margin', False, False), ('Target Profit Margin', 'target_profit_margin_pct', False, False),
        ('ROI', 'roi', False, False), ('Total Project Cost', 'total_cost', True, False),
        ('Selling Costs', 'selling_costs', True, False), ('Contingency', 'contingency', True, False),
        ('Cost Per Sq Ft', 'cost_per_sqft', True, False),
    ],
    'infill': [
        ('Maximum Land Value (MLV)', 'maximum_land_value', True, True), ('Max Allowable Offer (MAO)', 'mao', True, True),
        ('Adjusted ARV', 'adjusted_arv', True, False), ('Developer Profit', 'developer_profit', True, True),
        ('Actual Profit Margin', 'actual_profit_margin', False, False), ('Target Profit Margin', 'target_profit_margin_pct', False, False),
        ('ROI', 'roi', False, False), ('Total Project Cost', 'total_cost', True, False),
        ('Selling Costs', 'selling_costs', True, False), ('Contingency', 'contingency', True, False),
        ('Cost Per Sq Ft', 'cost_per_sqft', True, False),
    ],
    'commercial': [
        ('Net Operating Income', 'noi', True, False), ('Cap Rate', 'cap_rate', False, True),
        ('Cash Flow', 'cash_flow', True, True), ('Cash-on-Cash Return', 'coc_return', False, False),
        ('Gross Rent Multiplier', 'grm', False, False), ('DSCR', 'dscr', False, False),
        ('Mortgage Payment', 'mortgage_payment', True, False), ('Annual Debt Service', 'annual_debt_service', True, False),
        ('5-Year IRR', 'irr_5yr', False, True),
    ],
}


def _wholesale_results(outputs):
    if outputs.get('deal_type') == 'land':
        return [
            ('Maximum Land Value (MLV)', 'maximum_land_value', True, True), ('Max Allowable Offer (MAO)', 'mao', True, True),
            ('Your Assignment Fee', 'wholesale_profit', True, True), ('Developer Projected Profit', 'developer_profit', True, False),
            ('Selling Costs', 'selling_costs', True, False), ('Total Developer Costs', 'total_developer_costs', True, False),
        ]
    return [
        ('Your Assignment Profit', 'wholesale_profit', True, True), ('MAO at 70% Rule', 'mao_70', True, True),
        ('MAO at 75% Rule', 'mao_75', True, False), ('MAO at 80% Rule', 'mao_80', True, False),
        ('Buyer All-In Cost', 'buyer_all_in', True, False), ('Buyer Projected Profit', 'buyer_profit', True, True),
        ('Buyer ROI', 'buyer_roi', False, False), ('Deal Spread', 'spread', True, False),
    ]


def _results_for_strategy(strategy, outputs):
    if strategy == 'wholesale':
        return _wholesale_results(outputs)
    if strategy == 'construction' and outputs.get('exit_strategy') == 'build_to_rent':
        return [
            ('NOI (Annual)', 'noi', True, True), ('As-Built Value', 'as_built_value', True, True),
            ('Maximum Land Value (MLV)', 'maximum_land_value', True, True), ('Max Allowable Offer (MAO)', 'mao', True, True),
            ('Built-In Equity', 'built_in_equity', True, True), ('Equity Position', 'equity_pct', False, False),
            ('Cap Rate', 'cap_rate', False, False), ('Gross Yield', 'gross_yield', False, False),
            ('Monthly Cash Flow Est.', 'monthly_cashflow_estimate', True, False), ('Cost Per Sq Ft', 'cost_per_sqft', True, False),
        ]
    return RESULTS_BY_STRATEGY.get(strategy, [])


def _label_for_key(key):
    if key in LABEL_OVERRIDES:
        return LABEL_OVERRIDES[key]
    return key.replace('_', ' ').title()


def generate_deal_pdf(deal, inputs, outputs, prepared_by=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title=f"{deal.name} - {deal.strategy.replace('_', ' ').title()} Analysis"
    )

    elements = []
    location = ', '.join([p for p in [deal.address, deal.city, deal.province_state] if p])
    subtitle = f"{location + ' — ' if location else ''}{deal.status.title()} — {deal.strategy.replace('_', ' ').title()}"
    right_lines = ["Generated", datetime.utcnow().strftime('%B %d, %Y')]
    if prepared_by:
        right_lines.append(f"Prepared by {prepared_by}")

    elements += _letterhead(
        f"{deal.strategy.replace('_', ' ').title()} Analysis", subtitle, right_lines
    )
    elements.append(Paragraph(f"<b>{deal.name}</b>", ParagraphStyle('dealname', fontSize=13, textColor=TEXT_PRIMARY, spaceAfter=10)))

    results = _results_for_strategy(deal.strategy, outputs)

    # Key metrics: first 3 highlighted results become the KPI row (falls back gracefully if fewer than 3)
    highlighted = [(label, key) for label, key, is_currency, is_highlight in results if is_highlight]
    kpi_source = (highlighted + [(l, k) for l, k, c, h in results])[:3]
    kpi_items = []
    for label, key in kpi_source:
        value = outputs.get(key, 0)
        is_currency = next((c for l, k, c, h in results if k == key), True)
        kpi_items.append((label, _fmt_currency(value) if is_currency else _fmt_pct(value)))
    if kpi_items:
        elements.append(Paragraph('Key Metrics', style_section))
        elements.append(_kpi_row(kpi_items))
        elements.append(Spacer(1, 14))

    # Deal Inputs table — every non-empty input, human-readable label
    elements.append(Paragraph('Deal Inputs', style_section))
    input_rows = [['Input', 'Value']]
    for key, value in inputs.items():
        if value in (None, '', 0) and key not in ('assignment_fee', 'land_cost'):
            continue
        display_value = f"${value:,.0f}" if isinstance(value, (int, float)) and abs(value) >= 100 else str(value)
        input_rows.append([_label_for_key(key), display_value])
    if len(input_rows) == 1:
        input_rows.append(['—', '—'])
    input_table = Table(input_rows, colWidths=[3.5 * inch, 3.4 * inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 16))

    # Profit / Results Breakdown
    elements.append(Paragraph('Profit Breakdown', style_section))
    result_rows = [['Item', 'Amount']]
    for label, key, is_currency, is_highlight in results:
        value = outputs.get(key, 0)
        result_rows.append([label, _fmt_currency(value) if is_currency else _fmt_pct(value)])
    result_table = Table(result_rows, colWidths=[3.5 * inch, 3.4 * inch])
    row_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    for i, (label, key, is_currency, is_highlight) in enumerate(results, start=1):
        if is_highlight:
            row_styles.append(('BACKGROUND', (0, i), (-1, i), BG_LIGHT))
            row_styles.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
    result_table.setStyle(TableStyle(row_styles))
    elements.append(result_table)
    elements.append(Spacer(1, 16))

    if deal.notes:
        elements.append(Paragraph('Notes', style_section))
        elements.append(Paragraph(deal.notes, style_cell))

    doc.build(elements, onFirstPage=lambda c, d: _footer(c, d, 'deal'),
               onLaterPages=lambda c, d: _footer(c, d, 'deal'))
    buffer.seek(0)
    return buffer