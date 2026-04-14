import streamlit as st
import os

# แก้ปัญหาการ Import สำหรับ MoviePy หลายเวอร์ชัน
try:
    from moviepy.editor import VideoFileClip
except (ImportError, ModuleNotFoundError):
    from moviepy.video.io.VideoFileClip import VideoFileClip

def remove_watermark_by_crop(input_path, output_path, x1, y1, x2, y2):
    try:
        # โหลดคลิปวิดีโอ
        clip = VideoFileClip(input_path)
        
        # สั่ง Crop เอาเฉพาะส่วนที่เราต้องการ
        cropped_clip = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
        
        # เซฟไฟล์ใหม่ (ใช้ temp audio file เพื่อลด error บน Cloud)
        cropped_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        clip.close() # ปิดไฟล์เพื่อคืน Memory (ความประณีตระดับ Jigsaw Master)
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        return False

# ส่วน UI ของ Streamlit
st.title("✂️ Jigsaw Watermark Remover")
uploaded_file = st.file_uploader("เลือกวิดีโอที่ต้องการลบลายน้ำ", type=["mp4", "mov", "avi"])

if uploaded_file:
    # บันทึกไฟล์ชั่วคราว
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video("temp_video.mp4")
    
    if st.button("🚀 เริ่มตัดลายน้ำออก (Crop)"):
        with st.spinner("กำลังประมวลผล..."):
            # ตัวอย่างพิกัด (พี่สามารถเพิ่ม Slider มาปรับค่า x1, y1, x2, y2 ได้ทีหลังครับ)
            success = remove_watermark_by_crop("temp_video.mp4", "cleaned_video.mp4", 0, 0, 1920, 1000)
            
            if success:
                st.success("เสร็จเรียบร้อย!")
                with open("cleaned_video.mp4", "rb") as file:
                    st.download_button("📥 ดาวน์โหลดวิดีโอ", file, "cleaned_video.mp4")
