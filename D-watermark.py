import streamlit as st
import os
import cv2
import numpy as np
import easyocr
from moviepy.editor import VideoFileClip

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI Jigsaw Watermark Remover", page_icon="🤖")

st.title("🤖 AI Jigsaw Watermark Remover")
st.markdown("### ค้นหาและลบลายน้ำอัตโนมัติด้วย AI - *ความประณีตระดับสแกนพิกเซล*")

# โหลด AI Model (ใส่ cache ไว้เพื่อไม่ให้โหลดซ้ำทุกครั้งที่กดปุ่ม)
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr_reader()

# ส่วนอินพุตชื่อลายน้ำ
target_text = st.text_input("พิมพ์ชื่อลายน้ำที่ต้องการลบ (เช่น ชื่อเพจ หรือ ID):", placeholder="เช่น Tok-ta-gon")
padding = st.slider("เพิ่มระยะเผื่อการตัด (Padding Pixels):", 0, 100, 20)

uploaded_file = st.file_uploader("เลือกวิดีโอ", type=["mp4", "mov"])

if uploaded_file and target_text:
    input_path = "temp_input.mp4"
    output_path = "ai_cleaned_output.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.video(input_path)

    if st.button("🔍 สแกนหาลายน้ำและเริ่มลบ"):
        try:
            with st.spinner("AI กำลังวิเคราะห์หาตำแหน่งลายน้ำ..."):
                clip = VideoFileClip(input_path)
                # ดึงเฟรมแรกมาสแกน
                first_frame = clip.get_frame(0)
                
                # ใช้ EasyOCR ค้นหาข้อความ
                results = reader.readtext(first_frame)
                
                found_bbox = None
                for (bbox, text, prob) in results:
                    # เช็คว่ามีคำที่ต้องการลบอยู่ในข้อความที่เจอไหม (Case insensitive)
                    if target_text.lower() in text.lower():
                        found_bbox = bbox
                        st.write(f"✅ ตรวจพบ: '{text}' (ความแม่นยำ: {prob:.2f})")
                        break
                
                if found_bbox:
                    # คำนวณพิกัดเพื่อ Crop (EasyOCR คืนค่า [top-left, top-right, bottom-right, bottom-left])
                    x_coords = [p[0] for p in found_bbox]
                    y_coords = [p[1] for p in found_bbox]
                    
                    x1, y1 = min(x_coords), min(y_coords)
                    x2, y2 = max(x_coords), max(y_coords)
                    
                    # วิเคราะห์ว่าลายน้ำอยู่โซนไหนเพื่อเลือกวิธีตัดที่เหมาะสม
                    # ในที่นี้เราจะใช้วิธี Crop ส่วนที่ "ไม่ใช่" ลายน้ำไว้ (ตัวอย่างนี้คือการตัดขอบที่มีลายน้ำทิ้ง)
                    w, h = clip.size
                    
                    # ถ้าลายน้ำอยู่ขอบล่าง (พบบ่อยที่สุด)
                    if y2 > h * 0.7:
                        new_h = y1 - padding
                        final_clip = clip.crop(x1=0, y1=0, x2=w, y2=new_h)
                        st.info(f"ระบบตรวจพบลายน้ำที่ขอบล่าง: กำลังตัดวิดีโอให้เหลือความสูง {new_h}px")
                    # ถ้าลายน้ำอยู่ขอบบน
                    elif y1 < h * 0.3:
                        new_y1 = y2 + padding
                        final_clip = clip.crop(x1=0, y1=new_y1, x2=w, y2=h)
                        st.info(f"ระบบตรวจพบลายน้ำที่ขอบบน: กำลังตัดวิดีโอเริ่มที่ {new_y1}px")
                    else:
                        st.warning("⚠️ ลายน้ำอยู่กลางภาพ การ Crop อาจทำให้เนื้อหาหายเยอะ แนะนำใช้การเบลอแทน")
                        final_clip = clip # ให้ผ่านไปก่อน
                    
                    # เริ่ม Render
                    st.text("กำลังประมวลผลวิดีโอใหม่...")
                    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                    
                    st.success("✨ AI จัดการให้เรียบร้อยแล้ว!")
                    with open(output_path, "rb") as f:
                        st.download_button("📥 ดาวน์โหลดผลลัพธ์", f, file_name="ai_cleaned.mp4")
                    
                    clip.close()
                    final_clip.close()
                else:
                    st.error(f"❌ AI หาคำว่า '{target_text}' ไม่พบในเฟรมแรก ลองปรับชื่อหรือใช้ระบบ Manual Crop ครับ")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
            if "Memory" in str(e):
                st.warning("ทรัพยากรบน Cloud ไม่พอสำหรับวิดีโอขนาดใหญ่เกินไป")

st.divider()
st.caption("AI Jigsaw Watermark Remover - Powered by EasyOCR ☀️")
