import streamlit as st
import os, sys
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup
import time
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="Rolex Watch Details Extractor")


@st.cache_resource
def installff():
    os.system('sbase install geckodriver')
    os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

_ = installff()

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
        opts = FirefoxOptions()
        opts.add_argument("--headless")  # Run in headless mode

        if proxy:
            opts.add_argument(f'--proxy-server={proxy}')

        browser = webdriver.Firefox(options=opts)

        browser.get(url)
        time.sleep(2)
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text

    except Exception as e:
        st.error(f"Error extracting text from {url}: {e}")
        return None

    finally:
        browser.quit()

# Streamlit App
def main():
    # Set wide page layout

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
