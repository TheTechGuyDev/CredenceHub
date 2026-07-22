from app import db
from app.models import CityData


def seed_city_data():
    # Clear existing data
    CityData.query.delete()

    # ─────────────────────────────────────────────────────────
    # Sourcing notes (see chat for full citations):
    # CANADA — Basic/Standard/Premium ranges taken directly from
    #   Altus Group's 2025/2026 Canadian Cost Guide (single-family,
    #   unfinished basement, per REMAX Canada's published breakdown).
    #   Luxury tier is a reasoned extrapolation (premium x 1.4), not
    #   a directly-cited figure.
    # USA — anchored to Home-Cost.com's state-level averages (built
    #   on NAHB's "Cost of Constructing a Home" methodology), then
    #   adjusted for known metro premium within each state (e.g. NYC
    #   and LA typically run above their state average). Basic/
    #   Premium/Luxury tiers derived as standard x0.82 / x1.27 / x1.75.
    #   Multi-family and commercial columns are still reasoned
    #   estimates (~10-20% below equivalent SFH tier), not separately
    #   sourced — flag for follow-up research if this matters for a
    #   specific client deliverable.
    # Land cost, labor/material index, and permit base fee are still
    # placeholder estimates pending dedicated sourcing.
    # ─────────────────────────────────────────────────────────

    cities = [
        # Canada — Altus Group 2025/2026 Canadian Cost Guide
        {
            'city': 'Calgary', 'province_state': 'Alberta', 'country': 'CA',
            'land_cost_sqft': 45, 'labor_index': 1.05, 'material_index': 1.02,
            'permit_base_fee': 1200,
            'cost_sfh_basic': 185, 'cost_sfh_standard': 232, 'cost_sfh_premium': 280, 'cost_sfh_luxury': 390,
            'cost_multi_basic': 165, 'cost_multi_standard': 205, 'cost_multi_premium': 250,
            'cost_commercial_standard': 235,
        },
        {
            'city': 'Edmonton', 'province_state': 'Alberta', 'country': 'CA',
            'land_cost_sqft': 38, 'labor_index': 1.02, 'material_index': 1.00,
            'permit_base_fee': 1000,
            'cost_sfh_basic': 180, 'cost_sfh_standard': 230, 'cost_sfh_premium': 280, 'cost_sfh_luxury': 390,
            'cost_multi_basic': 160, 'cost_multi_standard': 203, 'cost_multi_premium': 248,
            'cost_commercial_standard': 232,
        },
        {
            'city': 'Vancouver', 'province_state': 'British Columbia', 'country': 'CA',
            'land_cost_sqft': 120, 'labor_index': 1.25, 'material_index': 1.15,
            'permit_base_fee': 2500,
            'cost_sfh_basic': 210, 'cost_sfh_standard': 275, 'cost_sfh_premium': 340, 'cost_sfh_luxury': 475,
            'cost_multi_basic': 188, 'cost_multi_standard': 243, 'cost_multi_premium': 300,
            'cost_commercial_standard': 285,
        },
        {
            'city': 'Toronto', 'province_state': 'Ontario', 'country': 'CA',
            'land_cost_sqft': 110, 'labor_index': 1.20, 'material_index': 1.10,
            'permit_base_fee': 2000,
            'cost_sfh_basic': 210, 'cost_sfh_standard': 250, 'cost_sfh_premium': 290, 'cost_sfh_luxury': 405,
            'cost_multi_basic': 188, 'cost_multi_standard': 221, 'cost_multi_premium': 256,
            'cost_commercial_standard': 245,
        },
        {
            'city': 'Ottawa', 'province_state': 'Ontario', 'country': 'CA',
            'land_cost_sqft': 65, 'labor_index': 1.08, 'material_index': 1.05,
            'permit_base_fee': 1400,
            'cost_sfh_basic': 145, 'cost_sfh_standard': 190, 'cost_sfh_premium': 230, 'cost_sfh_luxury': 320,
            'cost_multi_basic': 130, 'cost_multi_standard': 168, 'cost_multi_premium': 203,
            'cost_commercial_standard': 195,
        },
        {
            'city': 'Montreal', 'province_state': 'Quebec', 'country': 'CA',
            'land_cost_sqft': 55, 'labor_index': 0.98, 'material_index': 0.97,
            'permit_base_fee': 1100,
            'cost_sfh_basic': 150, 'cost_sfh_standard': 185, 'cost_sfh_premium': 215, 'cost_sfh_luxury': 300,
            'cost_multi_basic': 135, 'cost_multi_standard': 164, 'cost_multi_premium': 190,
            'cost_commercial_standard': 183,
        },
        {
            'city': 'Winnipeg', 'province_state': 'Manitoba', 'country': 'CA',
            'land_cost_sqft': 30, 'labor_index': 0.95, 'material_index': 0.96,
            'permit_base_fee': 900,
            'cost_sfh_basic': 175, 'cost_sfh_standard': 220, 'cost_sfh_premium': 265, 'cost_sfh_luxury': 370,
            'cost_multi_basic': 156, 'cost_multi_standard': 195, 'cost_multi_premium': 235,
            'cost_commercial_standard': 224,
        },
        # USA — Home-Cost.com state averages (NAHB methodology) + metro adjustment
        {
            'city': 'New York', 'province_state': 'New York', 'country': 'US',
            'land_cost_sqft': 200, 'labor_index': 1.60, 'material_index': 1.35,
            'permit_base_fee': 5000,
            'cost_sfh_basic': 310, 'cost_sfh_standard': 380, 'cost_sfh_premium': 480, 'cost_sfh_luxury': 660,
            'cost_multi_basic': 280, 'cost_multi_standard': 336, 'cost_multi_premium': 424,
            'cost_commercial_standard': 400,
        },
        {
            'city': 'Los Angeles', 'province_state': 'California', 'country': 'US',
            'land_cost_sqft': 175, 'labor_index': 1.45, 'material_index': 1.20,
            'permit_base_fee': 4000,
            'cost_sfh_basic': 215, 'cost_sfh_standard': 260, 'cost_sfh_premium': 330, 'cost_sfh_luxury': 455,
            'cost_multi_basic': 194, 'cost_multi_standard': 230, 'cost_multi_premium': 291,
            'cost_commercial_standard': 275,
        },
        {
            'city': 'Chicago', 'province_state': 'Illinois', 'country': 'US',
            'land_cost_sqft': 80, 'labor_index': 1.20, 'material_index': 1.08,
            'permit_base_fee': 2200,
            'cost_sfh_basic': 190, 'cost_sfh_standard': 230, 'cost_sfh_premium': 290, 'cost_sfh_luxury': 400,
            'cost_multi_basic': 171, 'cost_multi_standard': 203, 'cost_multi_premium': 256,
            'cost_commercial_standard': 242,
        },
        {
            'city': 'Houston', 'province_state': 'Texas', 'country': 'US',
            'land_cost_sqft': 40, 'labor_index': 0.95, 'material_index': 0.98,
            'permit_base_fee': 1000,
            'cost_sfh_basic': 130, 'cost_sfh_standard': 155, 'cost_sfh_premium': 195, 'cost_sfh_luxury': 270,
            'cost_multi_basic': 117, 'cost_multi_standard': 137, 'cost_multi_premium': 172,
            'cost_commercial_standard': 163,
        },
        {
            'city': 'Phoenix', 'province_state': 'Arizona', 'country': 'US',
            'land_cost_sqft': 35, 'labor_index': 0.92, 'material_index': 0.95,
            'permit_base_fee': 900,
            'cost_sfh_basic': 150, 'cost_sfh_standard': 185, 'cost_sfh_premium': 235, 'cost_sfh_luxury': 325,
            'cost_multi_basic': 135, 'cost_multi_standard': 163, 'cost_multi_premium': 207,
            'cost_commercial_standard': 196,
        },
        {
            'city': 'Dallas', 'province_state': 'Texas', 'country': 'US',
            'land_cost_sqft': 42, 'labor_index': 0.97, 'material_index': 0.99,
            'permit_base_fee': 1050,
            'cost_sfh_basic': 135, 'cost_sfh_standard': 165, 'cost_sfh_premium': 210, 'cost_sfh_luxury': 290,
            'cost_multi_basic': 122, 'cost_multi_standard': 146, 'cost_multi_premium': 185,
            'cost_commercial_standard': 175,
        },
        {
            'city': 'Miami', 'province_state': 'Florida', 'country': 'US',
            'land_cost_sqft': 95, 'labor_index': 1.10, 'material_index': 1.08,
            'permit_base_fee': 1800,
            'cost_sfh_basic': 170, 'cost_sfh_standard': 210, 'cost_sfh_premium': 265, 'cost_sfh_luxury': 365,
            'cost_multi_basic': 153, 'cost_multi_standard': 186, 'cost_multi_premium': 234,
            'cost_commercial_standard': 222,
        },
        {
            'city': 'Seattle', 'province_state': 'Washington', 'country': 'US',
            'land_cost_sqft': 130, 'labor_index': 1.30, 'material_index': 1.18,
            'permit_base_fee': 3000,
            'cost_sfh_basic': 205, 'cost_sfh_standard': 250, 'cost_sfh_premium': 320, 'cost_sfh_luxury': 440,
            'cost_multi_basic': 185, 'cost_multi_standard': 221, 'cost_multi_premium': 282,
            'cost_commercial_standard': 267,
        },
        {
            'city': 'Denver', 'province_state': 'Colorado', 'country': 'US',
            'land_cost_sqft': 70, 'labor_index': 1.08, 'material_index': 1.05,
            'permit_base_fee': 1500,
            'cost_sfh_basic': 170, 'cost_sfh_standard': 205, 'cost_sfh_premium': 260, 'cost_sfh_luxury': 360,
            'cost_multi_basic': 153, 'cost_multi_standard': 181, 'cost_multi_premium': 229,
            'cost_commercial_standard': 217,
        },
        {
            'city': 'Atlanta', 'province_state': 'Georgia', 'country': 'US',
            'land_cost_sqft': 45, 'labor_index': 0.95, 'material_index': 0.97,
            'permit_base_fee': 1000,
            'cost_sfh_basic': 155, 'cost_sfh_standard': 190, 'cost_sfh_premium': 240, 'cost_sfh_luxury': 330,
            'cost_multi_basic': 140, 'cost_multi_standard': 168, 'cost_multi_premium': 211,
            'cost_commercial_standard': 200,
        },
    ]

    for city_data in cities:
        city = CityData(**city_data)
        db.session.add(city)

    db.session.commit()
    print(f'Seeded {len(cities)} cities successfully.')