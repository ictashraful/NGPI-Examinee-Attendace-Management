import streamlit as st
import pandas as pd
import os
from PIL import Image

# ১. পেজ সেটআপ এবং আল্ট্রা-ক্লিন কর্পোরেট থিম কনফিগারেশন
st.set_page_config(page_title="Narsingdi Government Polytechnic Institute - Exam Control Portal", layout="wide")

# প্রিমিয়াম মিনিমালিস্ট লুক এবং গুগল ফন্ট (Hind Siliguri) ইন্টিগ্রেশন
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
    </style>
    """, unsafe_allow_html=True)

# ২. লগো এবং টাইটেল সেকশন
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
db_file = "attendance_database.csv"

if os.path.exists(file_name):
    df = pd.read_excel(file_name)
    df.columns = [str(col).strip() for col in df.columns]
    df['তারিখ'] = df['তারিখ'].ffill().astype(str).str.strip()
    df['সময়'] = df['সময়'].ffill().astype(str).str.strip()
    df['বিষয় কোড'] = df['বিষয় কোড'].ffill()
    df['বিষয়ের নাম'] = df['বিষয়ের নাম'].ffill()
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
        subject = row['বিষয়ের নাম']
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

        # স্থায়ী ডাটাবেস থেকে পূর্বের সেভ করা ভ্যালু রিকভারি লজিক
        saved_db_df = None
        if os.path.exists(db_file):
            try:
                saved_db_df = pd.read_csv(db_file)
            except:
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
                    
                    # প্রথম প্রায়োরিটি: ডাটাবেস ফাইল, দ্বিতীয় প্রায়োরিটি: ড্রাফট সেশন
                    default_val = item['মোট']
                    if saved_db_df is not None:
                        matched = saved_db_df[(saved_db_df['তারিখ'] == selected_date) & 
                                              (saved_db_df['সময়'] == selected_time) & 
                                              (saved_db_df['কক্ষ নম্বর'].astype(str) == str(room)) & 
                                              (saved_db_df['টেকনোলজি'] == item['টেকনোলজি'])]
                        if not matched.empty:
                            default_val = int(matched.iloc[0]['উপস্থিত'])
                    
                    saved_present = st.session_state.draft_storage.get(state_key, default_val)
                    
                    present = r_col3.number_input("উপস্থিত", min_value=0, max_value=item['মোট'], value=int(saved_present), key=state_key, label_visibility="collapsed")
                    absent = item['মোট'] - present
                    r_col4.markdown(f"<div class='data-row'><span class='absent-badge'>{absent} জন</span></div>", unsafe_allow_html=True)
                    
                    final_submission_list.append({
                        'তারিখ': selected_date, 'সময়': selected_time, 'কক্ষ নম্বর': room,
                        'টেকনোলজি': item['টেকনোলজি'], 'পর্ব': item['পর্ব'], 'বিষয়': item['বিষয়'],
                        'মোট পরীক্ষার্থী': item['মোট'], 'উপস্থিত': present, 'অনুপস্থিত': absent
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
                st.info("বর্তমান এন্ট্রিগুলো সাময়িকভাবে পরীক্ষা নিয়ন্ত্রণ কক্ষের মেমোরিতে সংরক্ষণ করা হয়েছে।")
                
            if final_btn:
                # স্থায়ী হার্ডড্রাইভ ব্যাকআপ ডাটাবেস প্রসেসিং
                new_data_df = pd.DataFrame(final_submission_list)
                if os.path.exists(db_file):
                    try:
                        old_df = pd.read_csv(db_file)
                        # ডুপ্লিকেট এন্ট্রি ওভাররাইট বা ক্লিন করা
                        combined_df = pd.concat([old_df, new_data_df]).drop_duplicates(subset=['তারিখ', 'সময়', 'কক্ষ নম্বর', 'টেকনোলজি'], keep='last')
                        combined_df.to_csv(db_file, index=False)
                    except:
                        new_data_df.to_csv(db_file, index=False)
                else:
                    new_data_df.to_csv(db_file, index=False)
                    
                st.success("✅ এই টাইম স্লটের তথ্য সফলভাবে হার্ডড্রাইভ ডাটাবেসে সেভ করা হয়েছে! এখন লগআউট করলেও ডাটা নিরাপদ থাকবে।")

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
            
        # ৭. মাস্টার ডাটাবেস ডাউনলোড (যেকোনো সময় পুরো পরীক্ষার ডাটা একসাথে ডাউনলোডের জন্য)
        if os.path.exists(db_file):
            st.write("---")
            st.subheader("📥 মাস্টার আর্কাইভ (সর্বমোট এন্ট্রি করা সকল পরীক্ষার ডাটাবেস)")
            full_db_df = pd.read_csv(db_file)
            full_csv = full_db_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📋 এ পর্যন্ত এন্ট্রি করা সকল স্লটের অল-ইন-ওয়ান রিপোর্ট ডাউনলোড করুন",
                data=full_csv,
                file_name="NPI_Mastar_Exam_Attendance_Database.csv",
                mime="text/csv",
                key="master_db_download"
            )
    else:
        st.warning("এই তারিখ এবং সময় স্লটে কোনো কক্ষে পরীক্ষার্থী বরাদ্দ খুঁজে পাওয়া যায়নি।")
else:
    st.error(f"দুঃখিত! ফোল্ডারে '{file_name}' নামের এক্সেল ফাইলটি পাওয়া যায়নি।")