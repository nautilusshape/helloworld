import streamlit as st
import json
import re
from google import genai
from google.genai import types
#import os
from bs4 import BeautifulSoup


#proxy = "http://localhost:24765"
#os.environ["HTTP_PROXY"] = proxy
#os.environ["HTTPS_PROXY"] = proxy


# --- Configuration ---
st.set_page_config(page_title="Fact-Checking Assistant", layout="wide")

# --- Gemini API Setup ---
systeminstruction = """
نقش: شما یک سیستم هوشمند و کامل برای تحلیل و صحت‌سنجی اخبار هستید. وظیفه شما اجرای یک فرآیند چهارمرحله‌ای بر روی متن ورودی است:
1.	استخراج ادعاهای قابل بررسی.
2.	تجزیه هر ادعا به سوالات بنیادین.
3.	تحقیق و گردآوری شواهد برای هر سوال.
4.	ارزیابی، جمع‌بندی و صدور رأی نهایی برای هر ادعا.
هدف: ارائه یک گزارش تحلیلی کامل در قالب یک آبجکت JSON که تمام مراحل صحت‌سنجی را برای هر ادعای موجود در متن ورودی مستند می‌کند.
دستورالعمل‌ها:
________________________________________
مرحله اول: شناسایی و استخراج ادعاها
•	متن خبر ورودی را به دقت مطالعه کن.
•	لیستی از تمام جملاتی که حاوی «ادعای قابل بررسی» هستند (شامل آمار، وعده، مقایسه، یا روابط علت و معلولی) را شناسایی کن.
•	از استخراج نظرات شخصی، جملات کلی یا سوالات خودداری کن.
________________________________________
مرحله دوم: تجزیه هر ادعا به سوالات اتمی
•	برای هر ادعایی که در مرحله اول استخراج کردی، آن را به اجزای منطقی و بنیادین خود تجزیه کن.
•	برای هر جزء، یک «سوال اتمی» دقیق و قابل جستجو طراحی کن که پاسخ به آن به درک درستیِ ادعای اصلی کمک کند.
________________________________________
مرحله سوم: تحقیق و گردآوری شواهد برای هر سوال اتمی
•	برای هر سوال اتمی که در مرحله دوم ساختی، یک فرآیند تحقیق کامل را اجرا کن:
o	طراحی عبارت‌های جستجو (Search Queries): چند عبارت کلیدی برای یافتن منابع موافق، مخالف و خنثی طراحی کن.
o	جمع‌آوری شواهد: با استفاده از عبارت‌های جستجو، حداقل ۳ و حداکثر ۵ شاهد معتبر از منابع دست اول (خبرگزاری‌ها، گزارش‌های رسمی، تحقیقات علمی) پیدا کن.
o	استخراج اطلاعات کلیدی: برای هر شاهد، اطلاعات زیر را استخراج کن:
..	date : تاریخ خبر به شمسی که در منبع ذکر شده است.
..	source_title : عنوان دقیق منبع.
..	quote : نقل قول مستقیم و مرتبط‌ترین بخش از متن منبع.
..	stance : موضع شاهد نسبت به «سوال اتمی» (نه ادعای اصلی). از برچسب‌های «موافق»، «مخالف» یا «خنثی/زمینه‌ای» استفاده کن.
..	interpretation : برداشت تحلیلی خودت از شاهد در یک یا دو جمله.
________________________________________
مرحله چهارم: ارزیابی و نتیجه‌گیری نهایی (مرحله جدید)
•	پس از جمع‌آوری شواهد برای تمام سوالات اتمیِ مرتبط با یک ادعا، یک تحلیل جامع برای ادعای اصلی ارائه بده. این تحلیل باید شامل موارد زیر باشد:
o	 summary_of_findings  : خلاصه‌ای چند جمله‌ای از مهم‌ترین شواهد موافق، مخالف و زمینه‌ای که به دست آوردی. این بخش باید تصویری کلی از چشم‌انداز اطلاعاتی پیرامون ادعا ارائه دهد.
o	verdict  : با توجه به مجموع شواهد، یکی از برچسب‌های زیر را برای «ادعای اصلی» انتخاب کن:
..	درست: تمام شواهد معتبر، ادعا را تایید می‌کنند.
..	نیمه درست: هسته اصلی ادعا درست است، اما جزئیات مهمی نادیده گرفته شده یا دقت کافی را ندارد.
..	گمراه‌کننده: ادعا ممکن است حاوی عناصری از حقیقت باشد، اما با حذف زمینه یا ارائه گزینشی اطلاعات، تصویر نادرستی را القا می‌کند.
..	نادرست: شواهد معتبر، ادعا را به وضوح رد می‌کنند.
..	غیر قابل بررسی: شواهد کافی و معتبری برای قضاوت در مورد درستی یا نادرستی ادعا در دسترس نیست.
o	reasoning  :به تفصیل توضیح بده که چرا این رأی را صادر کردی. به شواهد متناقض، نکات کلیدی، کیفیت منابع و زمینه‌های پنهان اشاره کن. این بخش باید به وضوح نشان دهد که چگونه شواهد جمع‌آوری‌شده در مرحله سوم به این نتیجه‌گیری منجر شده است.
________________________________________
نکات کلیدی
•	اگر در ادعا به تاریخ اشاره نشده، تاریخ روز را پیش‌فرض در نظر بگیر.
•	از گذاشتن citation مانند [2] در متن خروجی خودداری کن.
•	خروجی نهایی باید یک آبجکت JSON معتبر باشد.



-------

    "response_schema": {
        "type": "object",
        "properties": {
            "claims_and_evidences": {
                "type": "array",
                "description": "",
                "nullable": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "claims": {
                            "type": "array",
                            "description": "",
                            "nullable": True,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "claims_context": {
                                        "type": "string",
                                        "description": "",
                                        "nullable": True
                                    },
                                    "atomic_questions": {
                                        "type": "array",
                                        "description": "",
                                        "nullable": True,
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "question": {
                                                    "type": "string",
                                                    "description": "",
                                                    "nullable": True
                                                },
                                                "evidences": {
                                                    "type": "array",
                                                    "description": "",
                                                    "nullable": True,
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "date": {
                                                                "type": "string",
                                                                "description": "",
                                                                "nullable": True
                                                            },
                                                            "source_title": {
                                                                "type": "string",
                                                                "description": "",
                                                                "nullable": True
                                                            },
                                                            "Quote": {
                                                                "type": "string",
                                                                "description": "",
                                                                "nullable": True
                                                            },
                                                            "stance": {
                                                                "type": "string",
                                                                "description": "",
                                                                "nullable": True
                                                            },
                                                            "interpretation": {
                                                                "type": "string",
                                                                "description": "",
                                                                "nullable": True
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "total_fact_checking": {
                "type": "array",
                "description": "",
                "nullable": True,
                "items": {
                    "type": "object",
                    "properties": {
                        
                        "summary_of_findings": {
                            "type": "string",
                            "description": "",
                            "nullable": True
                        },
                        "verdict": {
                            "type": "string",
                            "enum": [
                                "درست",
                                "نیمه درست",
                                "گمراه کننده",
                                "نادرست",
                                "غیر قابل بررسی",
                            ]
                            "description": "",
                            "nullable": True
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "",
                            "nullable": True
                        }
                    }
                }
            }
        },
        "required": [
            "claims_and_evidences",
            "total_fact_checking"
            
        ]
    }
            
"""
apikey = "AIzaSyA0rz6G2sO3aqTiRpxt0VBcj5q6RHg3J3s"
client = genai.Client(api_key=apikey)
def callgemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
        "tools": [types.Tool(google_search=types.GoogleSearch())],
        "system_instruction": [types.Part.from_text(text=systeminstruction)],
        "temperature": 0.3,
        "thinking_config": types.ThinkingConfig(
            thinking_budget=0  # Disables thinking. Set a value in milliseconds to enable.
            )
    }
    )
    return response

def callgeminipro(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config={
        "tools": [types.Tool(google_search=types.GoogleSearch())],
        "system_instruction": [types.Part.from_text(text=systeminstruction)],
        "temperature": 0.3 ,
    }
    )
    return response




# --- Utility Functions ---
def is_primitive(val):
    return isinstance(val, (str, int, float, bool)) or val is None

def build_table_from_dict(d):
    headers = list(d.keys())
    rows = []
    cells = []
    for k in headers:
        v = d[k]
        if is_primitive(v):
            cells.append(str(v))
        elif isinstance(v, dict):
            cells.append(build_table_from_dict(v))
        elif isinstance(v, list):
            cells.append(build_table_from_list(v))
        else:
            cells.append(str(v))
    rows.append(cells)
    return make_table(headers, rows)

def build_table_from_list(lst):
    if not lst:
        return "<table><tr><td></td></tr></table>"
    if all(is_primitive(item) for item in lst):
        rows = [[str(item)] for item in lst]
        return make_table(["value"], rows)

    headers = []
    seen = set()
    for item in lst:
        if isinstance(item, dict):
            for key in item.keys():
                if key not in seen:
                    headers.append(key)
                    seen.add(key)

    rows = []
    for item in lst:
        row = []
        for h in headers:
            val = item.get(h, "")
            if is_primitive(val):
                row.append(str(val))
            elif isinstance(val, dict):
                row.append(build_table_from_dict(val))
            elif isinstance(val, list):
                row.append(build_table_from_list(val))
            else:
                row.append(str(val))
        rows.append(row)
    return make_table(headers, rows)

def make_table(headers, rows):
    table = '<table border="1" style="border-collapse:collapse; width:100%;">'
    if headers:
        table += "<thead><tr>"
        for h in headers:
            table += f'<th style="border:1px solid #000; background-color:#f0f0f0; font-weight:bold;">{h}</th>'
        table += "</tr></thead>"
    table += "<tbody>"
    for row in rows:
        table += "<tr>"
        for cell in row:
            table += f'<td style="border:1px solid #000;">{cell}</td>'
        table += "</tr>"
    table += "</tbody></table>"
    return table

# --- Persistent state ---
if "results" not in st.session_state:
    st.session_state.results = None
if "status" not in st.session_state:
    st.session_state.status = None
if "response_obj" not in st.session_state:
    st.session_state.response_obj = None
if "pending" not in st.session_state:
    st.session_state.pending = False   # flag for rerun
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# --- Streamlit UI ---
st.markdown(
    """
    <h1 style='direction:rtl; text-align:right;'>🌐 دستیار راستی‌آزمایی </h1>
    """,
    unsafe_allow_html=True
)

#  CSS
st.markdown(
    """
    <style>
    div.stRadio {
        direction: rtl;
        text-align: right;
    }
    div.stRadio label {
        display: flex !important;
        flex-direction: row-reverse !important;
        align-items: center;
        justify-content: flex-end;
        font-family: Vazirmatn, Tahoma, Arial, sans-serif;
        font-size: 16px;
        gap: 6px;
    }
    div.stRadio input[type="radio"] {
        margin: 0 !important;
    }
    textarea {
        direction: rtl;
        text-align: right;
        font-family: Vazirmatn, Tahoma, Arial, sans-serif;
    }
    div.stButton {
        text-align: right;  
        margin-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    prompt = st.text_area(
        "📝 متن خبر یا اظهار برای راستی‌آزمایی را وارد کنید:",
        height=200,
        label_visibility="collapsed",  
        key="input_text"
    )
    
    model_choice = st.radio(
        "💡 مدل را انتخاب کنید:",
        options=["Gemini-2.5pro", "Gemini-2.5flash"],
        index=0,
        horizontal=True
    )
    
    submit = st.button("✅ ارسال")

# ----------------- پردازش -----------------
# --- Status placeholder ---
if "status_placeholder" not in st.session_state:
    st.session_state.status_placeholder = st.empty()

# --- Handle submit ---
if submit:
    if not prompt.strip():
        st.session_state.status = """
        <div style='direction:rtl; text-align:right; background-color:#fff3cd;
                    color:#856404; border:1px solid #ffeeba; padding:10px; border-radius:8px; margin-top:5px;'>
            ⚠️ لطفاً یک متن معتبر وارد کنید.
        </div>
        """
        st.session_state.results = None
        st.session_state.response_obj = None
        st.session_state.pending = False
        st.session_state.status_placeholder.markdown(st.session_state.status, unsafe_allow_html=True)

    else:
        # --- Step 1: show loading ---
        st.session_state.status = """
        <div style='direction:rtl; text-align:right; background-color:#e6f7ff;
                    color:#0050b3; border:1px solid #91d5ff; padding:10px; border-radius:8px; margin-top:5px;'>
            ⏳ در حال تحلیل و راستی‌آزمایی...
        </div>
        """
        st.session_state.results = None
        st.session_state.response_obj = None
        st.session_state.pending = True
        st.session_state.status_placeholder.markdown(st.session_state.status, unsafe_allow_html=True)

# --- Step 2: run API if pending ---
if st.session_state.get("pending", False):
    import time
    time.sleep(0.1)  # short pause to let Streamlit render ⏳

    try:
        if model_choice == "Gemini-2.5flash":
            response = callgemini(prompt)
        else:
            response = callgeminipro(prompt)

        text = response.text
        st.session_state.results = text
        st.session_state.response_obj = response
        st.session_state.status = """
        <div style='direction:rtl; text-align:right; background-color:#daf3cc;
                    color:#389e0d; border:1px solid #73d13d; padding:10px; border-radius:8px; margin-top:5px;'>
             ✅ فرایند راستی‌آزمایی با موفقیت انجام شد
        </div>
        """
    except Exception as e:
        st.session_state.status = f"""
        <div style='direction:rtl; text-align:right; background-color:#f8d7da;
                    color:#842029; border:1px solid #f5c2c7; padding:10px; border-radius:8px; margin-top:5px;'>
            ❌ خطایی رخ داد: {e}
        </div>
        """
        st.session_state.results = None
        st.session_state.response_obj = None

    st.session_state.pending = False
    # overwrite the status placeholder
    st.session_state.status_placeholder.markdown(st.session_state.status, unsafe_allow_html=True)

# --- Always show latest state ---
if st.session_state.status:
    st.markdown(st.session_state.status, unsafe_allow_html=True)

if st.session_state.results:
    text = st.session_state.results
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            data = json.loads(json_str)

            html = """
            <style>
            table { 
                font-family: Vazirmatn, Arial, sans-serif; 
                font-size: 16px; 
                direction: rtl; 
                text-align: right;
            }
            th, td {
                border:1px solid #000;
                padding:6px;
            }
            th {
                background-color:#f0f0f0;
                font-weight:bold;
            }
            </style>
            """
            html += build_table_from_dict(data)

            # --- Verdict, summary, reasoning ---
            if (
                "total_fact_checking" in data 
                and isinstance(data["total_fact_checking"], list) 
                and len(data["total_fact_checking"]) > 0
            ):
                fact_check = data["total_fact_checking"][0]
                summary_of_findings = fact_check.get("summary_of_findings", "")
                verdict = fact_check.get("verdict", "")
                reasoning = fact_check.get("reasoning", "")

                if verdict:
                    st.markdown(
                        f"""
                            <div style='background-color:#e6f7ff; border:1px solid #91d5ff; 
                                        padding:12px; border-radius:8px; margin-bottom:5px;
                                        margin-top:15px;
                                        direction:rtl; text-align:right; font-size:18px;' >
                                <b>🏷️ برچسب نهایی:</b><br>
                                <span style="font-size:16px; font-weight:bold;">{verdict}</span>
                            </div>
                        """,
                        unsafe_allow_html=True
                    )

                if summary_of_findings:
                    st.markdown(
                        f"""
                            <div style='background-color:#e6f7ff; border:1px solid #91d5ff; 
                                        padding:12px; border-radius:8px; margin-bottom:5px; 
                                        direction:rtl; text-align:right; font-size:18px;' >
                                <b>📊 نتیجه کلی راستی‌آزمایی:</b><br>
                                <span style="font-size:18px;">{summary_of_findings}</span>
                            </div>
                        """,
                        unsafe_allow_html=True
                    )

                if reasoning:
                    st.markdown(
                        f"""
                            <div style='background-color:#e6f7ff; border:1px solid #91d5ff; 
                                        padding:12px; border-radius:8px; margin-bottom:5px; 
                                        direction:rtl; text-align:right; font-size:18px;' >
                                <b>📚 استدلال:</b><br>
                                <span style="font-size:18px;">{reasoning}</span>
                            </div>
                        """,
                        unsafe_allow_html=True
                    )

                # --- Extract references ---
                try:
                    if st.session_state.response_obj:
                        extract_ref = st.session_state.response_obj.candidates[0].grounding_metadata.search_entry_point.rendered_content
                        soup = BeautifulSoup(extract_ref, "html.parser")
                        chips = soup.select("div.carousel a.chip")
                        if chips:
                            chips_html = "<br>".join([f'• <a href="{chip.get("href")}" target="_blank">{chip.get_text(strip=True)}</a>' for chip in chips])
                            st.markdown(
                                f"""
                                <div style='background-color:#e6f7ff; border:1px solid #91d5ff; 
                                            padding:12px; border-radius:8px; margin-bottom:15px; 
                                            direction:rtl; text-align:right; font-size:18px;' >
                                    <b>🔎 پیشنهادات جستجو در گوگل :</b><br>
                                    <span style="font-size:18px;">{chips_html}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                except Exception:
                    pass

            # --- Full table ---
            st.components.v1.html(html, height=4000, scrolling=True)

        except json.JSONDecodeError as e:
            st.markdown(
                f"""
                <div style='direction:rtl; text-align:right; background-color:#f8d7da;
                            color:#842029; border:1px solid #f5c2c7; padding:10px; border-radius:8px; margin-top:5px;'>
                    ❌ خطا در پردازش JSON: {e}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            """
            <div style='direction:rtl; text-align:right; background-color:#f8d7da;
                        color:#842029; border:1px solid #f5c2c7; padding:10px; border-radius:8px; margin-top:5px;'>
                ❌ JSON معتبر در پاسخ یافت نشد.
            </div>
            """,
            unsafe_allow_html=True
        )