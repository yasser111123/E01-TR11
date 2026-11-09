import streamlit as st
import os
import re

# إعدادات الصفحة لتكون متوافقة مع الهواتف والآيفون شاشات اللمس
st.set_page_config(page_title="E01-TR11 PROG", page_icon="🚀", layout="centered")

# تطبيق ثيم أسود احترافي ومتناسق (Pitch Black Theme)
st.markdown("""
    <style>
    /* خلفية الصفحة والنصوص الرئيسية */
    .main { background-color: #0b0f19; color: #e2e8f0; }
    
    /* مربع إدخال النصوص */
    .stTextArea textarea { 
        background-color: #111827 !important; 
        color: #f3f4f6 !important; 
        border: 1px solid #1f2937 !important;
        font-family: 'Consolas', monospace !important; 
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.4) !important;
    }

    /* أزرار التشغيل */
    div.stButton > button:first-child { 
        background-color: #2563eb !important; 
        color: #ffffff !important; 
        font-weight: bold !important; 
        width: 100%; 
        border: none !important; 
        padding: 12px !important; 
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 0 12px rgba(37, 99, 235, 0.5) !important;
    }

    /* العناوين والشعار */
    .brand-title { 
        color: #ffffff; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 28px; 
        font-weight: 900; 
        text-align: center; 
        letter-spacing: 2px;
        margin-bottom: 0px; 
    }
    .brand-sub { 
        color: #94a3b8; 
        font-family: 'Consolas', monospace; 
        font-size: 13px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 25px; 
    }

    /* تنسيق الجداول */
    th { 
        background-color: #1e293b !important; 
        color: #38bdf8 !important; 
        text-align: center !important; 
        border-bottom: 2px solid #334155 !important;
    }
    td { 
        background-color: #0f172a !important;
        color: #cbd5e1 !important;
        text-align: center !important; 
        border-bottom: 1px solid #1e293b !important;
    }
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
    tokens = re.findall(r'\d+[a-zA-Z]?', line_text)
    
    if not tokens:
        return 0, ""
        
    quantity_sum = 0
    user_input_ref = ""
    
    for token in tokens:
        digits_only = "".join([c for c in token if c.isdigit()])
        
        if len(digits_only) >= 4:
            user_input_ref = token
        else:
            quantity_sum += int(digits_only)
            
    if not user_input_ref and tokens:
        user_input_ref = tokens[-1]
        digits_only = "".join([c for c in user_input_ref if c.isdigit()])
        if len(digits_only) < 4 and quantity_sum >= int(digits_only):
            quantity_sum -= int(digits_only)
            
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
