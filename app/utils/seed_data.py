from app import db
from app.models import CityData


def seed_city_data():
    # Clear existing data
    CityData.query.delete()

    cities = [
        # Canada
        {
            'city': 'Calgary', 'province_state': 'Alberta', 'country': 'CA',
            'land_cost_sqft': 45, 'labor_index': 1.05, 'material_index': 1.02,
            'permit_base_fee': 1200,
            'cost_sfh_basic': 180, 'cost_sfh_standard': 220, 'cost_sfh_premium': 280, 'cost_sfh_luxury': 380,
            'cost_multi_basic': 160, 'cost_multi_standard': 200, 'cost_multi_premium': 260,
            'cost_commercial_standard': 230,
        },
        {
            'city': 'Edmonton', 'province_state': 'Alberta', 'country': 'CA',
            'land_cost_sqft': 38, 'labor_index': 1.02, 'material_index': 1.00,
            'permit_base_fee': 1000,
            'cost_sfh_basic': 170, 'cost_sfh_standard': 210, 'cost_sfh_premium': 265, 'cost_sfh_luxury': 360,
            'cost_multi_basic': 150, 'cost_multi_standard': 190, 'cost_multi_premium': 245,
            'cost_commercial_standard': 215,
        },
        {
            'city': 'Vancouver', 'province_state': 'British Columbia', 'country': 'CA',
            'land_cost_sqft': 120, 'labor_index': 1.25, 'material_index': 1.15,
            'permit_base_fee': 2500,
            'cost_sfh_basic': 250, 'cost_sfh_standard': 320, 'cost_sfh_premium': 420, 'cost_sfh_luxury': 580,
            'cost_multi_basic': 220, 'cost_multi_standard': 290, 'cost_multi_premium': 390,
            'cost_commercial_standard': 340,
        },
        {
            'city': 'Toronto', 'province_state': 'Ontario', 'country': 'CA',
            'land_cost_sqft': 110, 'labor_index': 1.20, 'material_index': 1.10,
            'permit_base_fee': 2000,
            'cost_sfh_basic': 230, 'cost_sfh_standard': 295, 'cost_sfh_premium': 390, 'cost_sfh_luxury': 540,
            'cost_multi_basic': 205, 'cost_multi_standard': 270, 'cost_multi_premium': 360,
            'cost_commercial_standard': 315,
        },
        {
            'city': 'Ottawa', 'province_state': 'Ontario', 'country': 'CA',
            'land_cost_sqft': 65, 'labor_index': 1.08, 'material_index': 1.05,
            'permit_base_fee': 1400,
            'cost_sfh_basic': 195, 'cost_sfh_standard': 245, 'cost_sfh_premium': 315, 'cost_sfh_luxury': 430,
            'cost_multi_basic': 175, 'cost_multi_standard': 220, 'cost_multi_premium': 285,
            'cost_commercial_standard': 255,
        },
        {
            'city': 'Montreal', 'province_state': 'Quebec', 'country': 'CA',
            'land_cost_sqft': 55, 'labor_index': 0.98, 'material_index': 0.97,
            'permit_base_fee': 1100,
            'cost_sfh_basic': 175, 'cost_sfh_standard': 220, 'cost_sfh_premium': 285, 'cost_sfh_luxury': 390,
            'cost_multi_basic': 155, 'cost_multi_standard': 198, 'cost_multi_premium': 258,
            'cost_commercial_standard': 225,
        },
        {
            'city': 'Winnipeg', 'province_state': 'Manitoba', 'country': 'CA',
            'land_cost_sqft': 30, 'labor_index': 0.95, 'material_index': 0.96,
            'permit_base_fee': 900,
            'cost_sfh_basic': 160, 'cost_sfh_standard': 200, 'cost_sfh_premium': 255, 'cost_sfh_luxury': 345,
            'cost_multi_basic': 142, 'cost_multi_standard': 180, 'cost_multi_premium': 232,
            'cost_commercial_standard': 205,
        },
        # USA
        {
            'city': 'New York', 'province_state': 'New York', 'country': 'US',
            'land_cost_sqft': 200, 'labor_index': 1.60, 'material_index': 1.35,
            'permit_base_fee': 5000,
            'cost_sfh_basic': 320, 'cost_sfh_standard': 420, 'cost_sfh_premium': 560, 'cost_sfh_luxury': 800,
            'cost_multi_basic': 290, 'cost_multi_standard': 380, 'cost_multi_premium': 510,
            'cost_commercial_standard': 450,
        },
        {
            'city': 'Los Angeles', 'province_state': 'California', 'country': 'US',
            'land_cost_sqft': 175, 'labor_index': 1.45, 'material_index': 1.20,
            'permit_base_fee': 4000,
            'cost_sfh_basic': 290, 'cost_sfh_standard': 380, 'cost_sfh_premium': 500, 'cost_sfh_luxury': 700,
            'cost_multi_basic': 265, 'cost_multi_standard': 345, 'cost_multi_premium': 460,
            'cost_commercial_standard': 410,
        },
        {
            'city': 'Chicago', 'province_state': 'Illinois', 'country': 'US',
            'land_cost_sqft': 80, 'labor_index': 1.20, 'material_index': 1.08,
            'permit_base_fee': 2200,
            'cost_sfh_basic': 195, 'cost_sfh_standard': 255, 'cost_sfh_premium': 335, 'cost_sfh_luxury': 460,
            'cost_multi_basic': 175, 'cost_multi_standard': 230, 'cost_multi_premium': 305,
            'cost_commercial_standard': 270,
        },
        {
            'city': 'Houston', 'province_state': 'Texas', 'country': 'US',
            'land_cost_sqft': 40, 'labor_index': 0.95, 'material_index': 0.98,
            'permit_base_fee': 1000,
            'cost_sfh_basic': 150, 'cost_sfh_standard': 190, 'cost_sfh_premium': 245, 'cost_sfh_luxury': 335,
            'cost_multi_basic': 135, 'cost_multi_standard': 172, 'cost_multi_premium': 222,
            'cost_commercial_standard': 200,
        },
        {
            'city': 'Phoenix', 'province_state': 'Arizona', 'country': 'US',
            'land_cost_sqft': 35, 'labor_index': 0.92, 'material_index': 0.95,
            'permit_base_fee': 900,
            'cost_sfh_basic': 145, 'cost_sfh_standard': 185, 'cost_sfh_premium': 240, 'cost_sfh_luxury': 325,
            'cost_multi_basic': 130, 'cost_multi_standard': 167, 'cost_multi_premium': 218,
            'cost_commercial_standard': 195,
        },
        {
            'city': 'Dallas', 'province_state': 'Texas', 'country': 'US',
            'land_cost_sqft': 42, 'labor_index': 0.97, 'material_index': 0.99,
            'permit_base_fee': 1050,
            'cost_sfh_basic': 155, 'cost_sfh_standard': 195, 'cost_sfh_premium': 252, 'cost_sfh_luxury': 342,
            'cost_multi_basic': 138, 'cost_multi_standard': 176, 'cost_multi_premium': 228,
            'cost_commercial_standard': 205,
        },
        {
            'city': 'Miami', 'province_state': 'Florida', 'country': 'US',
            'land_cost_sqft': 95, 'labor_index': 1.10, 'material_index': 1.08,
            'permit_base_fee': 1800,
            'cost_sfh_basic': 200, 'cost_sfh_standard': 260, 'cost_sfh_premium': 340, 'cost_sfh_luxury': 470,
            'cost_multi_basic': 180, 'cost_multi_standard': 235, 'cost_multi_premium': 308,
            'cost_commercial_standard': 278,
        },
        {
            'city': 'Seattle', 'province_state': 'Washington', 'country': 'US',
            'land_cost_sqft': 130, 'labor_index': 1.30, 'material_index': 1.18,
            'permit_base_fee': 3000,
            'cost_sfh_basic': 255, 'cost_sfh_standard': 330, 'cost_sfh_premium': 435, 'cost_sfh_luxury': 600,
            'cost_multi_basic': 230, 'cost_multi_standard': 300, 'cost_multi_premium': 395,
            'cost_commercial_standard': 355,
        },
        {
            'city': 'Denver', 'province_state': 'Colorado', 'country': 'US',
            'land_cost_sqft': 70, 'labor_index': 1.08, 'material_index': 1.05,
            'permit_base_fee': 1500,
            'cost_sfh_basic': 195, 'cost_sfh_standard': 250, 'cost_sfh_premium': 325, 'cost_sfh_luxury': 445,
            'cost_multi_basic': 175, 'cost_multi_standard': 226, 'cost_multi_premium': 295,
            'cost_commercial_standard': 265,
        },
        {
            'city': 'Atlanta', 'province_state': 'Georgia', 'country': 'US',
            'land_cost_sqft': 45, 'labor_index': 0.95, 'material_index': 0.97,
            'permit_base_fee': 1000,
            'cost_sfh_basic': 155, 'cost_sfh_standard': 198, 'cost_sfh_premium': 258, 'cost_sfh_luxury': 350,
            'cost_multi_basic': 138, 'cost_multi_standard': 178, 'cost_multi_premium': 232,
            'cost_commercial_standard': 210,
        },
    ]

    for city_data in cities:
        city = CityData(**city_data)
        db.session.add(city)

    db.session.commit()
    print(f'Seeded {len(cities)} cities successfully.')