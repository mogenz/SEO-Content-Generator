import streamlit as st
from openai import OpenAI
import pyperclip, smtplib, datetime
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# --- New: Collect all unique internal links (non-recursive) ---
def collect_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        links = set()
        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            if full_url.startswith(origin) and not full_url.lower().endswith(".pdf"):
                links.add(full_url)
        return list(links)
    except Exception as e:
        st.error(f"Error collecting links: {e}")
        return []

# # --- Updated: Generate PDF with markdown formatting
# def generate_pdf(markdown_text):
#     html_text = markdown.markdown(markdown_text)
#     wkhtmltopdf_path = shutil.which("wkhtmltopdf")
#     if wkhtmltopdf_path:
#         config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
#         pdf_bytes = pdfkit.from_string(html_text, False, configuration=config)
#         return pdf_bytes
#     else:
#         st.error("wkhtmltopdf not found. Please install it from https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf")
#         return None


# --- Reusable API key input widget ---
def show_api_key_input():
    api_key = st.text_input("Enter API Key", value=st.session_state["api_key"], type="password", key="api_key_input_main")
    col1, col2 = st.columns([8, 1])
    with col1:
        if st.button("✔️ Save API Key", key="save_api_key_main"):
            st.session_state["api_key"] = api_key
            st.session_state["show_api_input"] = False
            st.success("API Key Saved!")
    with col2:
        st.markdown('<a href="https://platform.openai.com/account/api-keys" target="_blank">❓</a>', unsafe_allow_html=True)

# --- Session state defaults ---
st.session_state.setdefault("api_key", "")
st.session_state.setdefault("show_help", False)
st.session_state.setdefault("show_contact", False)
st.session_state.setdefault("show_api_input", False)

# --- Load email & smtp secrets ---
sender_email = st.secrets["email"]["sender_email"]
receiver_email = st.secrets["email"]["receiver_email"]
app_password = st.secrets["email"]["app_password"]
smtp_server = st.secrets["smtp"]["server"]
smtp_port = st.secrets["smtp"]["port"]

# --- Sidebar ---
with st.sidebar:
    st.title("SEO Content Generator")
    st.markdown("---")
    if st.button("🤖 Generator", use_container_width=True):
        st.session_state["show_help"] = False
        st.session_state["show_contact"] = False

    st.markdown("## 🔧 Options")
    if not st.session_state["show_api_input"]:
        if st.button("🔑 Set API Key", use_container_width=True):
            st.session_state["show_api_input"] = True
    else:
        api_key = st.text_input("Enter API Key", value=st.session_state["api_key"], type="password", key="api_key_input_sidebar")
        col1, col2 = st.columns([8, 1])
        with col1:
            if st.button("✔️ Save API Key", key="save_api_key_sidebar"):
                st.session_state["api_key"] = api_key
                st.session_state["show_api_input"] = False
                st.success("API Key Saved!")
        with col2:
            st.markdown('<a href="https://platform.openai.com/account/api-keys" target="_blank">❓</a>', unsafe_allow_html=True)

    if st.button("📖 How to Use", use_container_width=True):
        st.session_state["show_help"] = True
        st.session_state["show_contact"] = False

    if st.button("💡 Got an Idea?", use_container_width=True):
        st.session_state["show_contact"] = True
        st.session_state["show_help"] = False

    st.markdown("---")
    st.markdown("#### Created by [Gustaw](https://github.com/mogenz)")

# --- How to Use Page ---
if st.session_state["show_help"]:
    st.title("📖 How to Use This Program")
    st.markdown("""
    ## **Welcome to the SEO Content Generator!** 🎯
    
    This tool helps you create **SEO-optimized text** based on your selected keywords, locations, and website sources.

    ### **1️⃣ Setting Up**
    - Click on **"Set API Key"** in the sidebar.
    - Enter your **OpenAI API Key** and press **✔️ Save API Key**.

    ### **2️⃣ Entering Your Inputs**
    - **Keywords:** Provide comma-separated SEO keywords.
    - **Locations:** Specify the target locations.
    - **Text Length:** Set the minimum and maximum word count.
    - **Target Website:** Enter the main website URL.
    - **Reference Websites:** List other website URLs to analyze the language.

    ### **3️⃣ Structuring Your Text**
    - Choose the **number of subheadings**.
    - Select **paragraphs per subheading**.
    - (Optional) **Include a "Contact Us" section**.

    ### **4️⃣ Generating & Copying the Text**
    - Click **"Generate Text"**.
    - Once the text appears:
      - Switch between **Markdown & Raw Text** tabs.
      - Copy using **"📋 Copy Markdown"** or **"📋 Copy Raw Text"**.

    ### **5️⃣ FAQ & Support**
    - Need an API key? Click **❓** next to the API Key field.
    - Issues? Check [OpenAI’s API Docs](https://platform.openai.com/docs/).
    """)
    if st.button("🔙 Back", use_container_width=True):
        st.session_state["show_help"] = False

# --- Contact Page ---
elif st.session_state["show_contact"]:
    st.title("💡 Got an Idea?")
    st.markdown("### 📨 Submit a Feature Request or Bug Report")
    subject_choice = st.selectbox("What is your submission about?", ["Bug Report", "Feature Idea", "Other"], key="subject_choice")
    user_email = st.text_input("Your Email (Optional)", key="user_email_input")
    user_message = st.text_area("Describe your idea or bug:", key="user_message_input")
    if st.button("Send Feedback", use_container_width=True):
        submission_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_subject = f"SEO-ContentGenerator + {subject_choice.upper()}"
        email_body = f"""
        <html>
          <body>
            <h2>New {subject_choice} Submission</h2>
            <p>Submitted by: {user_email if user_email else 'Anonymous'}</p>
            <p>Date & Time: {submission_time}</p>
            <p>Message: {user_message}</p>
          </body>
        </html>
        """
        try:
            msg = EmailMessage()
            msg.set_content(email_body, subtype="html")
            msg["Subject"] = email_subject
            msg["From"] = sender_email
            msg["To"] = receiver_email
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)
            st.success("✅ Feedback sent!")
        except Exception as e:
            st.error("❌ Error sending feedback.")
            st.error(f"Details: {e}")
    if st.button("🔙 Back", use_container_width=True):
        st.session_state["show_contact"] = False

# --- Main Generator UI ---
elif not st.session_state["show_help"] and not st.session_state["show_contact"]:
    if not st.session_state["api_key"]:
        st.error("Invalid or missing API Key!")
        show_api_key_input()
    else:
        try:
            client = OpenAI(api_key=st.session_state["api_key"])
            client.models.list()  # Validate API key

            st.title("SEO Content Generator")
            st.text("A SEO-tool made by Gustaw")

            # Input fields
            keywords = st.text_input("Enter keywords (comma separated)", key="keywords_input").split(", ")
            cities = st.text_input("Enter locations (comma separated)", key="cities_input").split(", ")
            min_words = st.number_input("Minimum word count", min_value=100, max_value=5000, value=300, key="min_words_input")
            max_words = st.number_input("Maximum word count", min_value=100, max_value=5000, value=800, key="max_words_input")

            # --- Fetch Links (mimics Chrome extension) ---
            chosen_webpage = st.text_input("Target webpage URL", key="chosen_webpage_input")
            if st.button("Fetch Subpages"):
                links = collect_links(chosen_webpage)
                st.session_state["fetched_links"] = links
                st.success(f"Found {len(links)} links.")
            default_links = st.session_state.get("fetched_links", [])
            website_links_input = st.text_area("Enter website links (one per line)", value="\n".join(default_links), key="website_links_input")
            website_links = website_links_input.split("\n")

            # --- Auto Structure Option ---
            auto_structure = st.checkbox("Let AI decide text structure", key="auto_structure")
            if not auto_structure:
                num_subheadings = st.number_input("Number of Subheadings", min_value=0, max_value=10, value=2, key="subheading_count")
                paragraphs_per_subheading = st.number_input("Paragraphs per Subheading", min_value=1, max_value=10, value=2, key="paragraphs_per_subheading")
            else:
                num_subheadings = paragraphs_per_subheading = None

            include_contact = st.checkbox("Include contact section at the end", key="contact_section")

            if st.button("Generate Text"):
                prompt = f"Søgeord: {', '.join(keywords)}\nGeografi: {', '.join(cities)}\n"
                prompt += f"Tekst længde: MINIMUM {min_words} ord & MAXIMUM {max_words} ord.\n"
                prompt += f"Målrettet side: {chosen_webpage}\nWebsites til analyse: {', '.join(website_links)}\n"
                if not auto_structure:
                    total_paragraphs = num_subheadings * paragraphs_per_subheading + 1
                    if include_contact:
                        total_paragraphs += 1
                    words_per_paragraph = max_words // total_paragraphs
                    prompt += (f"Struktur:\n- 1 H1-overskrift\n- {num_subheadings} H2-overskrifter med {paragraphs_per_subheading} afsnit hver "
                               f"(ca. {words_per_paragraph} ord per afsnit)\n")
                else:
                    prompt += "Struktur: Lad AI bestemme strukturen.\n"
                if include_contact:
                    prompt += "Tilføj til sidst en 'Kontakt os' sektion.\n"
                prompt += "\nStart teksten:"

                with st.spinner("Generating SEO content..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du er en professionel SEO-tekstforfatter."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000
                    )
                    generated_text = response.choices[0].message.content
                    st.session_state["generated_text"] = generated_text
                    st.success("SEO Text Generated!")

            # --- Display Generated Text & PDF Download ---
            if "generated_text" in st.session_state:
                generated_text = st.session_state["generated_text"]
                raw_text = generated_text.replace("#", "").replace("##", "").replace("*", "")
                tab1, tab2, tab3 = st.tabs(["📜 Markdown", "📄 Raw Text", "📄 PDF"])
                
                with tab1:
                    st.markdown("### Generated Text (Markdown)")
                    st.markdown(generated_text)
                    if st.button("📋 Copy Markdown", key="copy_markdown"):
                        pyperclip.copy(generated_text)
                        st.success("Markdown copied!")
                    with st.expander("Word Counter - Markdown", expanded=True):
                            words = len(generated_text.split())
                            char_no_spaces = len(generated_text.replace(" ", ""))
                            char_with_spaces = len(generated_text)
                            st.write(f"**Words:** {words}")
                            st.write(f"**Characters (no spaces):** {char_no_spaces}")
                            st.write(f"**Characters (with spaces):** {char_with_spaces}")
                
                with tab2:
                    st.markdown("### Generated Text (Raw)")
                    st.text_area("Raw Text", raw_text, height=250)
                    if st.button("📋 Copy Raw", key="copy_raw"):
                        pyperclip.copy(raw_text)
                        st.success("Raw text copied!")
                    with st.expander("Word Counter - Raw", expanded=True):
                            words = len(generated_text.split())
                            char_no_spaces = len(generated_text.replace(" ", ""))
                            char_with_spaces = len(generated_text)
                            st.write(f"**Words:** {words}")
                            st.write(f"**Characters (no spaces):** {char_no_spaces}")
                            st.write(f"**Characters (with spaces):** {char_with_spaces}")
                        
                
                with tab3:
                    st.markdown("### Download as PDF")
                    st.info("Coming soon")
        except Exception as e:
            st.error("Invalid API Key or an error occurred.")
            st.error(f"Error: {e}")
