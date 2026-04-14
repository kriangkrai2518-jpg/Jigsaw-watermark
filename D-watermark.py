import streamlit as st
import os

# ระบบจัดการ Import แบบยืดหยุ่น (ป้องกัน Error จากเวอร์ชัน Library)
try:
    from moviepy.editor import VideoFileClip
except (ImportError, ModuleNotFoundError):
    from moviepy.video.io.VideoFileClip import VideoFileClip

# ตั้งค่าหน้าเว็บให้ดูเป็น Jigsaw Master
st.set_page_config(page_title="Jigsaw Watermark Remover", page_icon="✂️")

st.title("✂️ Jigsaw Watermark Remover")
st.markdown("### ระบบลบลายน้ำวิดีโอ (Crop Mode) - *ประณีตและรวดเร็ว*")

# --- ส่วน Sidebar สำหรับปรับแต่ง ---
st.sidebar.header("🛠️ ตั้งค่าการตัดลายน้ำ")
st.sidebar.info("ปรับพิกัดเพื่อตัดขอบที่มีลายน้ำออก")

# พิกัดสำหรับ Crop (ค่าเริ่มต้นคือไม่ตัดเลย)
left = st.sidebar.number_input("ตัดขอบซ้าย (x1)", 0, 4000, 0)
top = st.sidebar.number_input("ตัดขอบบน (y1)", 0, 4000, 0)
right_offset = st.sidebar.number_input("ตัดขอบขวาเข้ามาระยะ", 0, 4000, 0)
bottom_offset = st.sidebar.number_input("ตัดขอบล่างขึ้นมาระยะ", 0, 4000, 50) # ส่วนใหญ่อยู่ขอบล่าง

# --- ส่วนอัปโหลดไฟล์ ---
uploaded_file = st.file_uploader("เลือกวิดีโอที่ต้องการจัดการ", type=["mp4", "mov", "avi"])

if uploaded_file:
    # บันทึกไฟล์ชั่วคราวลงในเครื่อง Server
    input_path = "temp_input.mp4"
    output_path = "cleaned_output.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info("📌 วิดีโอต้นฉบับ:")
    st.video(input_path)
    
    # ปุ่มเริ่มการประมวลผล
    if st.button("🚀 เริ่มตัดลายน้ำออกเดี๋ยวนี้"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("กำลังโหลดวิดีโอ...")
            clip = VideoFileClip(input_path)
            w, h = clip.size
            
            # คำนวณพิกัดใหม่
            # x2 ต้องไม่เกินความกว้าง, y2 ต้องไม่เกินความสูง
            x2 = w - right_offset
            y2 = h - bottom_offset
            
            status_text.text(f"กำลังประมวลผลการ Crop: {left},{top} ถึง {x2},{y2}...")
            progress_bar.progress(30)
            
            # สั่ง Crop
            cropped_clip = clip.crop(x1=left, y1=top, x2=x2, y2=y2)
            
            # สั่งเขียนไฟล์ (ใช้ libx264 เพื่อให้รันบนเว็บได้ทุกเบราว์เซอร์)
            # audio_codec='aac' ช่วยลดปัญหาเสียงหายบน Streamlit Cloud
            cropped_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                temp_audiofile='temp-audio.m4a', 
                remove_temp=True
            )
            
            progress_bar.progress(100)
            status_text.text("เสร็จสมบูรณ์!")
            st.success("✨ ลบลายน้ำ (Crop) เรียบร้อยแล้ว!")
            
            # ปุ่มดาวน์โหลด
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 ดาวน์โหลดวิดีโอที่แก้ไขแล้ว",
                    data=file,
                    file_name="jigsaw_cleaned.mp4",
                    mime="video/mp4"
                )
            
            # ปิดคลิปเพื่อคืน Memory
            clip.close()
            cropped_clip.close()

        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            st.warning("คำแนะนำ: ลองตรวจสอบว่าพิกัดที่ระบุไม่เกินขนาดของวิดีโอต้นฉบับ")

st.divider()
st.caption("Jigsaw Watermark Remover - พัฒนาโดย Jigsaw Master AI ☀️")
