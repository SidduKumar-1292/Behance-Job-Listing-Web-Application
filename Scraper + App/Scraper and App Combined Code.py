import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
import time
import webbrowser

# Streamlit setup
st.set_page_config(page_title="Behance Job Listings", page_icon="📋", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        /* Page Background */
        body {
            background: linear-gradient(to bottom right, #FFEB3B, #FF6347);
            color: #333;
            font-family: 'Arial', sans-serif;
        }

        /* Header Styling */
        .header {
            color: #FFFFFF;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
        }

        .subheader {
            color: #FFFFFF;
            font-size: 24px;
            text-align: center;
            margin-bottom: 40px;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
        }

        /* Dropdown Menu */
        .stSelectbox {
            background-color: #FFF;
            border-radius: 5px;
            font-size: 16px;
            padding: 10px;
            color: #333;
        }

        /* Job Cards */
        .card {
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            background: linear-gradient(to top right, #2c3e50, #4ca1af);
            color: #FFF;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.6);
        }

        /* Card Image */
        .card img {
            width: 100px;
            height: 100px;
            object-fit: cover;
            margin-bottom: 15px;
            border-radius: 50%;
            border: 3px solid #FFFFFF;
        }

        /* Card Text */
        .card h4 {
            font-size: 18px;
            font-weight: bold;
            color: #FFD700;
            margin: 10px 0;
        }
        .card p {
            margin: 5px 0;
        }
        .card p strong {
            color: #FFD700;
        }
    </style>
    """, unsafe_allow_html=True)

# Scraping function
def scrape_jobs():
    categories = [
        "logo-design", "branding-services", "social-media-design", "website-design",
        "illustrations", "packaging-design", "landing-page-design", "ui-ux-design", "architecture-interior-design",
        "all-graphic-design"
    ]
    data = []
    seen_links = set()

    # Selenium WebDriver setup
    chrome_options = Options()
    chrome_options.add_argument("--start-fullscreen")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(r"C:\chromedriver-win64\chromedriver.exe")  # Update with your ChromeDriver path

    driver = webdriver.Chrome(service=service, options=chrome_options)

    for category in categories:
        try:
            url = f"https://www.behance.net/joblist?tracking_source=nav20&category={category}"
            driver.get(url)
            time.sleep(2)

            previous_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(50):
                driver.execute_script("window.scrollBy(0, 4000);")
                time.sleep(0.3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == previous_height:
                    break
                previous_height = new_height

            job_cards = driver.find_elements(By.CLASS_NAME, "JobCard-jobCard-mzZ")
            for card in job_cards:
                try:
                    company = card.find_element(By.CLASS_NAME, "JobCard-company-GQS").text
                    title = card.find_element(By.CLASS_NAME, "JobCard-jobTitle-LS4").text
                    description = card.find_element(By.CLASS_NAME, "JobCard-jobDescription-SYp").text
                    time_posted = card.find_element(By.CLASS_NAME, "JobCard-time-Cvz").text
                    location = card.find_element(By.CLASS_NAME, "JobCard-jobLocation-sjd").text
                    image_url = card.find_element(By.CSS_SELECTOR, '.JobLogo-logoButton-aes img').get_attribute('src')
                    job_link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

                    if job_link not in seen_links:
                        seen_links.add(job_link)
                        data.append([category, company, title, description, time_posted, location, image_url, job_link])
                except Exception:
                    continue
        except Exception:
            continue

    driver.quit()

    # Save data to CSV
    if data:
        filename = "behance_jobs_with_links.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Category", "Company", "Job Title", "Description", "Time Posted", "Location", "Image URL", "Job Link"])
            writer.writerows(data)

# Function to perform scrolling before opening job in new tab
def scroll_and_open_job(job_link):
    # Initialize WebDriver to perform scrolling on the main Behance job listings page
    chrome_options = Options()
    chrome_options.add_argument("--start-fullscreen")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(r"C:\chromedriver-win64\chromedriver.exe")  # Update with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open Behance job listings page
    driver.get("https://www.behance.net/joblist?tracking_source=nav20")
    time.sleep(2)  # Wait for page load

    # Scroll down 3 times
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 4000);")
        time.sleep(2)

    # Now open the selected job's page in a new tab
    driver.get(job_link)  # Open the job information page directly
    time.sleep(2)  # Wait for job details page to load
    
    # Open the job information page in a new tab
    webbrowser.open_new_tab(job_link)

# Streamlit UI
st.markdown("<div class='header'>Behance Job Listings</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Explore Creative Job Opportunities</div>", unsafe_allow_html=True)

# Search option (additional feature)
search_option = st.text_input("Search for a job title or company name:")
if search_option:
    data = pd.read_csv("behance_jobs_with_links.csv")
    search_results = data[data['Job Title'].str.contains(search_option, case=False, na=False) | data['Company'].str.contains(search_option, case=False, na=False)]
    
    if not search_results.empty:
        st.markdown("### Search Results")
        for i, (_, row) in enumerate(search_results.iterrows()):
            job_title = row['Job Title']
            company = row['Company']
            st.markdown(f"- **{job_title}** at **{company}**")
            
            # Add a button for opening the job page
            if st.button(f"Open {job_title} at {company}", key=f"open_{i}"):
                st.write("Performing scrolling automation and opening the job listing page...")
                # Perform scrolling and open the job in a new tab
                scroll_and_open_job(row['Job Link'])
                st.success(f"Opening job: {job_title} at {company}...")

    else:
        st.warning("No results found.")

# Scrape button
if st.button("Scrape Jobs"):
    with st.spinner("Scraping job listings..."):
        scrape_jobs()
    st.success("Job listings scraped and saved to CSV!")

# Display job listings
filename = "behance_jobs_with_links.csv"
try:
    data = pd.read_csv(filename)

    filter_option = st.radio(
        "Select the type of filter you want to use:",
        ("Job Title", "Company")
    )

    if filter_option == "Job Title":
        unique_titles = data['Job Title'].unique()
        selected_title = st.selectbox("Filter by Job Title", options=["All"] + list(unique_titles))
        filtered_data = data if selected_title == "All" else data[data['Job Title'] == selected_title]
    else:
        unique_companies = data['Company'].unique()
        selected_company = st.selectbox("Filter by Company", options=["All"] + list(unique_companies))
        filtered_data = data if selected_company == "All" else data[data['Company'] == selected_company]

    if filtered_data.empty:
        st.warning("No job listings found for the selected filter.")
    else:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, (_, row) in enumerate(filtered_data.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="card">
                        <img src="{row['Image URL']}" alt="Company Logo">
                        <h4>{row['Company']}</h4>
                        <p><strong>Job Title:</strong> {row['Job Title']}</p>
                        <p><strong>Description:</strong> {row['Description']}</p>
                        <p><strong>Time Posted:</strong> {row['Time Posted']}</p>
                        <p><strong>Location:</strong> {row['Location']}</p>
                        <p><a href="{row['Job Link']}" target="_blank" style="color: #FFD700; font-weight: bold;">View Job</a></p>
                    </div>
                """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"Error: The file {filename} was not found. Please ensure the file exists in the same directory as this script.")







