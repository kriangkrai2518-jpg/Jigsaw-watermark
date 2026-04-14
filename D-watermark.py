from moviepy.editor import VideoFileClip

def remove_watermark_by_crop(input_path, output_path, x1, y1, x2, y2):
    # โหลดคลิปวิดีโอ
    clip = VideoFileClip(input_path)
    
    # สั่ง Crop เอาเฉพาะส่วนที่เราต้องการ (ระบุพิกัดที่ไม่มีลายน้ำ)
    # x1, y1 คือจุดเริ่มต้นบนซ้าย / x2, y2 คือจุดสิ้นสุดล่างขวา
    cropped_clip = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    
    # เซฟไฟล์ใหม่
    cropped_clip.write_videofile(output_path, codec="libx264")

# ตัวอย่างการใช้งาน:
# remove_watermark_by_crop("video_in.mp4", "video_out.mp4", x1=0, y1=0, x2=1920, y2=1000)
