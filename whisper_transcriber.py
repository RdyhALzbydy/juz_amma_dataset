#!/usr/bin/env python3
"""
Whisper Large-v3 Transcription Script with Word-level Timestamps
سكريبت الترانسكربت باستخدام ويسبر مع timestamps لكل كلمة
"""

import os
import whisper
import json
import glob
import shutil
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class WhisperTranscriber:
    def __init__(self, input_dir="clean_audio", output_dir="transcripts"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.renamed_dir = "renamed_audio"
        self.model = None
        self.create_directories()
        
    def create_directories(self):
        """إنشاء المجلدات المطلوبة"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.renamed_dir, exist_ok=True)
        print(f"📁 تم إنشاء مجلد: {self.output_dir}")
        print(f"📁 تم إنشاء مجلد: {self.renamed_dir}")
    
    def load_whisper_model(self):
        """تحميل نموذج Whisper Large-v3"""
        print("🤖 تحميل نموذج Whisper Large-v3...")
        try:
            self.model = whisper.load_model("large-v3")
            print("✅ تم تحميل النموذج بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في تحميل النموذج: {e}")
            return False
    
    def rename_audio_files(self):
        """إعادة تسمية الملفات الصوتية إلى عينة 1، عينة 2، إلخ"""
        print("📝 بدء إعادة تسمية الملفات...")
        
        # العثور على جميع ملفات WAV النظيفة
        clean_files = glob.glob(os.path.join(self.input_dir, "clean_*.wav"))
        clean_files.sort()  # ترتيب أبجدي
        
        if not clean_files:
            print("❌ لم يتم العثور على ملفات صوتية نظيفة")
            return []
        
        renamed_files = []
        
        for i, old_file in enumerate(clean_files, 1):
            new_name = f"عينة {i}.wav"
            new_path = os.path.join(self.renamed_dir, new_name)
            
            # نسخ الملف بالاسم الجديد
            shutil.copy2(old_file, new_path)
            renamed_files.append((new_path, new_name))
            
            print(f"   ✅ {os.path.basename(old_file)} → {new_name}")
        
        print(f"📋 تم إعادة تسمية {len(renamed_files)} ملف")
        return renamed_files
    
    def transcribe_with_timestamps(self, audio_file, sample_name):
        """ترانسكربت الملف الصوتي مع timestamps لكل كلمة"""
        print(f"🎤 بدء ترانسكربت: {sample_name}")
        
        try:
            # إعدادات الترانسكربت
            result = self.model.transcribe(
                audio_file,
                language="ar",  # العربية
                word_timestamps=True,  # timestamps لكل كلمة
                verbose=False
            )
            
            # استخراج النص الكامل
            full_text = result["text"]
            
            # استخراج الكلمات مع timestamps
            words_with_timestamps = []
            
            for segment in result["segments"]:
                if "words" in segment:
                    for word_info in segment["words"]:
                        words_with_timestamps.append({
                            "word": word_info["word"].strip(),
                            "start": round(word_info["start"], 6),  # 6 خانات عشرية للقص الدقيق للكلمات
                            "end": round(word_info["end"], 6),
                            "confidence": round(word_info.get("probability", 0.0), 6)
                        })
            
            # إنشاء JSON النهائي
            transcript_data = {
                "metadata": {
                    "filename": sample_name,
                    "model": "whisper-large-v3",
                    "language": "ar",
                    "transcription_date": datetime.now().isoformat(),
                    "total_duration": round(result["segments"][-1]["end"] if result["segments"] else 0, 6),
                    "total_words": len(words_with_timestamps)
                },
                "full_text": full_text.strip(),
                "segments": [
                    {
                        "id": segment["id"],
                        "start": round(segment["start"], 6),
                        "end": round(segment["end"], 6),
                        "text": segment["text"].strip()
                    }
                    for segment in result["segments"]
                ],
                "words": words_with_timestamps
            }
            
            return transcript_data
            
        except Exception as e:
            print(f"   ❌ خطأ في الترانسكربت: {e}")
            return None
    
    def save_transcript_json(self, transcript_data, sample_name):
        """حفظ ترانسكربت كملف JSON"""
        base_name = os.path.splitext(sample_name)[0]  # إزالة امتداد .wav
        json_filename = f"{base_name}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 تم حفظ الترانسكربت: {json_filename}")
            return json_path
            
        except Exception as e:
            print(f"   ❌ خطأ في حفظ الملف: {e}")
            return None
    
    def process_all_files(self):
        """معالجة جميع الملفات"""
        print("🎵 بدء نظام الترانسكربت الشامل")
        print("=" * 60)
        
        # 1. تحميل نموذج Whisper
        if not self.load_whisper_model():
            return
        
        # 2. إعادة تسمية الملفات
        renamed_files = self.rename_audio_files()
        if not renamed_files:
            return
        
        print("\n" + "=" * 60)
        print("🎤 بدء عملية الترانسكربت...")
        
        success_count = 0
        failed_files = []
        total_files = len(renamed_files)
        
        # 3. ترانسكربت كل ملف
        for i, (file_path, sample_name) in enumerate(renamed_files, 1):
            print(f"\n🔄 [{i}/{total_files}] معالجة: {sample_name}")
            
            # ترانسكربت الملف
            transcript_data = self.transcribe_with_timestamps(file_path, sample_name)
            
            if transcript_data:
                # حفظ JSON
                json_path = self.save_transcript_json(transcript_data, sample_name)
                
                if json_path:
                    success_count += 1
                    print(f"   ✅ تم الانتهاء بنجاح!")
                    print(f"   📊 عدد الكلمات: {transcript_data['metadata']['total_words']}")
                    print(f"   ⏱️ المدة: {transcript_data['metadata']['total_duration']:.1f} ثانية")
                else:
                    failed_files.append(sample_name)
            else:
                failed_files.append(sample_name)
        
        # 4. تقرير النتائج النهائي
        print("\n" + "=" * 60)
        print("📊 تقرير الترانسكربت النهائي:")
        print(f"✅ نجح: {success_count}")
        print(f"❌ فشل: {len(failed_files)}")
        print(f"📁 الملفات الصوتية المعاد تسميتها: {os.path.abspath(self.renamed_dir)}")
        print(f"📁 ملفات الترانسكربت JSON: {os.path.abspath(self.output_dir)}")
        
        if failed_files:
            print(f"\n🚨 الملفات التي فشلت:")
            for file in failed_files:
                print(f"   - {file}")
        
        if success_count > 0:
            print(f"\n🎯 تم إنشاء {success_count} ملف JSON مع timestamps لكل كلمة!")
            print("📝 كل ملف JSON يحتوي على:")
            print("   - النص الكامل")
            print("   - تقسيم بالجمل مع timestamps") 
            print("   - كل كلمة مع بداية ونهاية ودقة بالثانية")
            print("   - معلومات وصفية (metadata)")

def main():
    """الدالة الرئيسية"""
    transcriber = WhisperTranscriber()
    transcriber.process_all_files()

if __name__ == "__main__":
    main()