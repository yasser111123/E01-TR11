import streamlit as st
import os
import re

# إعدادات الصفحة لتكون متوافقة مع الهواتف والآيفون شاشات اللمس
st.set_page_config(page_title="E01-TR11", page_icon="🚀", layout="centered")

# تطبيق ثيم مظلم احترافي ومتناسق عبر الـ CSS لتسهيل القراءة بالعمل
st.markdown("""
    <style>
    .main { background-color: #1e1e2e; color: #cdd6f4; }
    .stTextArea textarea { background-color: #313244 !important; color: #cdd6f4 !important; font-family: 'Consolas', monospace !important; }
    div.stButton > button:first-child { background-color: #a6e3a1 !important; color: #11111b !important; font-weight: bold !important; width: 100%; border: none !important; padding: 10px !important; }
    .brand-title { color: #f38ba8; font-family: 'Arial Black', sans-serif; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .brand-sub { color: #89b4fa; font-family: 'Consolas', monospace; font-size: 14px; font-weight: bold; text-align: center; margin-bottom: 25px; }
    th { background-color: #45475a !important; color: #cdd6f4 !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

def load_database():
    file_name = "Gamme_Database.txt"
    db = {}
    if not os.path.exists(file_name):
        return None
    
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            if ":" in line:
                ref, version = line.split(":", 1)
                db[ref.strip()] = version.strip()
    return db

def clean_ref_for_matching(ref_string):
    ref_string = ref_string.strip()
    if ref_string and ref_string[-1].isalpha():
        ref_string = ref_string[:-1]
    return "".join([c for c in ref_string if c.isdigit()])

def process_single_line(line_text):
    """
    تحليل كل سطر على حدة بناءً على عدد الأرقام مفصولة بمسافات.
    الأقل من 4 أرقام تجمع لتكون الكمية، و 4 أرقام أو أكثر هي الـ Reference.
    """
    # استخراج كافة الأعداد (التي قد تحتوي على حرف في نهايتها للمراجع)
    tokens = re.findall(r'\d+[a-zA-Z]?', line_text)
    
    if not tokens:
        return 0, ""
        
    quantity_sum = 0
    user_input_ref = ""
    
    for token in tokens:
        # استخراج الأرقام فقط لمعرفة طول العدد
        digits_only = "".join([c for c in token if c.isdigit()])
        
        if len(digits_only) >= 4:
            # إذا كان 4 أرقام أو أكثر فهو المرجع الرئيسي للسطر
            user_input_ref = token
        else:
            # إذا كان أقل من 4 أرقام نقوم بجمعه مع كميات هذا السطر
            quantity_sum += int(digits_only)
            
    # إذا لم يتم العثور على أي مرجع بـ 4 أرقام، نعتبر آخر عنصر بالسطر هو المرجع
    if not user_input_ref and tokens:
        user_input_ref = tokens[-1]
        digits_only = "".join([c for c in user_input_ref if c.isdigit()])
        if len(digits_only) < 4 and quantity_sum >= int(digits_only):
            quantity_sum -= int(digits_only)
            
    # إذا لم تكن هناك أي كميات مكتوبة في السطر، نعتبر الكمية الافتراضية 1
    if quantity_sum == 0:
        quantity_sum = 1
        
    return quantity_sum, user_input_ref

# الشعار الخاص بك في أعلى صفحة الويب
st.markdown('<div class="brand-title">E01-TR11</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">~prog:E01~</div>', unsafe_allow_html=True)

st.markdown("### 📝 قم بلصق بيانات الكارتية والكميات هنا:")
input_text = st.text_area("", height=220, placeholder="أمثلة الإدخال المعتمدة الآن:\n21 147 5117\n147 4733\n5117")

if st.button("🚀 معالجة البيانات وحساب الحصيلة"):
    db = load_database()
    if db is None:
        st.error("❌ ملف 'Gamme_Database.txt' غير موجود بجانب الكود.")
    elif not input_text.strip():
        st.warning("⚠️ الرجاء إدخال البيانات أولاً.")
    else:
        lines = input_text.strip().split("\n")
        detailed_data = []
        stats = {}
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # معالجة كل سطر على حدة بشكل منفصل تماماً
            quantity, user_input_ref = process_single_line(line_clean)
            
            search_digits = clean_ref_for_matching(user_input_ref)
            
            if not search_digits:
                detailed_data.append({"الرقم المختصر": line_clean, "المرجع الكامل": "❌ خطأ في الإدخال", "الكمية": 0, "النوع (Version)": "غير معروف"})
                continue

            matched_version = None
            matched_full_ref = None
            
            for db_ref, db_version in db.items():
                db_ref_digits = clean_ref_for_matching(db_ref)
                if db_ref_digits.endswith(search_digits) or search_digits.endswith(db_ref_digits):
                    matched_version = db_version
                    matched_full_ref = db_ref
                    break
            
            if matched_version:
                detailed_data.append({"الرقم المختصر": search_digits, "المرجع الكامل": matched_full_ref, "الكمية": quantity, "النوع (Version)": matched_version})
                stats[matched_version] = stats.get(matched_version, 0) + quantity
            else:
                detailed_data.append({"الرقم المختصر": search_digits, "المرجع الكامل": "❌ غير مسجل", "الكمية": quantity, "النوع (Version)": "مجهول"})

        # ترتيب المراجع تصاعدياً من الأصغر للأكبر لسهولة مراجعتها
        try:
            detailed_data.sort(key=lambda x: int(x["الرقم المختصر"]) if x["الرقم المختصر"].isdigit() else 999999)
        except Exception:
            pass

        st.markdown("---")
        st.markdown("### 📋 التقرير التفصيلي للمراجع (مرتبة تصاعدياً)")
        st.table(detailed_data)

        st.markdown("### 📊 إجمالي الحصيلة التراكمية (أرقام فقط)")
        
        summary_data = []
        if stats:
            for version, total_qty in sorted(stats.items()):
                summary_data.append({"النوع (Version)": version, "المجموع": total_qty})
        else:
            summary_data.append({"النوع (Version)": "لا توجد بيانات", "المجموع": 0})
            
        st.table(summary_data)