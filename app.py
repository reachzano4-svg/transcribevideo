import streamlit as st
import whisper
import datetime
import os

# --- ១. កំណត់ការកំណត់ទំព័រ (ត្រូវតែនៅខាងលើគេបង្អស់) ---
st.set_page_config(page_title="Video to SRT & Login", page_icon="🎥")

# --- ២. មុខងារជំនួយ (Helper Functions) ---

def format_time(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def login():
    st.title("🔐 សូមចូលប្រើប្រាស់កម្មវិធី")
    with st.form("login_form"):
        username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)")
        password = st.text_input("លេខសម្ងាត់ (Password)", type="password")
        submit_button = st.form_submit_button("ចូលប្រើ (Login)")

        if submit_button:
            # ប្តូរ Username និង Password នៅទីនេះ
            if username == "admin" and password == "123456":
                st.session_state.logged_in = True
                st.success("ការចូលប្រើជោគជ័យ!")
                st.rerun()
            else:
                st.error("ឈ្មោះអ្នកប្រើប្រាស់ ឬលេខសម្ងាត់មិនត្រឹមត្រូវទេ!")

# --- ៣. ប្រព័ន្ធគ្រប់គ្រងការចូលប្រើ (Auth Logic) ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# --- ៤. ផ្នែកកម្មវិធីចម្បង (បន្ទាប់ពី Login រួច) ---

# ប៊ូតុង Logout នៅ Sidebar
st.sidebar.title("ការកំណត់")
if st.sidebar.button("ចាកចេញ (Log out)"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🎥 Video to SRT Transcriber")
st.write(f"សួស្តី **{st.session_state.get('username', 'អ្នកប្រើប្រាស់')}**! សូមបញ្ចូលវីដេអូដើម្បីចាប់ផ្តើម។")

uploaded_file = st.file_uploader("ជ្រើសរើសវីដេអូ ឬសំឡេង (mp4, mp3, m4a, wav)", type=["mp4", "mp3", "m4a", "wav"])

if uploaded_file is not None:
    st.info(f"ឯកសារដែលបានជ្រើសរើស: {uploaded_file.name}")
    
    if st.button("🚀 ចាប់ផ្តើមបំប្លែង (Transcribe)"):
        try:
            with st.spinner("កំពុងដំណើរការ... សូមរង់ចាំ (អាចប្រើពេលពីរបីនាទី)"):
                
                temp_filename = "temp_data_file"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # បើម៉ាស៊ីន Online ខ្សោយ ប្រើ model="tiny" ឬ "base"
                model = whisper.load_model("base")
                result = model.transcribe(temp_filename)

                srt_content = ""
                for i, segment in enumerate(result['segments']):
                    start = format_time(segment['start'])
                    end = format_time(segment['end'])
                    text = segment['text'].strip()
                    srt_content += f"{i + 1}\n{start} --> {end}\n{text}\n\n"

                st.success("✅ បំប្លែងរួចរាល់!")
                st.text_area("អត្ថបទដែលទាញបាន (Preview):", srt_content, height=250)
                
                st.download_button(
                    label="📥 ទាញយកឯកសារ .srt",
                    data=srt_content,
                    file_name=f"{uploaded_file.name}.srt",
                    mime="text/plain"
                )

                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        except Exception as e:
            st.error(f"មានបញ្ហាបច្ចេកទេសមួយបានកើតឡើង: {e}")
