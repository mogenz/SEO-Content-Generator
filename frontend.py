import streamlit as st
from openai import OpenAI
import pyperclip
import smtplib
from email.message import EmailMessage
import datetime

# Initialize session state variables if not set
st.session_state.setdefault("api_key", "")
st.session_state.setdefault("show_help", False)
st.session_state.setdefault("show_contact", False)
st.session_state.setdefault("show_api_input", False)

# Load secrets
sender_email = st.secrets["email"]["sender_email"]
receiver_email = st.secrets["email"]["receiver_email"]
app_password = st.secrets["email"]["app_password"]
smtp_server = st.secrets["smtp"]["server"]
smtp_port = st.secrets["smtp"]["port"]

# UI for sidebar options
with st.sidebar:
    # 🎛️ Generator button (Most Prominent)
    if st.button("🤖 Generator", use_container_width=True):
        st.session_state["show_help"] = False
        st.session_state["show_contact"] = False

    st.markdown("## 🔧 Options")

    # 🔑 Set API Key Button
    if not st.session_state["show_api_input"]:
        if st.button("🔑 Set API Key", use_container_width=True):
            st.session_state["show_api_input"] = True
    else:
        api_key = st.text_input("Enter API Key", value=st.session_state["api_key"], type="password", key="api_key_input")
        col1, col2 = st.columns([8, 1])

        with col1:
            if st.button("✔️ Save API Key", use_container_width=True):
                st.session_state["api_key"] = api_key
                st.session_state["show_api_input"] = False  # Hide input immediately
                st.success("API Key Saved!")

        with col2:
            st.markdown('<a href="https://platform.openai.com/account/api-keys" target="_blank">❓</a>', unsafe_allow_html=True)

    # 📖 How to Use button
    if st.button("📖 How to Use", use_container_width=True):
        st.session_state["show_help"] = True
        st.session_state["show_contact"] = False

    # 💡 Got an Idea? button (Below How to Use)
    if st.button("💡 Got an Idea?", use_container_width=True):
        st.session_state["show_contact"] = True
        st.session_state["show_help"] = False

# Display "How to Use" Page
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

# Display Contact Page
elif st.session_state["show_contact"]:
    st.title("💡 Got an Idea?")
    st.markdown("### 📨 Submit a Feature Request or Bug Report")

    subject_choice = st.selectbox("What is your submission about?", ["Bug Report", "Feature Idea"], key="subject_choice")
    user_email = st.text_input("Your Email (Optional)", key="user_email_input")
    user_message = st.text_area("Describe your idea or bug:", key="user_message_input")

    if st.button("Send Feedback", use_container_width=True):
        submission_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_subject = f"SEO-ContentGenerator + {subject_choice.upper()}"
        
        # Format email body
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #0056b3;">📩 New {subject_choice} Submission</h2>
            <p>Dear Developer,</p>
            <p>You have received a new submission from the SEO Content Generator feedback form.</p>
            <hr style="border: 1px solid #ddd;">
            <h3>🔹 Submission Details:</h3>
            <ul>
                <li><b>Type:</b> {subject_choice.upper()}</li>
                <li><b>Submitted by:</b> {user_email if user_email else 'Anonymous User'}</li>
                <li><b>Date & Time:</b> {submission_time}</li>
            </ul>
            <h3>📝 Message Content:</h3>
            <p style="border-left: 4px solid #0056b3; padding-left: 10px; color: #444;">{user_message}</p>
            <hr style="border: 1px solid #ddd;">
            <p style="font-size: 12px; color: #777;">This email was automatically generated by the SEO Content Generator.</p>
        </body>
        </html>
        """

        try:
            msg = EmailMessage()
            msg.set_content(user_message)
            msg["Subject"] = email_subject
            msg["From"] = sender_email
            msg["To"] = receiver_email

            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)

            st.success("✅ Your feedback has been sent successfully! Thank you for your contribution. 🚀")

        except Exception as e:
            st.error("❌ Sorry, something went wrong while sending your feedback. Please try again later.")
            st.error(f"Error Details: {e}")
    
    if st.button("🔙 Back", use_container_width=True):
        st.session_state["show_contact"] = False

# ✅ Only show the main generator UI if neither "How to Use" nor "Got an Idea?" is open
elif not st.session_state["show_help"] and not st.session_state["show_contact"]:
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=st.session_state["api_key"])
        test_response = client.models.list()  # Test API key validity

        st.title("SEO Content Generator")
        st.text("A SEO-tool made by Gustaw")

        # User input fields
        keywords = st.text_input("Enter keywords (comma separated)", key="keywords_input").split(", ")
        cities = st.text_input("Enter locations (comma separated)", key="cities_input").split(", ")
        min_words = st.number_input("Minimum word count", min_value=100, max_value=5000, value=300, key="min_words_input")
        max_words = st.number_input("Maximum word count", min_value=100, max_value=5000, value=800, key="max_words_input")
        chosen_webpage = st.text_input("Target webpage URL", key="chosen_webpage_input")
        website_links = st.text_area("Enter website links (one per line)", key="website_links_input").split("\n")

        # New input fields for structure
        num_subheadings = st.number_input("Number of Subheadings", min_value=0, max_value=10, value=2, key="subheading_count")
        paragraphs_per_subheading = st.number_input("Paragraphs per Subheading", min_value=1, max_value=10, value=2, key="paragraphs_per_subheading")

        # Checkbox for contact section
        include_contact = st.checkbox("Include contact session at the end", key="contact_section")

        if st.button("Generate Text"):
            # Calculate total paragraphs
            total_paragraphs = num_subheadings * paragraphs_per_subheading + 1  # +1 for intro before subheadings
            if include_contact:
                total_paragraphs += 1  # Add one more for contact section

            words_per_paragraph = max_words // total_paragraphs  

            prompt = f"""
            Søgeord: {', '.join(keywords)}
            Geografi: {', '.join(cities)}
            Tekst længde: MINIMUM {min_words} ord & MAXIMUM {max_words} ord.

            Brug OpenAI’s internetbrowsing til at gennemgå følgende hjemmesider og deres undersider. 
            Teksten skal lyde som om og have samme ordvalg og ordlyd som teksterne fundet på hjemmesiderne.
            Teksten må ikke lyve, love noget der ikke er sandt eller direkte gentage tekster ord for ord. 
            Teksten SKAL have den angivne længde og inkludere de angivne søgeord og geografier.

            **Tekststruktur:**
            - **1 Hovedoverskrift** (inkluderende søgeord + geografi)
            - **{num_subheadings} Underoverskrifter**
            - **{paragraphs_per_subheading} Afsnit per underoverskrift**
            - **Fordeling af ord:** Ca. {words_per_paragraph} ord per afsnit

            Teksten skal være specifikt målrettet denne side: {chosen_webpage}

            Websites, der skal analyseres: {', '.join(website_links)}

            Brug OpenAI's browsing-funktion til at studere sproget på disse sider, før du genererer teksten.
            
            **Start nu teksten:**  
            - Skriv en H1-overskrift øverst.  
            - Skriv en kort introduktion (1 afsnit).  
            - Fordel teksten, så der er {num_subheadings} H2-underoverskrifter, med {paragraphs_per_subheading} afsnit hver.  
            - Teksten skal være naturlig og informativ.
            """

            if include_contact:
                prompt += """
                
                **Tilføj til sidst:**  
                - En sektion med en H2-overskrift kaldet "Kontakt os".  
                - Et kort afsnit om, hvordan læseren kan kontakte virksomheden.
                """

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

                st.session_state["generated_text"] = generated_text  # Store text in session state
                st.success("SEO Text Generated!")

        # Ensure text remains displayed after generation
        if "generated_text" in st.session_state:
            generated_text = st.session_state["generated_text"]
            raw_text = generated_text.replace("#", "").replace("##", "").replace("*", "")

            # Tabs to separate Markdown and Raw Text
            tab1, tab2 = st.tabs(["📜 Markdown", "📄 Raw Text"])

            with tab1:
                st.markdown("### ✍️ **Generated Text (Markdown)**")
                st.markdown(generated_text)  # Viser Markdown korrekt
                if st.button("📋 Copy Markdown", key="copy_markdown"):
                    pyperclip.copy(generated_text)
                    st.success("✅ Markdown-text Copied!")

            with tab2:
                st.markdown("### 🔹 **Generated Text (Raw Text)**")
                st.text_area("Raw Text", raw_text, height=250)
                if st.button("📋 Copy Tekst", key="copy_raw"):
                    pyperclip.copy(raw_text)
                    st.success("✅ Raw text Copied!")
    except Exception:
        st.error("❌ **Invalid API Key**. Please enter a valid API key or contact support for help.")
