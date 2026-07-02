import re

import httpx
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings for scraping outdated/insecure websites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MOCK_WEBPAGES = {
    "https://www.brickellfamilydentistry.com": {
        "scraped_title": "Brickell Family Dentistry | Modern Dental Care in Miami, FL",
        "meta_description": "Welcome to Brickell Family Dentistry. We offer cutting-edge dental care, cosmetic dentistry, Invisalign, and implants. Schedule your appointment online today!",
        "scraped_text": """
        Brickell Family Dentistry - Home.
        About Us: We are a modern, high-tech dental practice located in the heart of Brickell, Miami.
        Our services:
        - Preventive care and cleanings
        - Cosmetic Dentistry (Teeth whitening, veneers)
        - Invisalign & Orthodontic treatments
        - Dental Implants and oral surgery using state-of-the-art 3D imaging

        Why choose us?
        We use digital x-rays, intraoral cameras, and laser dentistry to make your visit fast, painless, and efficient.
        Schedule Online: Click here to access our automated patient portal to book your appointment, fill out intake forms, and pay online.
        Technology partner: Proudly powered by modern cloud dental software.
        """,
        "http_status": 200,
    },
    "http://downtownmiamidentalarts.example.com": {
        "scraped_title": "Downtown Dental Arts of Miami - Welcome",
        "meta_description": "Dental services in downtown Miami. Call us to book.",
        "scraped_text": """
        Welcome to Downtown Dental Arts of Miami.
        This website was built in 2013 and is best viewed on Internet Explorer 9.
        We have been serving patients for over 30 years.
        Services:
        - Tooth extraction
        - Fillings
        - Standard cleanings

        To schedule an appointment, you must call our receptionist between 9 AM and 4 PM. We do not support email or online scheduling.
        Please print our patient registration PDF, fill it out by hand, and bring it to your appointment.
        Warning: Our site is currently HTTP only. We do not store patient details online for security.
        """,
        "http_status": 200,
    },
    "https://www.tampabayinjurylawgroup.com": {
        "scraped_title": "Tampa Bay Injury Law Group | Accident & Injury Lawyers",
        "meta_description": "Injured in Tampa? Get a free consultation from our experienced personal injury attorneys. We have recovered millions for our clients across Florida.",
        "scraped_text": """
        Tampa Bay Injury Law Group - Fighting for you.
        We represent clients injured in car accidents, truck accidents, slip and falls, and medical malpractice.
        Our locations: Tampa office, St. Petersburg office, Clearwater office, and Orlando office.
        Our team includes 15 trial attorneys and over 40 paralegals and support staff.

        Case Results:
        - $5.2 Million truck accident settlement
        - $2.1 Million wrongful death verdict
        - $850,000 slip and fall compensation

        Contact us 24/7. Call our hotline or use our live chat tool on our website.
        We process hundreds of claims monthly using our custom databases.
        Client Portal: Log in to view your case documents and message your attorney (currently hosted on on-premise servers).
        """,
        "http_status": 200,
    },
    "https://sarasotatampadefense.example.com": {
        "scraped_title": "Sarasota & Tampa Defense Attorneys",
        "meta_description": "Affordable criminal defense in Sarasota and Tampa. DUI, drug charges, and misdemeanors.",
        "scraped_text": """
        Sarasota & Tampa Defense Attorneys.
        Have you been arrested? We can help.
        We handle DUI defense, traffic tickets, minor drug possession, and other misdemeanor offenses in Sarasota and Hillsborough counties.

        Our attorneys:
        - John Doe, Esq. (20 years experience)
        - Jane Smith, Esq. (12 years experience)

        Contact:
        Main Office: 123 Law Lane, Sarasota, FL
        Satellite Office: 201 E Kennedy Blvd, Tampa, FL
        Call us at 941-555-0190.
        Note: Website design by WebDesigns123. Copyright 2017.
        """,
        "http_status": 200,
    },
}


def clean_html(html_content: str) -> dict:
    """Parses HTML content using BeautifulSoup and extracts title, description, and clean text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Get title
    title = soup.title.string.strip() if soup.title else ""

    # Get meta description
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if meta_tag:
        meta_desc = meta_tag.get("content", "").strip()

    # Remove script and style elements
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.decompose()

    # Get text
    text = soup.get_text(separator=" ")

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text_content = "\n".join(chunk for chunk in chunks if chunk)

    # Limit to 3500 characters
    text_content = re.sub(r"\n+", "\n", text_content)
    cleaned_text = text_content[:3500]

    return {
        "scraped_title": title,
        "meta_description": meta_desc,
        "scraped_text": cleaned_text,
    }


def scrape_website(url: str) -> dict:
    """
    Fetches the website homepage and parses the content.
    Includes mock fallback for demonstration domains or if requests fail.
    """
    if not url:
        return {
            "scraped_title": "",
            "meta_description": "",
            "scraped_text": "No website URL provided.",
            "http_status": 404,
        }

    # Strip trailing slash for lookup
    clean_url = url.rstrip("/")
    if clean_url in MOCK_WEBPAGES:
        print(f"[Scraper] Returning mock webpage data for: {url}")
        return MOCK_WEBPAGES[clean_url]

    print(f"[Scraper] Fetching live website: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        with httpx.Client(verify=False, timeout=10.0, follow_redirects=True) as client:
            response = client.get(url, headers=headers)

            if response.status_code == 200:
                parsed_data = clean_html(response.text)
                parsed_data["http_status"] = 200
                return parsed_data
            else:
                return {
                    "scraped_title": "",
                    "meta_description": "",
                    "scraped_text": f"Failed to load website. HTTP Status: {response.status_code}",
                    "http_status": response.status_code,
                }
    except Exception as e:
        print(f"[Scraper] Error scraping {url}: {e}")
        return {
            "scraped_title": "",
            "meta_description": "",
            "scraped_text": f"Error during scraping: {e!s}",
            "http_status": 500,
        }
