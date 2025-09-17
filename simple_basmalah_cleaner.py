#!/usr/bin/env python3
"""
منظف البسملة البسيط - إزالة أول 4 كلمات
Simple Basmalah cleaner - remove first 4 words
"""

import json
import os
import glob

def main():
    input_dir = "juz_amma_surahs" 
    output_dir = "simple_clean_surahs"
    
    # إنشاء مجلد الإخراج
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 تم إنشاء مجلد: {output_dir}")
    
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    
    if not json_files:
        print(f"❌ لم يتم العثور على ملفات JSON في {input_dir}")
        return
    
    processed_count = 0
    basmalah_removed_count = 0
    
    print("🕌 إزالة أول 4 كلمات من كل سورة (البسملة)")
    print("=" * 60)
    
    for json_file in sorted(json_files):
        filename = os.path.basename(json_file)
        print(f"🔄 معالجة: {filename}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'verses' not in data or not data['verses']:
                print(f"   ❌ لا توجد آيات في الملف")
                continue
            
            first_verse = data['verses'][0]
            original_text = first_verse['text']
            
            # تقسيم النص إلى كلمات
            words = original_text.split()
            
            if len(words) >= 4:
                # إزالة أول 4 كلمات مباشرة (البسملة)
                basmalah_words = words[:4]
                remaining_words = words[4:]
                
                basmalah_text = ' '.join(basmalah_words)
                
                if remaining_words:
                    new_text = ' '.join(remaining_words)
                    first_verse['text'] = new_text
                    
                    # إضافة معلومات التنظيف
                    data['basmalah_removed'] = True
                    data['original_first_verse'] = original_text
                    data['removed_basmalah'] = basmalah_text
                    data['correction_note'] = "تم إزالة أول 4 كلمات (البسملة) من الآية الأولى"
                    
                    basmalah_removed_count += 1
                    print(f"   ✅ تم إزالة: {basmalah_text}")
                    print(f"   🎯 النص الجديد: {new_text}")
                else:
                    print(f"   ⚠️ الآية كانت تحتوي على 4 كلمات فقط (بسملة)")
                    data['note'] = "الآية كانت تحتوي على البسملة فقط"
            else:
                print(f"   ❌ الآية تحتوي على أقل من 4 كلمات")
                data['note'] = f"الآية تحتوي على {len(words)} كلمات فقط"
            
            # حفظ الملف
            surah_name = data.get('surah_name', 'غير محدد')
            clean_filename = filename.replace('.json', '_بسيط.json')
            output_path = os.path.join(output_dir, clean_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # حفظ ملف نصي
            txt_filename = filename.replace('.json', '_بسيط.txt')
            txt_path = os.path.join(output_dir, txt_filename)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"{surah_name} - منظف بسيط\\n")
                f.write("=" * 50 + "\\n\\n")
                
                for verse in data['verses']:
                    verse_num = verse['verse_number']
                    verse_text = verse['text']
                    f.write(f"({verse_num}) {verse_text}\\n")
            
            processed_count += 1
            print(f"   ✅ تم حفظ: {clean_filename}")
            
        except Exception as e:
            print(f"   ❌ خطأ في معالجة {filename}: {e}")
        
        print()
    
    print("=" * 60)
    print("📊 تقرير التنظيف:")
    print(f"✅ تم معالجة: {processed_count} سورة")
    print(f"🧹 تم تنظيف: {basmalah_removed_count} سورة")
    print(f"📁 المجلد: {os.path.abspath(output_dir)}")
    print("🎉 تم الانتهاء من التنظيف!")

if __name__ == "__main__":
    main()