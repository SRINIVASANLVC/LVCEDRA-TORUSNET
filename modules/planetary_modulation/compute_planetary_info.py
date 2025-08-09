import ephem
from math import pi
from datetime import datetime, timedelta

from .load_bodies import load_bodies


def utc_to_fractional_year(utc_time_str):
    dt = datetime.strptime(utc_time_str, '%Y/%m/%d %H:%M:%S')
    year_start = datetime(dt.year, 1, 1)
    year_end = datetime(dt.year + 1, 1, 1)
    year_fraction = (dt - year_start).total_seconds() / (year_end - year_start).total_seconds()
    return (dt.year + year_fraction)

def lahiri_ayanamsa_from_utc(utc_time_str):
    y = utc_to_fractional_year(utc_time_str)
    # Lahiri reference year is 285 AD with 0° ayanamsa
    precession_rate = 50.285123 / 3600  # arcseconds/year → degrees/year
    return round(((y - 285) * precession_rate) + 7, 6)  # we add additional 7 degrees to ayanamsa to ensure our model of separating sun and moon nakshatras to 2 separate houses

def mean_node_longitude(julian_day):
    # Mean lunar node calculation (simplified)
    T = (julian_day - 2451545.0) / 36525.0
#    node = 125.04452 - 1934.136261 * T + 0.0020708 * T**2 + (T**3) / 450000
    node = 125.04455501 - 1934.1361849 * T + 0.0020762 * T**2 + T**3 / 467410 - T**4 / 60616000
    return node % 360

def mean_lilith_longitude(julian_day):
    # Empirical mean motion: ~40.645°/year
#    T = (julian_day - 2451545.0) / 365.25  # Convert to Julian years
    lilith = (julian_day - 2451545.0)* 360.0 * 7.0/365.256363005 / 62 + 263.0 + 21.0/60
    return lilith % 360


def get_sidereal_longitude(body, utc_time, ayanamsa):
    body_title = body.title()    

    if body_title == 'Lilith':
        jd = ephem.julian_date(utc_time)
        lilith_lon = mean_lilith_longitude(jd) - ayanamsa
        return round(lilith_lon % 360, 6)
    
    
    elif body_title in ['Rahu', 'Ketu']:
        jd = ephem.julian_date(utc_time)
        rahu_lon = mean_node_longitude(jd) - ayanamsa
        rahu_lon = rahu_lon % 360
        ketu_lon = (rahu_lon + 180) % 360
        return round(rahu_lon, 6) if body_title == 'Rahu' else round(ketu_lon, 6)
 

    # Handle standard ephem-supported bodies
    elif hasattr(ephem, body_title):
        planet = getattr(ephem, body_title)()
        planet.compute(utc_time)
        ecl = ephem.Ecliptic(planet)
        lon = ecl.lon * (180.0 / pi) - ayanamsa        
        return round(lon % 360, 6)

    else:
        # Stub for unsupported bodies
        return f"{body_title} requires extended support (e.g., Swiss Ephemeris)"

def get_zone_info(longitude, zones):
    longitude = longitude % 360  # Normalize wrap-around
    for zone in zones:
        if zone["start"] <= longitude < zone["end"]:
            return {
                "zone": zone["zone"],
                "sign": zone["sign"],
                "sign_ruler": zone["ruler"],
                "nakshatra": zone["nakshatra"],
                "nakshatra_ruler": zone["nak_ruler"],
                "template_House": zone["house"]
            }
    return None  # if no match found

        
def retrograde_flag(body_title, planet_zone, sun_longitude, sun_zone, utc_time, ayanamsa):
    if body_title in ['Mercury' , 'Venus']:
        planet = getattr(ephem, body_title)()
        planet.compute(utc_time)
        ecl = ephem.Ecliptic(planet)
        lon = ecl.lon * (180.0 / pi) - ayanamsa
        sep = abs(lon - sun_longitude)
        if sep > 8:
            planet_status = "Direct"
        if sep <= 8 and planet.phase <= 0.1:
            planet_status = "Retrograde"
        elif sep <= 8 and planet.phase > 0.1:
            planet_status = "Combust" 
        return planet_status  
    elif body_title in ['Rahu', 'Ketu', 'Lilith']:
        return "Retrograde"
    elif body_title in ['Sun', 'Moon']:
        return "Direct"
    elif body_title in ['Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:    
        delta = abs(planet_zone - sun_zone) % 36
        if delta == 0:
            return "Combust"
        elif delta <= 12 or delta >= 24:
            return "Direct"
        else:
            return "Retrograde"
    else:
        return "NA"

def get_sun_info(utc_time, ayanamsa, modulation_zones):
    sun = ephem.Sun()
    sun.compute(utc_time)
    ecl = ephem.Ecliptic(sun)
    sun_longitude = ecl.lon * (180.0 / pi) - ayanamsa
    sun_longitude = sun_longitude % 360
    sun_zone_data = get_zone_info(sun_longitude, modulation_zones)
    return sun_longitude, sun_zone_data

def trace_all_variables():
    print("\n--- Variable Trace (locals) ---")
    for name, val in locals().items():
        if not name.startswith("__"):
            print(f"{name} = {val} ({type(val).__name__})")

    print("\n--- Variable Trace (globals) ---")
    for name, val in globals().items():
        if not name.startswith("__") and not callable(val):
            print(f"{name} = {val} ({type(val).__name__})")
    
def compute_planetary_info(utc_time, modulation_zones):
    ayanamsa = lahiri_ayanamsa_from_utc(utc_time)
    bodies = load_bodies()
    # modulation_zones = load_modulation_zones()
    # print(f"Ayanamsa adjusted: {ayanamsa}")

    planet_info = {}

    # Calculate Sun's sidereal longitude and zone first
    sun = ephem.Sun()
    sun.compute(utc_time)
    ecl = ephem.Ecliptic(sun)
    sun_longitude = ecl.lon * (180.0 / pi) - ayanamsa
    sun_zone = get_zone_info(sun_longitude, modulation_zones)["zone"]          

    for body in bodies:
        lon = get_sidereal_longitude(body, utc_time, ayanamsa)
        zone_data = get_zone_info(lon, modulation_zones)
        planet_zone = zone_data["zone"]
        retrograde_status = retrograde_flag(body, planet_zone, sun_longitude, sun_zone,utc_time, ayanamsa)

        
        # Store all details
        planet_info[body] = {
            "longitude": lon,
            **zone_data,
            "retrograde_status": retrograde_status
        }

    # Optional: Print nicely
    # for body, info in planet_info.items():
    #     print(f"{body}: {info['longitude']:.6f}°, Direction: {info['retrograde_status']}, {info}")
    # trace_all_variables()
    return planet_info