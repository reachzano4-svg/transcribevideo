import streamlit as st
import whisper
import datetime
import os

# បង្កើត Path ពេញលេញសម្រាប់ File បណ្តោះអាសន្ន
TEMP_FILE_PATH = "temp_audio_file.mp4"

if uploaded_file is not None:
    with open(TEMP_FILE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # បន្ទាប់មកប្រើ Path នេះក្នុង model.transcribe
    result = model.transcribe(TEMP_FILE_PATH)
    
    # បន្ទាប់ពីប្រើរួច គួរលុបវាចេញវិញដើម្បីកុំឱ្យពេញ Server
    if os.path.exists(TEMP_FILE_PATH):
        os.remove(TEMP_FILE_PATH)

# មុខងារបំប្លែងពេលវេលាឱ្យទៅជា Format របស់ SRT (00:00:00,000)
def format_time(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

st.title("🎥 Video to SRT Transcriber")
st.write("បំប្លែងវីដេអូ ឬសំឡេងទៅជាអត្ថបទអក្សររត់ក្រោម (SRT)")

# ១. បង្ហោះ File
uploaded_file = st.file_uploader("ជ្រើសរើសវីដេអូ (mp4, mp3, m4a)", type=["mp4", "mp3", "m4a"])

if uploaded_file is not None:
    # រក្សាទុក File បណ្តោះអាសន្ន
    with open("temp_file", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("ឯកសារត្រូវបានបញ្ចូលរួចរាល់!")
    
    if st.button("ចាប់ផ្តើមបំប្លែង (Transcribe)"):
        with st.spinner("កំពុងដំណើរការ... អាចប្រើពេលបន្តិចអាស្រ័យលើទំហំវីដេអូ"):
            # ២. Load Model (ប្រើ 'tiny' ឬ 'base' សម្រាប់ Online ព្រោះវាស្រាល)
            model = whisper.load_model("base")
            result = model.transcribe("temp_file")

            # ៣. បង្កើត Format SRT
            srt_content = ""
            for i, segment in enumerate(result['segments']):
                start = format_time(segment['start'])
                end = format_time(segment['end'])
                text = segment['text'].strip()
                srt_content += f"{i + 1}\n{start} --> {end}\n{text}\n\n"

            # ៤. បង្ហាញលទ្ធផល និងឱ្យ Download
            st.text_area("លទ្ធផលអត្ថបទ:", srt_content, height=300)
            
            st.download_button(
                label="ទាញយកឯកសារ .srt",
                data=srt_content,
                file_name="subtitle.srt",
                mime="text/plain"
            )
