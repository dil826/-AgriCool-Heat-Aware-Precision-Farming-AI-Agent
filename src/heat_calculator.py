
def calculate_heat_index(temperature_c: float, humidity: float) -> float:
    """Approximate heat index (°C) from temperature (°C) and relative humidity (%)."""
    t_f = (temperature_c * 9 / 5) + 32
    r = humidity

    hi_f = (
        -42.379
        + 2.04901523 * t_f
        + 10.14333127 * r
        - 0.22475541 * t_f * r
        - 6.83783e-3 * t_f * t_f
        - 5.481717e-2 * r * r
        + 1.22874e-3 * t_f * t_f * r
        + 8.5282e-4 * t_f * r * r
        - 1.99e-6 * t_f * t_f * r * r
    )

    hi_c = (hi_f - 32) * 5 / 9
    return round(max(temperature_c, hi_c), 1)


def heat_risk_level(heat_index_c: float) -> str:
    if heat_index_c < 27:
        return "Low"
    if heat_index_c < 32:
        return "Moderate"
    if heat_index_c < 41:
        return "High"
    return "Severe"


def estimate_irrigation_need(
    temperature_c: float,
    heat_index_c: float,
    crop_profile: dict,
    precipitation_mm: float = 0.0,
) -> dict:
    """Estimate daily irrigation need and water-loss severity."""
    optimal_max = crop_profile.get("optimal_temp_c", {}).get("max", 30)
    stress_start = crop_profile.get("stress_temp_c", {}).get("moderate", optimal_max + 3)

    stress_delta = max(0.0, heat_index_c - stress_start)
    evap_factor = 1.0 + (stress_delta / 12.0)

    base_mm = max(3.0, (temperature_c - 18) * 0.25)
    gross_mm = base_mm * evap_factor
    net_mm = max(0.0, gross_mm - precipitation_mm)

    water_loss_l_per_hectare = round(net_mm * 10000, 0)

    if heat_index_c >= crop_profile.get("stress_temp_c", {}).get("severe", 42):
        severity = "Critical"
    elif heat_index_c >= crop_profile.get("stress_temp_c", {}).get("high", 36):
        severity = "High"
    elif heat_index_c >= stress_start:
        severity = "Elevated"
    else:
        severity = "Normal"

    return {
        "irrigation_mm_day": round(net_mm, 1),
        "water_loss_l_ha_day": water_loss_l_per_hectare,
        "water_stress_severity": severity,
    }
