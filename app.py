import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import google.generativeai as genai
import chromedriver_autoinstaller

def extract_details_with_gemini(text, api_key="AIzaSyB9dSYe3H16e3PV-4ol7n-IydclXw3PiAY"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Define the prompt
    prompt = f"""
    Extract the following details from the provided text:
    - SKU
    - Model Case
    - Bezel
    - Water Resistance
    - Movement
    - Calibre
    - Power Reserve
    - Bracelet
    - Dial
    - Certification

    Text:
    {text}
    """
    try:
        # Generate content using the Gemini model
        response = model.generate_content(prompt)
        candidates = response.candidates
        details = candidates[0].content.parts[0].text

        return details
    except Exception as e:
        st.error(f"Error communicating with Gemini API: {e}")
        return None

# Function to extract webpage text with Selenium
def extract_text_with_selenium(url, proxy=None):
    try:
        # Automatically install the appropriate ChromeDriver version
        chromedriver_autoinstaller.install()

        chrome_options = Options()
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        chrome_options.add_argument("--headless")  # Run in headless mode for deployment
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')

        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)
        driver.implicitly_wait(10)
        time.sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text

    except Exception as e:
        st.error(f"Error extracting text from {url}: {e}")
        return None

    finally:
        driver.quit()

# Streamlit App
def main():
    # Set wide page layout
    st.set_page_config(layout="wide", page_title="Rolex Watch Details Extractor")

    # Sidebar for proxy
    proxy = st.sidebar.text_input("Optional: Enter proxy server (e.g., http://proxy-server:port)")

    st.title("Rolex Watch Details Extractor with Gemini API")

    # Input: List of URLs
    urls = st.text_area("Enter website URLs (one per line):", placeholder="https://example.com\nhttps://another-site.com")

    if st.button("Extract Rolex Details"):
        if urls.strip():
            urls = urls.splitlines()

            for url in urls:
                st.write(f"Extracting text from: {url}")
                text = extract_text_with_selenium(url, proxy if proxy.strip() else None)
                text = text.strip() if text else None
                text = str(text).replace("\n", " ")

                if text:
                    # Use Gemini API to extract details
                    st.write(f"Processing extracted text with Gemini API...")
                    details = extract_details_with_gemini(text)

                    if details:
                        st.subheader(f"Rolex Details from {url}")
                        st.code(details, language="text")  # `st.code` provides a copy button by default
                    else:
                        st.error(f"Failed to extract details from {url} using Gemini API")

                else:
                    st.error(f"Failed to extract text from {url}")
        else:
            st.warning("Please enter at least one URL.")

if __name__ == "__main__":
    main()
