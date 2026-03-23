import streamlit as st
import whisper
import datetime
import os

# --- ១. បង្កើតមុខងារជំនួយ (Helper Functions) ---

# មុខងារបំប្លែងពេលវេលាឱ្យទៅជា Format របស់ SRT (00:00:00,000)
def format_time(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# --- ២. រៀបចំ Interface របស់កម្មវិធី ---

st.set_page_config(page_title="Video to SRT", page_icon="🎥")
st.title("🎥 Video to SRT Transcriber")
st.write("បំប្លែងវីដេអូ ឬសំឡេងទៅជាអត្ថបទអក្សររត់ក្រោម (SRT)")

# កន្លែងសម្រាប់ Upload File (ដាក់នៅខាងលើដើម្បីឱ្យ Python ស្គាល់អថេរនេះមុន)
uploaded_file = st.file_uploader("ជ្រើសរើសវីដេអូ ឬសំឡេង (mp4, mp3, m4a, wav)", type=["mp4", "mp3", "m4a", "wav"])

# --- ៣. Logic ចម្បង ---

if uploaded_file is not None:
    st.info(f"ឯកសារដែលបានជ្រើសរើស: {uploaded_file.name}")
    
    # ប៊ូតុងចាប់ផ្តើម
    if st.button("🚀 ចាប់ផ្តើមបំប្លែង (Transcribe)"):
        try:
            with st.spinner("កំពុងដំណើរការ... សូមរង់ចាំ (អាចប្រើពេលពីរបីនាទី)"):
                
                # រក្សាទុក File បណ្តោះអាសន្ន ដើម្បីឱ្យ Whisper អាចអានបាន
                temp_filename = "temp_data_file"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Load Model (ប្រើ 'base' សម្រាប់តុល្យភាពល្បឿន និងភាពត្រឹមត្រូវ)
                model = whisper.load_model("base")
                
                # ចាប់ផ្តើមបំប្លែង
                result = model.transcribe(temp_filename)

                # បង្កើត Format SRT
                srt_content = ""
                for i, segment in enumerate(result['segments']):
                    start = format_time(segment['start'])
                    end = format_time(segment['end'])
                    text = segment['text'].strip()
                    srt_content += f"{i + 1}\n{start} --> {end}\n{text}\n\n"

                # បង្ហាញលទ្ធផល
                st.success("✅ បំប្លែងរួចរាល់!")
                st.text_area("អត្ថបទដែលទាញបាន (Preview):", srt_content, height=250)
                
                # ប៊ូតុងទាញយក
                st.download_button(
                    label="📥 ទាញយកឯកសារ .srt",
                    data=srt_content,
                    file_name=f"{uploaded_file.name}.srt",
                    mime="text/plain"
                )

                # លុប File បណ្តោះអាសន្នចេញពី Server ដើម្បីកុំឱ្យពេញ
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        except Exception as e:
            st.error(f"មានបញ្ហាបច្ចេកទេសមួយបានកើតឡើង: {e}")
