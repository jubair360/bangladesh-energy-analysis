-- Load the two Our World in Data files and keep only the four countries and years we study.
CREATE OR REPLACE TABLE energy AS
SELECT country, year,
       electricity_generation            AS generation_twh,
       per_capita_electricity            AS kwh_per_person,
       gas_share_elec   AS gas_pct,  coal_share_elec AS coal_pct, oil_share_elec AS oil_pct,
       hydro_share_elec AS hydro_pct, solar_share_elec AS solar_pct, wind_share_elec AS wind_pct,
       nuclear_share_elec AS nuclear_pct, renewables_share_elec AS renewables_pct,
       low_carbon_share_elec AS low_carbon_pct,
       carbon_intensity_elec AS g_co2_per_kwh,
       net_elec_imports_share_demand AS imports_pct_of_demand
FROM read_csv_auto('data/owid-energy-data.csv')
WHERE country IN ('Bangladesh', 'India', 'Pakistan', 'Vietnam') AND year BETWEEN 2000 AND 2025;

CREATE OR REPLACE TABLE emissions AS
SELECT country, year, co2 AS co2_mt, co2_per_capita AS co2_t_per_person, population
FROM read_csv_auto('data/owid-co2-data.csv')
WHERE country IN ('Bangladesh', 'India', 'Pakistan', 'Vietnam') AND year BETWEEN 2000 AND 2025;
