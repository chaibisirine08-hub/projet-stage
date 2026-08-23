import whois
import requests
from whois.exceptions import WhoisDomainNotFoundError, PywhoisError


def check_domain(domain):
    """
    Checks if a domain name is available.
    Uses whois library first, and falls back to rdap.org API if whois fails or is inconclusive.
    Returns: 'available', 'unavailable', or 'unknown'
    """
    domain = domain.strip().lower()

    # Method 1: Use python-whois
    try:
        print(f"WHOIS check for: {domain}")
        w = whois.whois(domain)
        
        # If registrar or creation_date is present, the domain is definitely registered
        if w.registrar or w.creation_date or w.expiration_date:
            print(f"WHOIS: {domain} is registered (Unavailable)")
            return "unavailable"
            
        # Sometimes whois returns an empty object or list instead of throwing an error
        # If there's no domain name info or registrar, it might be available
        if not w.domain_name:
            print(f"WHOIS: No domain_name info found for {domain}, checking RDAP fallback...")
        else:
            print(f"WHOIS: Found domain_name info for {domain} (Unavailable)")
            return "unavailable"

    except (WhoisDomainNotFoundError, PywhoisError) as e:
        # These errors are raised when domain is not found (which means it is available)
        print(f"WHOIS: {domain} is not registered -> Available")
        return "available"
        
    except Exception as e:
        # Catch connection timeouts, socket errors, unsupported TLDs, etc.
        print(f"WHOIS error for {domain}: {e}. Trying RDAP fallback...")

    # Method 2: Fallback to RDAP API
    try:
        url = f"https://rdap.org/domain/{domain}"
        print(f"RDAP check for: {domain}")
        response = requests.get(url, timeout=7)
        
        print(f"RDAP: {domain} response status: {response.status_code}")
        
        if response.status_code == 200:
            # 200 OK means domain record exists, so it is registered
            return "unavailable"
        elif response.status_code == 404:
            # 404 Not Found means no record exists, so it is available
            return "available"
        else:
            return "unknown"

    except Exception as e:
        print(f"RDAP error for {domain}: {e}")
        return "unknown"