import os
import hashlib

# المسار الجديد بعد النقل لداخل مجلد SecLists
directory = "Passwords/Common-Credentials"

hash_algorithms = {
    "MD5": hashlib.md5,
    "SHA1": hashlib.sha1,
    "SHA224": hashlib.sha224,
    "SHA256": hashlib.sha256,
    "SHA384": hashlib.sha384,
    "SHA512": hashlib.sha512
}

def generate_hash_files():
    if not os.path.exists(directory):
        print(f"❌ المجلد غير موجود: {directory}")
        return

    # التاكد من جلب الملفات النصية فقط والتي لم يتم تحويلها مسبقاً
    files = []
    for f in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, f)):
            if not any(f.endswith(f"_{algo}.txt") for algo in hash_algorithms.keys()):
                files.append(f)

    if not files:
        print("⚠️ لم يتم العثور على ملفات جديدة لمعالجتها.")
        return

    for filename in files:
        input_path = os.path.join(directory, filename)
        base_name, ext = os.path.splitext(filename)
        
        print(f"⏳ جاري معالجة الملف: {filename} ...")
        
        output_files = {}
        try:
            # فتح ملفات المخرجات
            for algo in hash_algorithms.keys():
                out_name = f"{base_name}_{algo}{ext}"
                out_path = os.path.join(directory, out_name)
                output_files[algo] = open(out_path, 'w', encoding='utf-8')
                
            # القراءة سطراً بسطر لتقليل استهلاك الرام
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
                for line in infile:
                    word = line.strip()
                    if not word:
                        continue
                        
                    for algo, func in hash_algorithms.items():
                        hashed_word = func(word.encode('utf-8')).hexdigest()
                        output_files[algo].write(hashed_word + '\n')
                        
            print(f"✅ تم إنشاء جميع ملفات الهاش للملف: {filename}")
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء معالجة {filename}: {e}")
            
        finally:
            for f in output_files.values():
                f.close()
                
    print("\n🎉 تم الانتهاء بنجاح من جميع الملفات!")

if __name__ == "__main__":
    generate_hash_files()