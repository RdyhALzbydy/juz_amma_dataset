#!/usr/bin/env python3
"""
Audio Cleaning and Enhancement Script for AI Training
معالج الصوت وتنظيفه للتدريب على الذكاء الاصطناعي
"""

import os
import librosa
import numpy as np
import soundfile as sf
import noisereduce as nr
from scipy import signal
from pydub import AudioSegment
from pydub.silence import split_on_silence
import glob
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class AudioCleaner:
    def __init__(self, input_dir="downloaded_audio", output_dir="clean_audio"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.create_output_dir()
        
    def create_output_dir(self):
        """إنشاء مجلد الحفظ"""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 تم إنشاء مجلد: {self.output_dir}")
        
    def normalize_audio(self, audio, target_lufs=-23.0):
        """تطبيع الصوت - Audio Normalization"""
        # حساب RMS
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            # تطبيع بناءً على RMS
            target_rms = 0.1  # قيمة مرجعية
            scaling_factor = target_rms / rms
            audio = audio * scaling_factor
        
        # منع التشبع (Clipping Prevention)
        max_val = np.max(np.abs(audio))
        if max_val > 0.95:
            audio = audio * (0.95 / max_val)
            
        return audio
    
    def reduce_noise(self, audio, sr):
        """إزالة الضوضاء - Noise Reduction"""
        try:
            # استخدام noisereduce لإزالة الضوضاء
            reduced_noise = nr.reduce_noise(
                y=audio, 
                sr=sr,
                stationary=True,
                prop_decrease=0.8
            )
            return reduced_noise
        except Exception as e:
            print(f"⚠️ خطأ في إزالة الضوضاء: {e}")
            return audio
    
    def enhance_audio(self, audio, sr):
        """تحسين جودة الصوت - Audio Enhancement"""
        
        # 1. High-pass filter لإزالة الترددات المنخفضة غير المرغوبة
        nyquist = sr // 2
        low_cutoff = 80  # Hz
        high = low_cutoff / nyquist
        
        if high < 1.0:
            b, a = signal.butter(5, high, btype='high')
            audio = signal.filtfilt(b, a, audio)
        
        # 2. Spectral gating لإزالة الضوضاء الطيفية
        # حساب الطيف
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        
        # تطبيق gate على الأجزاء الهادئة
        threshold = np.percentile(magnitude, 10)  # 10% أقل قيم
        mask = magnitude > threshold
        stft_cleaned = stft * mask
        
        # العكس للحصول على الصوت المنظف
        audio_enhanced = librosa.istft(stft_cleaned)
        
        return audio_enhanced
    
    def segment_audio(self, audio_path, min_silence_len=500, silence_thresh=-40):
        """تقطيع الصوت وإزالة الصمت - Audio Segmentation"""
        try:
            # تحميل الملف باستخدام pydub
            audio = AudioSegment.from_wav(audio_path)
            
            # تقسيم الصوت بناءً على فترات الصمت
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,  # الحد الأدنى لفترة الصمت (ms)
                silence_thresh=silence_thresh,    # عتبة الصمت (dB)
                keep_silence=100                  # الاحتفاظ بقليل من الصمت (ms)
            )
            
            # دمج القطع الصغيرة مع بعضها البعض
            if len(chunks) > 1:
                # دمج القطع مع فاصل قصير
                final_audio = AudioSegment.empty()
                for i, chunk in enumerate(chunks):
                    if len(chunk) > 1000:  # تجاهل القطع الأقل من ثانية واحدة
                        final_audio += chunk
                        if i < len(chunks) - 1:  # إضافة فاصل قصير بين القطع
                            final_audio += AudioSegment.silent(duration=100)
                
                return final_audio
            else:
                return audio
                
        except Exception as e:
            print(f"⚠️ خطأ في تقطيع الصوت: {e}")
            return AudioSegment.from_wav(audio_path)
    
    def process_single_file(self, input_file, counter, total):
        """معالجة ملف واحد"""
        try:
            print(f"\n🔄 [{counter}/{total}] معالجة: {os.path.basename(input_file)}")
            
            # تحميل الملف الصوتي
            audio, sr = librosa.load(input_file, sr=None, mono=True)
            original_duration = len(audio) / sr
            
            print(f"   📊 المدة الأصلية: {original_duration:.1f} ثانية")
            print(f"   📊 معدل العينة: {sr} Hz")
            
            # 1. تطبيع الصوت (Audio Normalization)
            print("   🎛️ تطبيع الصوت...")
            audio = self.normalize_audio(audio)
            
            # 2. إزالة الضوضاء (Noise Reduction)
            print("   🔇 إزالة الضوضاء...")
            audio = self.reduce_noise(audio, sr)
            
            # 3. تحسين جودة الصوت (Audio Enhancement) 
            print("   ✨ تحسين جودة الصوت...")
            audio = self.enhance_audio(audio, sr)
            
            # حفظ الملف المؤقت للتقطيع
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            temp_file = os.path.join(self.output_dir, f"temp_{base_name}.wav")
            sf.write(temp_file, audio, sr)
            
            # 5. تقطيع الصوت وإزالة الصمت (Audio Segmentation)
            print("   ✂️ تقطيع الصوت وإزالة الصمت...")
            segmented_audio = self.segment_audio(temp_file)
            
            # حفظ الملف النهائي
            output_file = os.path.join(self.output_dir, f"clean_{base_name}.wav")
            segmented_audio.export(output_file, format="wav")
            
            # حذف الملف المؤقت
            os.remove(temp_file)
            
            # احصائيات
            final_duration = len(segmented_audio) / 1000  # pydub يستخدم milliseconds
            size_reduction = (1 - final_duration / original_duration) * 100
            
            print(f"   ✅ تم الانتهاء!")
            print(f"   📊 المدة النهائية: {final_duration:.1f} ثانية")
            print(f"   📉 تقليل الحجم: {size_reduction:.1f}%")
            print(f"   💾 حُفظ في: {output_file}")
            
            return True, {
                'original_duration': original_duration,
                'final_duration': final_duration,
                'size_reduction': size_reduction,
                'output_file': output_file
            }
            
        except Exception as e:
            print(f"   ❌ خطأ في معالجة الملف: {str(e)}")
            return False, None
    
    def process_all_files(self):
        """معالجة جميع الملفات"""
        print("🎵 بدء معالجة وتنظيف الملفات الصوتية")
        print("=" * 60)
        
        # البحث عن جميع ملفات WAV
        wav_files = glob.glob(os.path.join(self.input_dir, "*.wav"))
        total_files = len(wav_files)
        
        if total_files == 0:
            print("❌ لم يتم العثور على أي ملفات WAV")
            return
        
        print(f"📋 تم العثور على {total_files} ملف للمعالجة")
        print("=" * 60)
        
        success_count = 0
        failed_files = []
        processing_stats = []
        
        # معالجة كل ملف
        for i, wav_file in enumerate(wav_files, 1):
            success, stats = self.process_single_file(wav_file, i, total_files)
            
            if success:
                success_count += 1
                processing_stats.append(stats)
            else:
                failed_files.append(os.path.basename(wav_file))
        
        # تقرير النتائج النهائي
        print("\n" + "=" * 60)
        print("📊 تقرير المعالجة النهائي:")
        print(f"✅ نجح: {success_count}")
        print(f"❌ فشل: {len(failed_files)}")
        print(f"📁 الملفات المنظفة محفوظة في: {os.path.abspath(self.output_dir)}")
        
        if processing_stats:
            avg_original = sum(s['original_duration'] for s in processing_stats) / len(processing_stats)
            avg_final = sum(s['final_duration'] for s in processing_stats) / len(processing_stats)
            avg_reduction = sum(s['size_reduction'] for s in processing_stats) / len(processing_stats)
            
            print(f"\n📈 إحصائيات المعالجة:")
            print(f"   متوسط المدة الأصلية: {avg_original:.1f} ثانية")
            print(f"   متوسط المدة النهائية: {avg_final:.1f} ثانية")
            print(f"   متوسط تقليل الحجم: {avg_reduction:.1f}%")
        
        if failed_files:
            print(f"\n🚨 الملفات التي فشلت:")
            for file in failed_files:
                print(f"   - {file}")

def main():
    """الدالة الرئيسية"""
    cleaner = AudioCleaner()
    cleaner.process_all_files()

if __name__ == "__main__":
    main()