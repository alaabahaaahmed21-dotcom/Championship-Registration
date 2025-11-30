import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path
import requests
import hashlib
import time

# ---------------- Google Sheet API ----------------
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec"  

@st.cache_data
def save_to_google_sheet(row):
    """Save row to Google Sheets with retry logic"""
    for attempt in range(3):
        try:
            r = requests.post(GOOGLE_SHEET_API, json=row, timeout=10)
            if r.status_code == 200:
                return True
            time.sleep(0.5 * (attempt + 1))  # Exponential backoff
        except:
            continue
    return False

def hash_password(password):
    """Secure password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def safe_rerun():
    """Safe rerun with backward compatibility"""
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except:
        pass

# ---------------- Logos ----------------
img1 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png"
img2 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png"
img3 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png"
img4 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"

# ---------------- CSS ----------------
st.markdown("""
<style>
.image-row { display: flex; justify-content: center; gap: 10px; flex-wrap: nowrap; }
.image-row img { width: 80px; height: auto; }
.success-box { background-color: #d4edda; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745; }
.error-box { background-color: #f8d7da; padding: 10px; border-radius: 5px; border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

# ---------------- Page State ----------------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"
if "new_rows" not in st.session_state:
    st.session_state.new_rows = []

DATA_FILE = Path("athletes_data.csv")
ADMIN_HASH = hash_password("mobadr90")  # غير هذا لكلمة سر قوية

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    cols = [
        "Championship", "Athlete Name", "Club", "Nationality", "Coach Name",
        "Phone Number", "Date of Birth", "Sex", "Player Code",
        "Belt Degree", "Competitions", "Federation", "Timestamp"
    ]
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)

# ---------------- Save Data (FIXED) ----------------
def save_data(df, new_rows):
    """Fixed version - saves only NEW rows to Google Sheets"""
    # Save CSV first
    df.to_csv(DATA_FILE, index=False)
    
    # Send only newly added rows to Google Sheets
    success_count = 0
    for _, row in new_rows.iterrows():
        row_dict = row.to_dict()
        row_dict["Timestamp"] = pd.Timestamp.now().isoformat()
        if save_to_google_sheet(row_dict):
            success_count += 1
        else:
            st.error(f"❌ Failed to save: {row['Athlete Name']} to Google Sheets")
    
    if success_count == len(new_rows):
        st.markdown(f"""
        <div class="success-box">
            ✅ All {success_count} players saved to Google Sheets successfully!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="error-box">
            ⚠️ Saved {success_count}/{len(new_rows)} to Google Sheets. CSV backup saved locally.
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# PAGE 1 — Select Championship
# =====================================================
if st.session_state.page == "select_championship":
    st.markdown(f"""
    <div class="image-row">
        <img src="{img1}">
        <img src="{img2}">
        <img src="{img3}">
        <img src="{img4}">
    </div>
    """, unsafe_allow_html=True)

    st.title("🏆 Select Championship")
    championship = st.selectbox(
        "Please select the championship you want to register for:",
        [
            "African Master Course",
            "African Open Traditional Karate Championship",
            "North Africa Unitied Karate Championship (General)"
        ]
    )

    if st.button("Next ➜", use_container_width=True):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        st.session_state.new_rows = []
        safe_rerun()
    st.stop()

# =====================================================
# PAGE 2 — Registration (IMPROVED)
# =====================================================
if st.session_state.page == "registration":
    # Back button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.page = "select_championship"
            safe_rerun()

    st.markdown(f"""
    <div class="image-row">
        <img src="{img1}">
        <img src="{img2}">
        <img src="{img3}">
        <img src="{img4}">
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<h2 style='color:#1f77b4'>🏆 Registration: {st.session_state.selected_championship}</h2>",
        unsafe_allow_html=True
    )

    athletes_data = []
    
    # ------------------------------------------------------------
    # African Master Course
    # ------------------------------------------------------------
    if st.session_state.selected_championship == "African Master Course":
        course_type = st.selectbox("Choose course type:", ["Master", "General"])
        club = st.text_input("Enter Club for all players", key="club_master")
        num_players = st.number_input("Number of players to add:", min_value=1, max_value=50, value=5)

        belt_options = [
            "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
            "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
            "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
            "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
            "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
        ]

        for i in range(num_players):
            with st.expander(f"👤 Player {i+1}", expanded=(i<2)):
                col1, col2 = st.columns(2)
                with col1:
                    athlete_name = st.text_input("Athlete Name *", key=f"name_master_{i}")
                    dob = st.date_input("Date of Birth *", min_value=date(1960,1,1), max_value=date.today(), key=f"dob_master_{i}")
                    sex = st.selectbox("Sex *", ["Male", "Female"], key=f"sex_master_{i}")
                with col2:
                    code = st.text_input("Player Code *", key=f"code_master_{i}")
                    belt = st.selectbox("Belt Degree *", belt_options, key=f"belt_master_{i}")
                    nationality = st.text_input("Nationality *", key=f"nat_master_{i}")
                    phone = st.text_input("Phone Number *", key=f"phone_master_{i}")

                if athlete_name and code:  # Only add if basic info exists
                    athletes_data.append({
                        "Athlete Name": athlete_name.strip(),
                        "Club": club.strip(),
                        "Nationality": nationality.strip(),
                        "Coach Name": "",
                        "Phone Number": phone.strip(),
                        "Date of Birth": str(dob),
                        "Sex": sex,
                        "Player Code": code.strip(),
                        "Belt Degree": belt,
                        "Competitions": "",
                        "Federation": "",
                        "Timestamp": pd.Timestamp.now().isoformat(),
                        "Championship": f"African Master Course - {course_type}"
                    })

    # ------------------------------------------------------------
    # Other Championships (IMPROVED)
    # ------------------------------------------------------------
    else:
        col1, col2 = st.columns(2)
        with col1:
            club = st.text_input("Club *", key="club")
            nationality = st.text_input("Nationality *", key="nationality")
        with col2:
            coach_name = st.text_input("Coach Name *", key="coach_name")
            phone_number = st.text_input("Coach Phone *", key="phone_number")
        
        num_players = st.number_input("Number of players:", min_value=1, max_value=50, value=5)

        belt_options = [
            "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
            "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
            "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
            "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
            "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
        ]

        for i in range(num_players):
            with st.expander(f"👤 Player {i+1}", expanded=(i<2)):
                col1, col2 = st.columns(2)
                with col1:
                    athlete_name = st.text_input("Athlete Name *", key=f"name_{i}")
                    dob = st.date_input("Date of Birth *", min_value=date(1960,1,1), max_value=date.today(), key=f"dob_{i}")
                    sex = st.selectbox("Sex *", ["Male", "Female"], key=f"sex_{i}")
                with col2:
                    code = st.text_input("Player Code *", key=f"code_{i}")
                    belt = st.selectbox("Belt Degree *", belt_options, key=f"belt_{i}")

                federation_champs = [
                    "African Open Traditional Karate Championship",
                    "North Africa Unitied Karate Championship (General)"
                ]
                if st.session_state.selected_championship in federation_champs:
                    federation = st.selectbox(
                        "Federation *",
                        ["Egyptian Traditional Karate Federation", "United General Federation"],
                        key=f"fed_{i}"
                    )
                    comp_list = ["Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                                "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"] \
                               if federation=="Egyptian Traditional Karate Federation" else \
                               ["Individual Kata","Kata Team","Kumite Ibon","Kumite Nihon",
                                "Kumite Sanbon","Kumite Rote Shine"]
                else:
                    federation = ""
                    comp_list = ["Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                                "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"]

                competitions = st.multiselect("Competitions *", comp_list, key=f"comp_{i}")

                if athlete_name and code:  # Only add if basic info exists
                    athletes_data.append({
                        "Athlete Name": athlete_name.strip(),
                        "Club": club.strip(),
                        "Nationality": nationality.strip(),
                        "Coach Name": coach_name.strip(),
                        "Phone Number": phone_number.strip(),
                        "Date of Birth": str(dob),
                        "Sex": sex,
                        "Player Code": code.strip(),
                        "Belt Degree": belt,
                        "Competitions": ", ".join(competitions),
                        "Federation": federation,
                        "Timestamp": pd.Timestamp.now().isoformat(),
                        "Championship": st.session_state.selected_championship
                    })

    # ---------------- Preview & Submit ----------------
    if athletes_data:
        st.subheader("📋 Preview")
        preview_df = pd.DataFrame(athletes_data)
        st.dataframe(preview_df, use_container_width=True)
        
        if st.button(f"✅ Submit {len(athletes_data)} Players", type="primary", use_container_width=True):
            df = load_data()
            errors = []
            
            # Validation
            for athlete in athletes_data:
                required = ["Athlete Name", "Player Code", "Belt Degree", "Club", "Nationality", "Phone Number"]
                for field in required:
                    if not str(athlete[field]).strip():
                        errors.append(f"Missing {field}: {athlete['Athlete Name']}")
                
                # Duplicate check
                existing = df[df["Championship"] == athlete["Championship"]]["Player Code"].astype(str)
                if str(athlete["Player Code"]) in existing.values:
                    errors.append(f"Duplicate Player Code '{athlete['Player Code']}': {athlete['Athlete Name']}")
                
                if st.session_state.selected_championship != "African Master Course":
                    if not athlete["Competitions"].strip():
                        errors.append(f"No competitions: {athlete['Athlete Name']}")
                    if not athlete["Coach Name"].strip():
                        errors.append(f"No coach: {athlete['Athlete Name']}")

            if errors:
                st.error("❌ Fix these errors:")
                for error in errors:
                    st.write(f"• {error}")
            else:
                # Add to dataframe
                new_df = pd.DataFrame(athletes_data)
                df = pd.concat([df, new_df], ignore_index=True)
                
                # Save with fixed logic
                st.session_state.new_rows = new_df
                save_data(df, new_df)
                
                st.success(f"🎉 {len(athletes_data)} players registered successfully!")
                st.balloons()
                
                # Clear form
                if st.button("➕ Add More Players"):
                    safe_rerun()
                st.stop()

    else:
        st.info("📝 Fill in player details above to preview and submit.")

# ---------------- Admin Panel (SECURE) ----------------
with st.sidebar:
    st.header("🔐 Admin")
    admin_password = st.text_input("Password", type="password")
    if hash_password(admin_password) == ADMIN_HASH:
        st.success("✅ Admin Access")
        df = load_data()
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=400)
            
            buffer = io.BytesIO()
            filename = st.session_state.get("selected_championship", "athletes").replace(" ", "_")
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            
            st.download_button(
                "📥 Download Excel",
                buffer,
                file_name=f"{filename}_{date.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.metric("Total Players", len(df))
            st.metric("Championships", df["Championship"].nunique())
    else:
        st.info("Enter password for admin access")
