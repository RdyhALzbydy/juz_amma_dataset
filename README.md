# Juz Amma Dataset

مجموعة بيانات جزء عم للذكاء الاصطناعي - تحتوي على تسجيلات صوتية نظيفة ونصوص مُفهرسة لجميع سور جزء عم من القرآن الكريم.

## المحتويات

### 📁 المجلدات الأساسية

- **`transcripts/`** - ملفات JSON تحتوي على النصوص المستخرجة بـ Whisper مع timestamps دقيقة
- **`simple_clean_surahs/`** - سور جزء عم النظيفة (JSON & TXT) مع إزالة البسملة

### 🎵 الملفات الصوتية 

📥 **تحميل الصوتيات:** [SharePoint Link](https://aiplacez-my.sharepoint.com/:f:/g/personal/radhyah_saudiaip_com/EkrtY3Ck8X5GmMAu_GTQZH0BtyouOHhQpmhfEiU1LH9BNA?e=oc2iwM)

- **`downloaded_audio/`** - التسجيلات الصوتية الأصلية من YouTube (29 ملف)
- **`clean_audio/`** - التسجيلات الصوتية المُنظفة والمُحسنة (29 ملف)
- **`renamed_audio/`** - الصوتيات مُعاد تسميتها (عينة 1.wav - عينة 29.wav)

### 🐍 الأكواد المهمة

#### `download_quran_audio.py`
- تحميل التسجيلات من YouTube
- تحويل إلى WAV عالي الجودة
- تنظيم أسماء الملفات

#### `audio_cleaner.py` 
- إزالة الضوضاء والتشويش
- تطبيع مستوى الصوت
- تحسين جودة الصوت للتدريب

#### `whisper_transcriber.py`
- استخراج النصوص باستخدام Whisper Large-v3
- إنتاج timestamps دقيقة لكل كلمة
- تصدير JSON منظم

#### `simple_basmalah_cleaner.py`
- إزالة البسملة من بداية كل سورة
- تنظيف النصوص للتدريب
- إنتاج ملفات JSON و TXT

## البيانات

- **29 قارئ مختلف** لجزء عم كاملاً
- **19 سورة** من سورة النبأ (78) إلى سورة الناس (114)
- **تسجيلات عالية الجودة** مُنظفة ومُحسنة
- **نصوص دقيقة** مع timestamps لكل كلمة

## الاستخدام

```bash
# تحميل الصوتيات
python download_quran_audio.py

# تنظيف وتحسين الصوت
python audio_cleaner.py

# استخراج النصوص
python whisper_transcriber.py

# تنظيف البسملة
python simple_basmalah_cleaner.py
```

## الخطوة التالية
قص الصوتيات حسب الآيات لإنشاء dataset مُفصل لكل آية منفرداً.

## المتطلبات

```
torch
torchaudio  
whisper-openai
pydub
librosa
noisereduce
yt-dlp
```