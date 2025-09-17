#!/usr/bin/env python3
"""
تنزيل التسجيلات الصوتية من يوتيوب وتحويلها إلى ملفات WAV
YouTube Audio Downloader and WAV Converter
"""

import os
import sys
import docx
import yt_dlp
from pydub import AudioSegment
import re
import time

def extract_urls_from_docx(docx_path):
    """استخراج الروابط من ملف الوورد"""
    doc = docx.Document(docx_path)
    urls = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text and ('youtube.com' in text or 'youtu.be' in text):
            urls.append(text)
    return urls

def sanitize_filename(filename):
    """تنظيف اسم الملف من الأحرف غير المسموحة"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.replace('\n', ' ').replace('\r', '')
    return filename[:200]  # تحديد طول الاسم

def download_and_convert_to_wav(url, output_dir="downloaded_audio", counter=1, total=1):
    """تنزيل الفيديو وتحويله إلى WAV"""
    try:
        # إعدادات yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # الحصول على معلومات الفيديو
            info = ydl.extract_info(url, download=False)
            video_title = sanitize_filename(info.get('title', 'Unknown'))
            video_id = info.get('id', 'unknown')
            
            print(f"[{counter}/{total}] بدء تنزيل: {video_title}")
            
            # تنزيل الصوت
            ydl.download([url])
            
            # العثور على الملف المنزل
            downloaded_files = []
            for file in os.listdir(output_dir):
                if video_id in file or video_title in file:
                    downloaded_files.append(file)
            
            if not downloaded_files:
                # البحث عن أحدث ملف صوتي
                audio_files = [f for f in os.listdir(output_dir) 
                             if f.endswith(('.mp3', '.m4a', '.webm', '.opus'))]
                if audio_files:
                    downloaded_files = [max(audio_files, key=lambda f: os.path.getctime(os.path.join(output_dir, f)))]
            
            if downloaded_files:
                downloaded_file = downloaded_files[0]
                file_path = os.path.join(output_dir, downloaded_file)
                
                # تحويل إلى WAV
                wav_filename = f"{video_id}_{sanitize_filename(video_title)}.wav"
                wav_path = os.path.join(output_dir, wav_filename)
                
                print(f"تحويل إلى WAV: {wav_filename}")
                
                # تحميل وتحويل الصوت
                audio = AudioSegment.from_file(file_path)
                audio.export(wav_path, format="wav")
                
                # حذف الملف الأصلي
                os.remove(file_path)
                
                print(f"✅ تم الانتهاء من: {video_title}")
                print(f"📁 حُفظ في: {wav_path}\n")
                
                return True, wav_filename
            else:
                print(f"❌ لم يتم العثور على الملف المنزل لـ: {video_title}")
                return False, None
                
    except Exception as e:
        print(f"❌ خطأ في تنزيل {url}: {str(e)}")
        return False, None

def main():
    """الدالة الرئيسية"""
    print("🎵 برنامج تنزيل التسجيلات الصوتية من يوتيوب وتحويلها إلى WAV")
    print("=" * 60)
    
    # إنشاء مجلد الحفظ
    output_dir = "downloaded_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # استخراج الروابط من ملف الوورد
    docx_file = "youtube_dataset.docx"
    if not os.path.exists(docx_file):
        print(f"❌ لم يتم العثور على ملف: {docx_file}")
        return
    
    urls = extract_urls_from_docx(docx_file)
    total_urls = len(urls)
    
    print(f"📋 تم العثور على {total_urls} رابط للتنزيل")
    print("=" * 60)
    
    success_count = 0
    failed_urls = []
    
    # تنزيل كل رابط
    for i, url in enumerate(urls, 1):
        print(f"🔄 معالجة الرابط {i}/{total_urls}")
        success, filename = download_and_convert_to_wav(url, output_dir, i, total_urls)
        
        if success:
            success_count += 1
        else:
            failed_urls.append(url)
        
        # توقف قصير بين التنزيلات
        if i < total_urls:
            time.sleep(2)
    
    # تقرير النتائج
    print("=" * 60)
    print("📊 تقرير النتائج:")
    print(f"✅ نجح: {success_count}")
    print(f"❌ فشل: {len(failed_urls)}")
    print(f"📁 الملفات محفوظة في: {os.path.abspath(output_dir)}")
    
    if failed_urls:
        print("\n🚨 الروابط التي فشلت:")
        for url in failed_urls:
            print(f"  - {url}")

if __name__ == "__main__":
    main()