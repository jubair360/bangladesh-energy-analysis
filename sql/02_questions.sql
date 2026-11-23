-- Q1. How much has Bangladesh's electricity grown, and how does per-person use compare?
-- name: q1_growth
SELECT country,
       MAX(generation_twh) FILTER (WHERE year = 2000) AS twh_2000,
       MAX(generation_twh) FILTER (WHERE year = 2025) AS twh_2025,
       ROUND(MAX(generation_twh) FILTER (WHERE year = 2025) /
             MAX(generation_twh) FILTER (WHERE year = 2000), 1) AS growth_x,
       ROUND(MAX(kwh_per_person) FILTER (WHERE year = 2025)) AS kwh_per_person_2025
FROM energy GROUP BY country ORDER BY kwh_per_person_2025;

-- Q2. Has growth slowed? Year-on-year change in Bangladesh's generation.
-- name: q2_bd_yoy
SELECT year, generation_twh,
       ROUND(100 * (generation_twh / LAG(generation_twh) OVER (ORDER BY year) - 1), 1) AS yoy_pct
FROM energy WHERE country = 'Bangladesh' AND year >= 2015 ORDER BY year;

-- Q3. How has Bangladesh's power mix shifted?
-- name: q3_bd_mix
SELECT year, ROUND(gas_pct, 1) AS gas, ROUND(coal_pct, 1) AS coal, ROUND(oil_pct, 1) AS oil,
       ROUND(renewables_pct, 1) AS renewables,
       ROUND(imports_pct_of_demand, 1) AS imports_pct_of_demand
FROM energy WHERE country = 'Bangladesh' AND year >= 2010 ORDER BY year;

-- Q4. Renewables and carbon intensity: Bangladesh against its peers, 2015 vs 2025.
-- name: q4_peers
SELECT country,
       ROUND(MAX(renewables_pct) FILTER (WHERE year = 2015), 1) AS renewables_2015,
       ROUND(MAX(renewables_pct) FILTER (WHERE year = 2025), 1) AS renewables_2025,
       ROUND(MAX(solar_pct)      FILTER (WHERE year = 2025), 1) AS solar_2025,
       ROUND(MAX(g_co2_per_kwh)  FILTER (WHERE year = 2015)) AS g_co2_per_kwh_2015,
       ROUND(MAX(g_co2_per_kwh)  FILTER (WHERE year = 2025)) AS g_co2_per_kwh_2025
FROM energy GROUP BY country ORDER BY renewables_2025;

-- Q5. Emissions per person: how low is Bangladesh?
-- name: q5_emissions
SELECT e.country, e.year, ROUND(e.co2_t_per_person, 2) AS co2_t_per_person
FROM emissions e WHERE e.year = (SELECT MAX(year) FROM emissions WHERE co2_t_per_person IS NOT NULL)
ORDER BY co2_t_per_person;
