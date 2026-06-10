import streamlit as st
import pandas as pd
import os
from PIL import Image
from supabase import create_client, Client

# ১. পেজ সেটআপ এবং আল্ট্রা-ক্লিন কর্পোরেট থিম কনফিগারেশন
st.set_page_config(page_title="Narsingdi Government Polytechnic Institute - Exam Control Portal", layout="wide")

# Supabase কানেকশন সেটিংস (Streamlit Secrets থেকে ডাটা নেবে)
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error("Supabase Credentials কনফিগার করা নেই। অনুগ্রহ করে Streamlit Secrets চেক করুন।")

# প্রিমিয়াম মিনিমালিস্ট লুক, লগইন স্ক্রিন এবং গুগল ফন্ট (Hind Siliguri) ইন্টিগ্রেশন
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    * { font-family: 'Hind Siliguri', sans-serif !important; }
    
    .title-container {
        background: #F8FAFC;
        padding: 16px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    .inst-title { font-size: 24px; font-weight: 700; color: #1E3A8A; text-align: center; margin: 0; padding: 0; }
    .sub-title { font-size: 16px; font-weight: 500; color: #475569; text-align: center; margin-top: 5px; }
    
    /* লগইন বক্সের স্টাইল */
    .login-box {
        max-width: 450px;
        margin: 50px auto;
        padding: 30px;
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .login-header {
        font-size: 20px; font-weight: 700; color: #1E3A8A; text-align: center; margin-bottom: 20px;
    }
    
    .slot-badge {
        font-size: 14px; color: #1E40AF; background-color: #EFF6FF; padding: 6px 14px;
        border-radius: 4px; font-weight: 600; display: inline-block; margin-bottom: 15px; border: 1px solid #BFDBFE;
    }
    
    .room-card-header { background-color: #1E3A8A; color: white; padding: 8px 14px; border-radius: 4px 4px 0 0; font-weight: 600; font-size: 15px; margin-top: 25px; }
    .table-header-bg { background-color: #F1F5F9; font-weight: 600; color: #334155; font-size: 14px; padding: 8px; border-bottom: 1px solid #CBD5E1; }
    .data-row { font-size: 14px; color: #334155; padding: 10px 8px; border-bottom: 1px solid #E2E8F0; align-items: center; }
    .absent-badge { color: #B91C1C; font-weight: 700; font-size: 15px; background: #FEF2F2; padding: 4px 10px; border-radius: 4px; border: 1px solid #FCA5A5; }
    
    div[data-testid="stMarkdownContainer"] + div input {
        background-color: #F0F4F8 !important; border: 1px solid #CBD5E1 !important; color: #0F172A !important; font-weight: 600 !important; border-radius: 4px !important;
    }
    
    div[data-testid="stForm"] { border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; background-color: #FFFFFF; }
    .stButton>button { border-radius: 4px !important; font-size: 14px !important; padding: 8px 16px !important; font-weight: 600 !important; }
    
    .logout-btn { text-align: right; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 🔑 ২. লগইন সিস্টেম রিলিজ এবং সেশন স্টেট হ্যান্ডলিং
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def check_login(username, password):
    # Streamlit Secrets থেকে ইউজারনেম ও পাসওয়ার্ড রিড করা
    correct_username = st.secrets.get("PORTAL_USERNAME", "admin")
    correct_password = st.secrets.get("PORTAL_PASSWORD", "npi1234")
    
    if username == correct_username and password == correct_password:
        st.session_state.logged_in = True
        st.success("🔓 লগইন সফল হয়েছে!")
        st.rerun()
    else:
        st.error("❌ ভুল ইউজারনেম অথবা পাসওয়ার্ড! আবার চেষ্টা করুন।")

# ব্যবহারকারী লগইন না থাকলে লগইন স্ক্রিন দেখাবে
if not st.session_state.logged_in:
    st.markdown('<div class="login-box"><div class="login-header">🔐 পরীক্ষা নিয়ন্ত্রণ কক্ষ লগইন প্যানেল</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        user_input = st.text_input("ইউজারনেম (Username)", placeholder="Username লিখুন")
        pass_input = st.text_input("পাসওয়ার্ড (Password)", type="password", placeholder="••••••••")
        submit_login = st.form_submit_button("লগইন করুন", use_container_width=True)
        
        if submit_login:
            check_login(user_input, pass_input)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # লগইন না করা পর্যন্ত নিচের বাকি কোড রান হওয়া বন্ধ থাকবে

# 🚪 লগআউট বাটন (লগইন থাকার পর স্ক্রিনের উপরে দেখাবে)
l_col1, l_col2 = st.columns([8, 1])
with l_col2:
    if st.button("🚪 লগআউট"):
        st.session_state.logged_in = False
        st.rerun()

# ৩. লগো এবং টাইটেল সেকশন (লগইন সফল হলে এটি লোড হবে)
logo_name = "NPI Logo.png"
if os.path.exists(logo_name):
    img_col, txt_col = st.columns([1, 8])
    with img_col:
        try:
            st.image(Image.open(logo_name), width=90)
        except:
            pass
    with txt_col:
        st.markdown('<div class="title-container"><div class="inst-title">নরসিংদী সরকারি পলিটেকনিক ইনস্টিটিউট</div><div class="sub-title">পরীক্ষা নিয়ন্ত্রণ কক্ষ | লাইভ উপস্থিতি মনিটরিং পোর্টাল</div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="title-container"><div class="inst-title">নরসিংদী সরকারি পলিটেকনিক ইনস্টিটিউট</div><div class="sub-title">পরীক্ষা নিয়ন্ত্রণ কক্ষ | লাইভ উপস্থিতি মনিটরিং পোর্টাল</div></div>', unsafe_allow_html=True)

file_name = "Room wise Student no Sheet.xlsx"

if os.path.exists(file_name):
    df = pd.read_excel(file_name)
    df.columns = [str(col).strip() for col in df.columns]
    df['তারিখ'] = df['তারিখ'].ffill().astype(str).str.strip()
    df['সময়'] = df['সময়'].ffill().astype(str).str.strip()
    df['বিষয় কোড'] = df['বিষয় কোড'].ffill()
    df['विषয়ের নাম'] = df['विषয়ের নাম'].ffill()
    df['পর্ব'] = df['পর্ব'].ffill()

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_date = st.selectbox("তারিখ নির্বাচন করুন", df['তারিখ'].unique())
    with f_col2:
        selected_time = st.selectbox("সময় / শিফট স্লট নির্বাচন করুন", df['সময়'].unique())

    filtered_df = df[(df['তারিখ'] == selected_date) & (df['সময়'] == selected_time)]
    st.markdown(f'<div class="slot-badge">বর্তমান স্লট: {selected_date} | {selected_time}</div>', unsafe_allow_html=True)

    room_cols = [col for col in df.columns if col.replace('.0', '').isdigit()]
    
    room_data_dict = {}
    for idx, row in filtered_df.iterrows():
        tech = row['টেকনোলজি']
        if pd.isna(tech) or 'সর্বমোট' in str(tech):
            continue
        subject = row['विषয়ের নাম']
        sub_code = str(row['বিষয় কোড']).split('.')[0]
        semester = row['পর্ব']
        
        for room_col in room_cols:
            val = row[room_col]
            try:
                count = int(float(val))
                if count > 0:
                    display_room = str(int(float(room_col)))
                    if display_room not in room_data_dict:
                        room_data_dict[display_room] = []
                    room_data_dict[display_room].append({
                        'টেকনোলজি': tech, 'পর্ব': semester, 'বিষয়': f"{subject} ({sub_code})", 'মোট': count
                    })
            except:
                continue

    if room_data_dict:
        sorted_rooms = sorted(room_data_dict.keys(), key=int)
        
        if "draft_storage" not in st.session_state:
            st.session_state.draft_storage = {}

        # Supabase থেকে ডাটা রিড করার লজিক
        saved_db_df = None
        try:
            response = supabase.table("attendance_database").select("*").eq("তারিখ", selected_date).eq("সময়", selected_time).execute()
            if response.data:
                saved_db_df = pd.DataFrame(response.data)
        except Exception as e:
            pass

        with st.form("attendance_sheet_form"):
            final_submission_list = []
            
            for room in sorted_rooms:
                st.markdown(f'<div class="room-card-header">কক্ষ নম্বর: {room}</div>', unsafe_allow_html=True)
                h_col1, h_col2, h_col3, h_col4 = st.columns([4, 2, 2, 2])
                h_col1.markdown("<div class='table-header-bg'>টেকনোলজি (পর্ব) ও বিষয়</div>", unsafe_allow_html=True)
                h_col2.markdown("<div class='table-header-bg'>মোট পরীক্ষার্থী</div>", unsafe_allow_html=True)
                h_col3.markdown("<div class='table-header-bg'>উপস্থিত পরীক্ষার্থী</div>", unsafe_allow_html=True)
                h_col4.markdown("<div class='table-header-bg'>অনুপস্থিত পরীক্ষার্থী</div>", unsafe_allow_html=True)
                
                for item in room_data_dict[room]:
                    r_col1, r_col2, r_col3, r_col4 = st.columns([4, 2, 2, 2])
                    r_col1.markdown(f"<div class='data-row'><b>{item['টেকনোলজি']}</b> ({item['পর্ব']})<br><small style='color:#64748B;'>{item['বিষয়']}</small></div>", unsafe_allow_html=True)
                    r_col2.markdown(f"<div class='data-row' style='font-weight:600;'>{item['মোট']} জন</div>", unsafe_allow_html=True)
                    
                    state_key = f"key_{selected_date}_{selected_time}_{room}_{item['টেকনোলজি']}"
                    
                    default_val = item['মোট']
                    if saved_db_df is not None and not saved_db_df.empty:
                        matched = saved_db_df[(saved_db_df['কক্ষ নম্বর'].astype(str) == str(room)) & 
                                              (saved_db_df['টেকনোলজি'] == item['টেকনোলজি'])]
                        if not matched.empty:
                            default_val = int(matched.iloc[0]['উপস্থিত'])
                    
                    saved_present = st.session_state.draft_storage.get(state_key, default_val)
                    
                    present = r_col3.number_input("উপস্থিত", min_value=0, max_value=item['মোট'], value=int(saved_present), key=state_key, label_visibility="collapsed")
                    absent = item['মোট'] - present
                    r_col4.markdown(f"<div class='data-row'><span class='absent-badge'>{absent} জন</span></div>", unsafe_allow_html=True)
                    
                    final_submission_list.append({
                        'তারিখ': selected_date, 'সময়': selected_time, 'কক্ষ নম্বর': str(room),
                        'টেকনোলজি': item['টেকনোলজি'], 'পর্ব': item['পর্ব'], 'বিষয়': item['বিষয়'],
                        'মোট পরীক্ষার্থী': int(item['মোট']), 'উপস্থিত': int(present), 'অনুপস্থিত': int(absent)
                    })
                st.write("") 

            st.write("---")
            b1, b2 = st.columns(2)
            with b1:
                draft_btn = st.form_submit_button("ড্রাফট সেভ করুন (Save Draft)")
            with b2:
                final_btn = st.form_submit_button("ফাইনাল সাবমিট (Final Submit)")

            if draft_btn:
                for data in final_submission_list:
                    k = f"key_{data['তারিখ']}_{data['সময়']}_{data['কক্ষ নম্বর']}_{data['টেকনোলজি']}"
                    st.session_state.draft_storage[k] = data['উপস্থিত']
                st.info("বর্তমান এন্ট্রিগুলো সাময়িকভাবে সেশন মেমোরিতে সংরক্ষণ করা হয়েছে।")
                
            if final_btn:
                try:
                    # পুরোনো ডুপ্লিকেট ডাটা ডিলিট করা
                    supabase.table("attendance_database").delete().eq("তারিখ", selected_date).eq("সময়", selected_time).execute()
                    
                    # নতুন ডাটা ক্লাউডে পুশ করা
                    supabase.table("attendance_database").insert(final_submission_list).execute()
                    st.success("✅ এই টাইম স্লটের তথ্য সফলভাবে ক্লাউড ডাটাবেসে সেভ করা হয়েছে!")
                    st.rerun()
                except Exception as e:
                    st.error(f"ডাটাবেসে সেভ করতে সমস্যা হয়েছে: {e}")

        # ৬. মাস্টার ডাউনলোড প্যানেল
        st.write("---")
        st.subheader("লাইভ স্ট্যাটিস্টিকস ও প্রফেশনাল রিপোর্ট")
        
        if final_submission_list:
            rep_df = pd.DataFrame(final_submission_list)
            t_allocated = rep_df['মোট পরীক্ষার্থী'].sum()
            t_present = rep_df['উপস্থিত'].sum()
            t_absent = rep_df['অনুপস্থিত'].sum()
            rate = (t_present / t_allocated * 100) if t_allocated > 0 else 0
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("মোট বরাদ্দ আসন", f"{t_allocated} জন")
            m2.metric("মোট উপস্থিত", f"{t_present} জন")
            m3.metric("মোট অনুপস্থিত", f"{t_absent} জন", delta_color="inverse")
            m4.metric("উপস্থিতির হার", f"{rate:.2f}%")
            
            csv_data = rep_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="এই শিফটের প্রফেশনাল রিপোর্ট ডাউনলোড করুন",
                data=csv_data,
                file_name=f"NPI_Attendance_Report_{selected_date}_{selected_time}.csv",
                mime="text/csv"
            )
            
        # ৭. মাস্টার ডাটাবেস ডাউনলোড (Supabase ক্লাউড থেকে সব ডাটা একসাথে নামানোর জন্য)
        try:
            full_response = supabase.table("attendance_database").select("*").execute()
            if full_response.data:
                st.write("---")
                st.subheader("📥 মাস্টার আর্কাইভ (ক্লাউড ডাটাবেস)")
                full_db_df = pd.DataFrame(full_response.data)
                if 'id' in full_db_df.columns: full_db_df.drop(columns=['id', 'created_at'], errors='ignore', inplace=True)
                
                full_csv = full_db_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📋 এ পর্যন্ত ক্লাউডে এন্ট্রি করা সকল স্লটের অল-ইন-ওয়ান রিপোর্ট ডাউনলোড করুন",
                    data=full_csv,
                    file_name="NPI_Master_Exam_Attendance_Database.csv",
                    mime="text/csv",
                    key="master_db_download"
                )
        except:
            pass
    else:
        st.warning("এই তারিখ এবং সময় স্লটে কোনো কক্ষে পরীক্ষার্থী বরাদ্দ খুঁজে পাওয়া যায়নি।")
else:
    st.error(f"দুঃখিত! ফোল্ডারে '{file_name}' নামের এক্সেল ফাইলটি পাওয়া যায়নি।")
