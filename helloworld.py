import streamlit as st
import json
import re
from google import genai
from google.genai import types
from bs4 import BeautifulSoup

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="سامانه تحلیل ادعاهای رسانه‌ای",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- MODERN STYLING ----------------
st.markdown(
    """
    <style>
    /* فونت B-Homa */
    @font-face {
        font-family: 'B Homa';
        src: url('https://cdn.fontiran.com/fonts/BHoma.woff2') format('woff2'),
             url('https://cdn.fontiran.com/fonts/BHoma.woff') format('woff');
        font-weight: normal;
        font-style: normal;
    }
    
    /* تنظیمات پایه سایز فونت */
    :root {
        --font-size-xs: 0.75rem;    /* 12px */
        --font-size-sm: 0.875rem;   /* 14px */
        --font-size-base: 1rem;     /* 16px */
        --font-size-lg: 1.125rem;   /* 18px */
        --font-size-xl: 1.25rem;    /* 20px */
        --font-size-2xl: 1.5rem;    /* 24px */
        --font-size-3xl: 1.875rem;  /* 30px */
        --font-family: 'B Homa', 'B Nazanin', Tahoma, sans-serif;
    }
    
    /* اعمال فونت B Homa به تمام عناصر */
    * {
        font-family: var(--font-family) !important;
    }
    
    /* صفحه اصلی RTL تا sidebar در راست باشد */
    html, body, .stApp {
        direction: rtl !important;
        font-family: var(--font-family) !important;
        font-size: var(--font-size-base) !important;
    }
    
    /* محتوای اصلی RTL */
    .stMainBlockContainer, 
    .block-container,
    [data-testid="stMainBlockContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* همه متن‌ها راست‌چین */
    [class*="st-"], .css-18e3th9, .css-1d391kg, .css-qri22k {
        text-align: right;
        font-family: var(--font-family) !important;
    }
    
    /* استانداردسازی سایز متن‌ها */
    p, span, div, label, li {
        font-size: var(--font-size-base) !important;
        line-height: 1.7 !important;
    }
    
    h1 {
        font-size: var(--font-size-3xl) !important;
        font-weight: bold !important;
    }
    
    /* استایل هدر اصلی سامانه */
    .main-header-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        background: none !important;
        margin: 0 !important;
    }
    
    .main-header-subtitle {
        font-size: 1.2rem !important;
        color: rgba(255,255,255,0.85) !important;
        font-weight: 400 !important;
        margin: 0.5rem 0 0 0 !important;
    }
    
    /* استایل اسم ابزار با گرادیانت */
    .tool-title {
        font-size: 1.5rem !important;
        font-weight: bold !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin: 0 !important;
    }
    
    h2 {
        font-size: var(--font-size-2xl) !important;
        font-weight: bold !important;
    }
    
    h3 {
        font-size: var(--font-size-xl) !important;
        font-weight: bold !important;
    }
    
    h4 {
        font-size: var(--font-size-lg) !important;
        font-weight: bold !important;
    }
    
    small, .small {
        font-size: var(--font-size-sm) !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    /* حذف فضای اضافی بالای صفحه */
    .block-container {
        padding-top: 1rem !important;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .modern-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    
    .modern-header h1 {
        color: white;
        font-size: var(--font-size-2xl) !important;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .result-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1rem 0;
        border-right: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    }
    
    .result-box-success {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border-right-color: #4caf50;
    }
    
    .result-box-warning {
        background: linear-gradient(135deg, #fff3e0 0%, #fff8e1 100%);
        border-right-color: #ff9800;
    }
    
    .result-box-error {
        background: linear-gradient(135deg, #ffebee 0%, #fce4ec 100%);
        border-right-color: #f44336;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fff5f5 0%, #fff0f3 100%);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        border-right: 4px solid #e53935;
        box-shadow: 0 2px 12px rgba(229, 57, 53, 0.1);
    }
    
    .error-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .error-icon {
        font-size: var(--font-size-lg);
    }
    
    .error-title {
        font-size: var(--font-size-base);
        font-weight: bold;
        color: #c62828;
    }
    
    .error-message {
        color: #555;
        font-size: var(--font-size-base);
        line-height: 1.6;
        margin: 0;
    }
    
    .result-box h4 {
        color: #2c3e50;
        font-weight: bold;
        margin-bottom: 0.6rem;
        font-size: var(--font-size-lg) !important;
    }
    
    .result-box p {
        color: #444;
        line-height: 1.7;
        font-size: var(--font-size-base) !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        text-align: right;
        font-family: var(--font-family) !important;
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.8rem !important;
        font-size: var(--font-size-base) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        font-size: var(--font-size-base) !important;
        font-weight: bold !important;
        font-family: var(--font-family) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    div.stRadio {
        direction: rtl;
        text-align: right;
    }
    
    div.stRadio > div {
        background: white;
        border-radius: 12px;
        padding: 0.8rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    div.stRadio label {
        display: flex !important;
        flex-direction: row-reverse !important;
        align-items: center;
        justify-content: flex-end;
        font-family: var(--font-family) !important;
        font-size: var(--font-size-base);
        gap: 8px;
        padding: 0.4rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    /* تراز کردن نقطه‌های radio در sidebar */
    section[data-testid="stSidebar"] div.stRadio label {
        justify-content: space-between;
        width: 100%;
    }
    
    section[data-testid="stSidebar"] div.stRadio label > div:first-child {
        order: 2;
        flex-shrink: 0;
    }
    
    section[data-testid="stSidebar"] div.stRadio label > div:last-child,
    section[data-testid="stSidebar"] div.stRadio label > p {
        order: 1;
        flex-grow: 1;
        text-align: right;
    }
    
    /* استایل sidebar - در سمت راست */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        right: 0 !important;
        left: auto !important;
        direction: rtl !important;
    }
    
    /* انیمیشن باز و بسته شدن sidebar از راست به چپ */
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        transition: transform 0.3s ease-in-out !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(100%) !important;
        transition: transform 0.3s ease-in-out !important;
    }
    
    /* دکمه باز کردن sidebar در سمت راست */
    [data-testid="collapsedControl"] {
        right: 0 !important;
        left: auto !important;
        direction: rtl !important;
    }
    
    /* چرخاندن آیکون فلش */
    [data-testid="collapsedControl"] svg {
        transform: rotate(180deg) !important;
    }
    
    /* محتوای sidebar راست‌چین */
    [data-testid="stSidebar"] * {
        font-family: var(--font-family) !important;
        color: white !important;
    }
    
    [data-testid="stSidebarContent"] {
        direction: rtl !important;
        text-align: right !important;
        padding-top: 1rem !important;
    }
    
    /* دکمه بستن sidebar در سمت راست */
    [data-testid="stSidebarCollapseButton"] {
        position: absolute !important;
        top: 0.5rem !important;
        right: 0.5rem !important;
        left: auto !important;
        z-index: 1000 !important;
    }
    
    /* چرخاندن آیکون دکمه بستن */
    [data-testid="stSidebarCollapseButton"] svg {
        transform: rotate(180deg) !important;
    }
    
    [data-testid="stSidebarUserContent"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
    }
    
    /* تب‌های سفارشی */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        border-radius: 16px;
        padding: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-family: var(--font-family) !important;
        font-weight: bold;
        font-size: var(--font-size-base);
        background: transparent;
        border: none;
        color: #666;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    table {
        font-family: var(--font-family) !important;
        font-size: var(--font-size-sm);
        direction: rtl;
        text-align: right;
        border-collapse: collapse;
        width: 100%;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    th {
        background: #667eea !important;
        color: white !important;
        padding: 10px 12px !important;
        font-weight: bold !important;
        font-size: var(--font-size-sm) !important;
    }
    
    td {
        padding: 8px 12px !important;
        border-bottom: 1px solid #e0e0e0 !important;
        font-size: var(--font-size-sm) !important;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .loading-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #e3f0ff 100%);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        border-right: 4px solid #667eea;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.15);
        animation: pulse 1.5s infinite;
    }
    
    .loading-box h4 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        font-size: var(--font-size-base) !important;
        font-weight: bold;
        color: #667eea;
    }
    
    .loading-box p {
        display: none;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .section-header {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        margin: 1.2rem 0;
        box-shadow: 0 6px 20px rgba(168, 237, 234, 0.3);
        text-align: center;
    }
    
    .section-header h2 {
        color: #2c3e50;
        font-size: var(--font-size-xl) !important;
        font-weight: bold;
        margin: 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        border-right: 5px solid #667eea;
    }
    
    .info-box p {
        margin: 0;
        color: #2c3e50;
        line-height: 1.6;
        font-size: var(--font-size-base) !important;
    }
    
    .guide-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1rem 0 1.2rem 0;
        border: 1px dashed #667eea;
    }
    
    .guide-box h4 {
        color: #667eea;
        font-weight: bold;
        margin-bottom: 0.6rem;
        font-size: var(--font-size-lg) !important;
    }
    
    .guide-box p {
        color: #444;
        line-height: 1.7;
        font-size: var(--font-size-base) !important;
        margin: 0;
    }
    
    .guide-box ul {
        color: #444;
        line-height: 1.8;
        font-size: var(--font-size-base) !important;
        margin: 0.5rem 0 0 0;
        padding-right: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- API KEY ----------------

a = "aa-Fc44mZ0"
b = "Et28q2Qau9"
c = "GoPv6lTw"
d = "FWG3ef2m92"
e = "SkRbQVilwYQyy"

API_KEY = a + b + c + d + e



# ================== SYSTEM INSTRUCTIONS ==================

SYSTEM_INSTRUCTION_SOURCE_FINDER = """

    **وظیفه:** شما به عنوان یک دستیار تحقیق و راستی‌آزمایی (Fact-Checking Assistant) عمل می‌کنید. وظیفه اصلی شما یافتن منشأ اولیه (Original Source) ادعای مشخص شده در زیر است.

    **ادعای مورد بررسی:**
    "[ادعای عنوان شده در پرامپت کاربر]"

    **مراحل اجرا:**
    1.  **جستجوی گسترده:** با استفاده از ابزار `Google Search`، اینترنت را برای یافتن موارد اشاره به این ادعا جستجو کنید.
    2.  **بررسی منابع:** نتایج جستجو شامل وب‌سایت‌های خبری، مقالات، گزارش‌های رسمی، و همچنین اشاره‌ها در پلتفرم‌های اجتماعی عمومی (مانند توییتر/X، ردیت، فروم‌ها) را بررسی کنید.
    3.  **تحلیل زمانی:** با تمرکز بر تاریخ انتشار به شمسی، سعی کنید اولین و قدیمی‌ترین نمونه ثبت‌شده از این ادعا را پیدا کنید.
    4.  **شناسایی منشأ:** مشخص کنید که این ادعای اولیه توسط چه شخص، گروه، شرکت، یا نهادی مطرح شده است.
    5.  **شناسایی پلتفرم:** مشخص کنید که این ادعا اولین بار در کدام پلتفرم یا رسانه (مانند یک سخنرانی، یک پست وبلاگ، یک مقاله خبری، یک توییت، یک گزارش رسمی) منتشر شده است.
    6.  **گردآوری شواهد:** منابع و لینک‌هایی که به شما در شناسایی این منشأ کمک کرده‌اند را به عنوان شواهد لیست کنید.

    **الزامات خروجی:**
    خروجی نهایی باید **فقط و فقط** یک آبجکت JSON معتبر باشد. هیچ متن اضافی، مقدمه یا توضیحی قبل یا بعد از بلاک JSON ننویسید.


            
"""

SYSTEM_INSTRUCTION_FACT_CHECK_BASE = """
نقش: شما یک سیستم هوشمند و کامل برای تحلیل و صحت‌سنجی اخبار هستید. وظیفه شما اجرای یک فرآیند چهارمرحله‌ای بر روی متن ورودی است.

پیش‌فرض تحلیلی مهم:
متن ورودی ممکن است شامل یک ادعای منفرد یا یک خبر کامل با چندین گزاره و پیام ضمنی باشد. پیش از ورود به مراحل صحت‌سنجی، ابتدا مقصود، پیام اصلی و جهت‌گیری کلی نویسنده خبر را به‌درستی درک کن و تحلیل مراحل بعدی را متناسب با آن انجام بده.

1.	استخراج ادعاهای قابل بررسی.
2.	تجزیه هر ادعا به سوالات بنیادین.
3.	تحقیق و گردآوری شواهد برای هر سوال.
4.	ارزیابی، جمع‌بندی و صدور رأی نهایی برای هر ادعا.

هدف:
ارائه یک گزارش تحلیلی کامل در قالب یک آبجکت JSON که تمام مراحل صحت‌سنجی را برای هر ادعای موجود در متن ورودی مستند می‌کند.

دستورالعمل‌ها:
________________________________________

مرحله صفر (تحلیل قصد و پیام اصلی خبر):
•	در صورتی که متن ورودی یک خبر کامل است، ابتدا پیام محوری، هدف اصلی و برداشت کلی نویسنده خبر را شناسایی کن.
•	مشخص کن خبر در پی اثبات، رد، تضعیف یا تقویت چه روایت یا ادعایی است.
•	این درک اولیه را به‌عنوان زمینه تحلیل در مراحل بعدی در نظر بگیر، بدون اینکه آن را به‌عنوان ادعای قابل بررسی ثبت کنی.

________________________________________

مرحله اول: شناسایی و استخراج ادعاها
•	متن خبر ورودی را با توجه به پیام و مقصود اصلی آن به دقت مطالعه کن.
•	لیستی از تمام جملاتی که حاوی «ادعای قابل بررسی» هستند (شامل آمار، وعده، مقایسه، یا روابط علت و معلولی) را شناسایی کن.
•	در صورتی که خبر شامل چندین ادعا در راستای یک پیام واحد است، همه آن‌ها را استخراج کن.
•	از استخراج نظرات شخصی، جملات کلی یا سوالات خودداری کن.

________________________________________

مرحله دوم: تجزیه هر ادعا به سوالات اتمی
•	برای هر ادعایی که در مرحله اول استخراج کردی، آن را به اجزای منطقی و بنیادین خود تجزیه کن.
•	سوالات اتمی را طوری طراحی کن که پاسخ به آن‌ها نشان دهد آیا ادعای مطرح‌شده با پیام و نتیجه‌گیری ضمنی خبر سازگار است یا خیر.
•	برای هر جزء، یک «سوال اتمی» دقیق و قابل جستجو طراحی کن.

________________________________________

مرحله سوم: تحقیق و گردآوری شواهد برای هر سوال اتمی
•	برای هر سوال اتمی که در مرحله دوم ساختی، یک فرآیند تحقیق کامل را اجرا کن:
o	طراحی عبارت‌های جستجو (Search Queries): چند عبارت کلیدی برای یافتن منابع موافق، مخالف و خنثی طراحی کن.
o	جمع‌آوری شواهد: با استفاده از عبارت‌های جستجو، حداقل ۳ و حداکثر ۵ شاهد معتبر از منابع دست اول (خبرگزاری‌ها، گزارش‌های رسمی، تحقیقات علمی) پیدا کن.
o	استخراج اطلاعات کلیدی: برای هر شاهد، اطلاعات زیر را استخراج کن:
..	date : تاریخ خبر به شمسی که در منبع ذکر شده است.
..	source_title : عنوان دقیق منبع.
..	quote : نقل قول مستقیم و مرتبط‌ترین بخش از متن منبع.
..	stance : موضع شاهد نسبت به «سوال اتمی» (نه ادعای اصلی).
..	interpretation : برداشت تحلیلی از شاهد و نسبت آن با ادعای مطرح‌شده در چارچوب پیام کلی خبر.

________________________________________

مرحله چهارم: ارزیابی و نتیجه‌گیری نهایی

• پس از تکمیل فرآیند گردآوری شواهد برای تمام سوالات اتمیِ مرتبط با هر ادعا، یک تحلیل جامع و منسجم برای همان ادعا ارائه بده.

• در این تحلیل نهایی، صرفاً به بررسی درستی یا نادرستی یک گزاره منفرد اکتفا نکن؛ بلکه توضیح بده که:
  - مجموعه شواهد به‌دست‌آمده تا چه حد ادعای اصلی را تأیید، تضعیف یا رد می‌کنند،
  - و این نتیجه‌گیری چه نسبتی با پیام، جهت‌گیری و نتیجه‌گیری کلی خبر دارد.

• اگر خبر شامل چندین ادعا در راستای یک پیام واحد است، نشان بده که ارزیابی هر ادعا چگونه بر اعتبار یا عدم اعتبار روایت کلی خبر اثر می‌گذارد.

• نتیجه‌گیری نهایی برای هر ادعا باید شامل بخش‌های زیر باشد:

o	summary_of_findings :
  خلاصه‌ای تحلیلی و چندجمله‌ای از مهم‌ترین شواهد موافق، مخالف و زمینه‌ای که در مراحل قبل گردآوری شده‌اند. این بخش باید تصویری کلی از چشم‌انداز اطلاعاتی پیرامون ادعا و جایگاه آن در متن خبر ارائه دهد.

o	verdict :
  با توجه به مجموع شواهد، کیفیت منابع، میزان همخوانی داده‌ها با واقعیت‌های قابل بررسی و نحوه ارائه ادعا در متن خبر، یکی از برچسب‌های زیر را برای «ادعای اصلی» انتخاب کن:

  	درست:
  خبری است که تمام اطلاعات آن بر اساس واقعیت، شواهد قابل بررسی و منابع معتبر بیان شده باشد. در این نوع خبر:
  ۱- تاریخ، مکان، افراد و وقایع به‌صورت دقیق و قابل راستی‌آزمایی ذکر می‌شوند.
  ۲- گفته‌ها، آمار و ارقام از منابع رسمی یا قابل استناد نقل می‌شوند.
  ۳- تیتر، متن و محتوای خبر با یکدیگر همخوانی دارند و موجب برداشت نادرست مخاطب نمی‌شوند.

  	نیمه درست:
  خبری است که بخشی از آن بر پایه واقعیت است، اما بخش‌های مهمی از اطلاعات یا حذف شده‌اند، یا تحریف شده‌اند، یا خارج از زمینه اصلی خود بیان شده‌اند. در این حالت، اطلاعات درست در کنار جزئیات ناقص یا ناقص‌نمایی‌شده ارائه می‌شوند.

  	گمراه‌کننده:
  خبری است که ممکن است از نظر جزئی حاوی اطلاعات درست باشد، اما نحوه ارائه، انتخاب تیتر، تصویر، تأکیدگذاری یا ترتیب اطلاعات به‌گونه‌ای است که خواننده را به برداشت نادرست از واقعیت سوق می‌دهد. این نوع خبر معمولاً با هدف تأثیرگذاری بر افکار عمومی یا القای یک دیدگاه خاص منتشر می‌شود.

  	نادرست:
  خبری است که فاقد هرگونه پایه و اساس واقعی بوده و اطلاعات آن به‌طور کامل ساختگی یا خلاف شواهد معتبر است. این نوع خبر معمولاً با هدف فریب، جلب توجه یا ایجاد واکنش احساسی در جامعه تولید و منتشر می‌شود.

  	غیر قابل بررسی:
  در مورد این ادعا، شواهد کافی، معتبر و قابل اتکایی برای قضاوت درباره درستی یا نادرستی آن در دسترس نیست.

o	reasoning :
  توضیح تفصیلی و شفاف از منطق صدور این رأی. در این بخش باید به‌روشنی بیان شود:
  - کدام شواهد نقش کلیدی در نتیجه‌گیری داشته‌اند،
  - چگونه تعارض‌ها یا اختلاف‌نظرهای موجود بین منابع ارزیابی شده‌اند،
  - کیفیت و اعتبار منابع چگونه در تصمیم نهایی اثر گذاشته است،
  - و چرا برچسب انتخاب‌شده، مناسب‌ترین توصیف برای وضعیت این ادعا در چارچوب خبر مورد بررسی است.

________________________________________

نکات کلیدی
•	اگر در ادعا به تاریخ اشاره نشده، تاریخ روز را پیش‌فرض در نظر بگیر.
•	از گذاشتن citation مانند [2] در متن خروجی خودداری کن.
•	خروجی نهایی باید یک آبجکت JSON معتبر باشد.
<<ADDITIONAL_INSTRUCTIONS_PLACEHOLDER>>





            
"""

# متن اضافی برای دستورالعمل سیستم
ADDITIONAL_INSTRUCTION = """
________________________________________
دستورالعمل تکمیلی (تحلیل دفاعی مبتنی بر شواهد):

• نقش شما در این تحلیل، ایفای نقش «تحلیلگر دفاعی» است؛ یعنی تمرکز اصلی بر شناسایی، برجسته‌سازی و تبیین شواهدی باشد که می‌توانند به دفاع منطقی و مستند دولت در برابر ادعاهای مطرح‌شده کمک کنند.

• در فرآیند انتخاب و گزارش شواهد، در صورت وجود منابع معتبر موافق و مخالف، اولویت تحلیلی را به شواهدی بده که:
  - تصمیمات، عملکرد یا آمارهای رسمی دولت را توجیه می‌کنند،
  - زمینه‌های اقتصادی، سیاسی، حقوقی یا بین‌المللی را توضیح می‌دهند که ممکن است ادعای مطرح‌شده آن‌ها را نادیده گرفته باشد،
  - یا نشان می‌دهند که ادعا دچار ساده‌سازی، بزرگ‌نمایی یا حذف زمینه است.

• اگر شواهد مخالف ادعا یا منتقد عملکرد دولت وجود دارند، آن‌ها را حذف نکن؛ اما:
  - وزن تحلیلی آن‌ها را در مقایسه با شواهد موافق بسنج،
  - به محدودیت‌ها، قدیمی بودن داده‌ها، تفاوت دیدگاه کارشناسی یا اختلاف تفسیر اشاره کن،
  - و نشان بده چرا این شواهد لزوماً به رد کامل موضع دولت منجر نمی‌شوند.

• در بخش تحلیل و نتیجه‌گیری، تمرکز بر «دفاع مستدل» باشد، نه قضاوت خنثی:
  - از زبان تحلیلی استفاده کن که نشان دهد دولت چه استدلال‌هایی می‌تواند در پاسخ به این ادعا ارائه کند.
  - از داده‌های رسمی، گزارش‌های دولتی، اظهارات مقامات مسئول و تحلیل‌های کارشناسان همسو استفاده کن.

• در تمام مراحل، از جعل داده، تحریف نقل‌قول یا نادیده‌گرفتن کامل شواهد معتبر مخالف خودداری کن؛ هدف، دفاع عقلانی و مستند است، نه تبلیغ خام یا اطلاعات نادرست.

"""

ADDITIONAL_INSTRUCTION_2 = """
________________________________________
دستورالعمل تکمیلی ۲ (اولویت منابع رسمی و داده‌های حاکمیتی):

• در فرآیند تحقیق و گردآوری شواهد، فقط از منابع رسمی، معتبر و قابل استناد استفاده کن و از به‌کارگیری هرگونه داده، تحلیل یا آمار غیررسمی موجود در اینترنت (شبکه‌های اجتماعی، وبلاگ‌ها، سایت‌های تحلیلی غیررسمی، رسانه‌های فاقد مرجع آماری) پرهیز کن.

• در اولویت انتخاب منابع، به‌ترتیب زیر عمل کن:
  1. گزارش‌ها، آمارها و بیانیه‌های رسمی بانک مرکزی جمهوری اسلامی ایران
  2. داده‌ها و گزارش‌های منتشرشده توسط مرکز آمار ایران
  3. گزارش‌های تحلیلی، کارشناسی و پژوهشی مرکز پژوهش‌های مجلس شورای اسلامی
  4. در صورت لزوم، سایر نهادهای رسمی دولتی یا حاکمیتی مرتبط با موضوع ادعا

• شواهد انتخاب‌شده باید:
  - مستقیماً به نقل از این نهادها باشند یا
  - توسط رسانه‌های معتبر، با ارجاع صریح و شفاف به این نهادها منتشر شده باشند.

• اگر منبع خبری یا تحلیلی از داده‌های این نهادها استفاده کرده است، فقط در صورتی قابل استفاده است که:
  - منبع داده به‌روشنی مشخص شده باشد،
  - نقل‌قول یا عدد ارائه‌شده دقیقاً قابل تطبیق با گزارش رسمی باشد.

• در صورت وجود تعارض میان داده‌های رسمی و داده‌های غیررسمی موجود در فضای عمومی:
  - داده‌های رسمی را مبنای تحلیل قرار بده،
  - و منابع غیررسمی را فاقد اعتبار تحلیلی تلقی کن، مگر اینکه صرفاً برای توضیح فضای رسانه‌ای یا طرح ادعا ذکر شوند.

• در بخش تحلیل و نتیجه‌گیری، به‌طور مشخص نشان بده که استدلال‌های دفاعی دولت چگونه بر پایه آمار و گزارش‌های رسمی این نهادها شکل می‌گیرند و چرا این منابع نسبت به سایر داده‌های اینترنتی اولویت دارند.

"""


# ================== ERROR HANDLING ==================

class APIError:
    """کلاس برای مدیریت و دسته‌بندی خطاها"""
    
    ERROR_MESSAGES = {
        # خطاهای API
        "RESOURCE_EXHAUSTED": {
            "title": "محدودیت درخواست",
            "message": "تعداد درخواست‌ها به حد مجاز رسیده است. لطفاً چند دقیقه صبر کنید و دوباره تلاش کنید.",
            "icon": "⏱️"
        },
        "RATE_LIMIT": {
            "title": "محدودیت نرخ درخواست",
            "message": "درخواست‌های زیادی در زمان کوتاه ارسال شده. لطفاً کمی صبر کنید.",
            "icon": "🚦"
        },
        "OVERLOADED": {
            "title": "سرور شلوغ است",
            "message": "سرور در حال حاضر شلوغ است. لطفاً چند لحظه دیگر تلاش کنید.",
            "icon": "🔄"
        },
        "SERVICE_UNAVAILABLE": {
            "title": "سرویس در دسترس نیست",
            "message": "سرویس موقتاً در دسترس نیست. لطفاً بعداً تلاش کنید.",
            "icon": "🔌"
        },
        "INVALID_API_KEY": {
            "title": "کلید API نامعتبر",
            "message": "کلید API معتبر نیست. لطفاً با پشتیبانی تماس بگیرید.",
            "icon": "🔑"
        },
        "NETWORK_ERROR": {
            "title": "خطای شبکه",
            "message": "اتصال به سرور برقرار نشد. لطفاً اتصال اینترنت خود را بررسی کنید.",
            "icon": "🌐"
        },
        "TIMEOUT": {
            "title": "پایان زمان انتظار",
            "message": "درخواست بیش از حد طول کشید. لطفاً دوباره تلاش کنید.",
            "icon": "⏰"
        },
        # خطاهای JSON
        "JSON_DECODE_ERROR": {
            "title": "خطای پردازش پاسخ",
            "message": "پاسخ دریافتی قابل پردازش نیست. لطفاً دوباره تلاش کنید.",
            "icon": "📄"
        },
        "NO_JSON_FOUND": {
            "title": "پاسخ نامعتبر",
            "message": "پاسخ سرور ساختار مورد انتظار را ندارد. لطفاً دوباره تلاش کنید.",
            "icon": "❓"
        },
        # خطای پیش‌فرض
        "UNKNOWN": {
            "title": "خطای غیرمنتظره",
            "message": "خطایی رخ داده است. لطفاً دوباره تلاش کنید.",
            "icon": "⚠️"
        }
    }
    
    @classmethod
    def detect_error_type(cls, error_text: str) -> str:
        """تشخیص نوع خطا از متن خطا"""
        error_lower = error_text.lower()
        
        if "resource_exhausted" in error_lower or "quota" in error_lower:
            return "RESOURCE_EXHAUSTED"
        elif "rate" in error_lower and "limit" in error_lower:
            return "RATE_LIMIT"
        elif "overloaded" in error_lower:
            return "OVERLOADED"
        elif "service unavailable" in error_lower or "503" in error_lower:
            return "SERVICE_UNAVAILABLE"
        elif "invalid" in error_lower and "api" in error_lower and "key" in error_lower:
            return "INVALID_API_KEY"
        elif "network" in error_lower or "connection" in error_lower:
            return "NETWORK_ERROR"
        elif "timeout" in error_lower or "timed out" in error_lower:
            return "TIMEOUT"
        elif "jsondecode" in error_lower or "json" in error_lower:
            return "JSON_DECODE_ERROR"
        elif "429" in error_lower:
            return "RATE_LIMIT"
        elif "500" in error_lower or "502" in error_lower:
            return "SERVICE_UNAVAILABLE"
        elif "401" in error_lower or "403" in error_lower:
            return "INVALID_API_KEY"
        else:
            return "UNKNOWN"
    
    @classmethod
    def get_error_html(cls, error_type: str, details: str = None, show_details: bool = False) -> str:
        """تولید HTML برای نمایش خطا"""
        error_info = cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES["UNKNOWN"])
        
        details_html = ""
        if show_details and details:
            details_html = f"""
            <details style="margin-top: 0.8rem; cursor: pointer;">
                <summary style="color: #666; font-size: 0.85rem;">جزئیات فنی</summary>
                <pre style="background: #f5f5f5; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem; font-size: 0.8rem; overflow-x: auto; white-space: pre-wrap; word-break: break-word;">{details}</pre>
            </details>
            """
        
        return f"""
        <div class="error-box">
            <div class="error-header">
                <span class="error-icon">{error_info['icon']}</span>
                <span class="error-title">{error_info['title']}</span>
            </div>
            <p class="error-message">{error_info['message']}</p>
            {details_html}
        </div>
        """
    
    @classmethod
    def format_error(cls, error, raw_response: str = None) -> str:
        """فرمت کردن خطا برای نمایش"""
        error_text = str(error)
        error_type = cls.detect_error_type(error_text)
        return cls.get_error_html(error_type, details=raw_response or error_text, show_details=True)

def get_gemini_client():
    return genai.Client(api_key=API_KEY, http_options={"base_url": "https://api.avalai.ir"})


def sanitize_source_results(results: dict) -> dict:
    if not isinstance(results, dict):
        return {}

    clean_results = results.copy()

    claim = clean_results.get("claim_analyzed", "")
    if not isinstance(claim, str):
        clean_results["claim_analyzed"] = str(claim) if claim else ""

    for key in ["original_source", "initial_publication", "evidence_sources"]:
        items = clean_results.get(key, [])
        if isinstance(items, str):
            try:
                parsed = json.loads(items)
                clean_results[key] = parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                clean_results[key] = []
        elif isinstance(items, dict):
            clean_results[key] = [items]
        elif not isinstance(items, list):
            clean_results[key] = []

    summary = clean_results.get("analysis_summary", "")
    if not isinstance(summary, str):
        clean_results["analysis_summary"] = str(summary) if summary else ""

    return clean_results


def get_source_finder_response(claim: str, model_id: str):
    """دریافت پاسخ از API برای یافتن منشأ ادعا"""
    client = get_gemini_client()

    prompt = f"""
    ادعای مورد بررسی:
    "{claim}"

    لطفاً منشأ اولیه این ادعا را پیدا کنید و نتیجه را به صورت JSON برگردانید.
    """

    tools = [{"google_search": {}}]

    try:
        config = {
            "tools": tools,
            "system_instruction": [types.Part.from_text(text=SYSTEM_INSTRUCTION_SOURCE_FINDER)],
            "temperature": 0.2,
            "response_schema": {
                "type": "object",
                "properties": {
                    "claim_analyzed": {
                        "type": "string",
                        "description": "متن کامل ادعایی که بررسی کردید",
                        "nullable": True
                    },
                    "original_source": {
                        "type": "array",
                        "description": "",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "نام دقیق شخص، گروه، شرکت یا نهادی که ادعا را اولین بار مطرح کرد (یا 'ناشناخته' اگر قابل شناسایی نبود)",
                                    "nullable": True
                                },
                                "type": {
                                    "type": "string",
                                    "description": "نوع منبع (مثال: 'شخص - سیاستمدار'، 'سازمان خبری'، 'گروه تحقیقاتی'، 'کاربر شبکه اجتماعی', 'شرکت', 'نهاد دولتی')",
                                    "nullable": True
                                }
                            }
                        }
                    },
                    "initial_publication": {
                        "type": "array",
                        "description": "",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "platform": {
                                    "type": "string",
                                    "description": "نام پلتفرم یا رسانه‌ای که ادعا اولین بار در آن منتشر شد (مثال: 'توییتر/X'، 'وب‌سایت رسمی شرکت'، 'سخنرانی رسمی'، 'گزارش تحقیقی', 'وب‌سایت خبری XYZ')",
                                    "nullable": True
                                },
                                "reference_title_or_description": {
                                    "type": "string",
                                    "description": "عنوان مقاله، توضیحات پست، یا شرح مختصری از منبع اولیه",
                                    "nullable": True
                                },
                                "publication_date": {
                                    "type": "string",
                                    "description": "تاریخ شمسی دقیق یا تخمینی اولین انتشار (به فرمت YYYY-MM-DD)",
                                    "nullable": True
                                }

                            }
                        }
                    },
                    "analysis_summary": {
                        "type": "string",
                        "description": "توضیح بسیار مختصر در مورد اینکه چگونه این منبع به عنوان منشأ اولیه شناسایی شد و درجه اطمینان از این یافته.",
                        "nullable": True
                    },
                    "evidence_sources": {
                        "type": "array",
                        "description": "",
                        "nullable": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "عنوان منبع کمکی  (مقاله‌ای که به منبع اصلی اشاره دارد)",
                                    "nullable": True
                                },
                                "snippet": {
                                    "type": "string",
                                    "description": "بخش کوتاهی از متن منبع که به ردیابی کمک کرده است",
                                    "nullable": True
                                }
                            }
                        }
                    }
                },
                "required": [
                    "claim_analyzed",
                    "original_source",
                    "initial_publication",
                    "analysis_summary",
                    "evidence_sources",
                
                ]
            }
        }
        if model_id == "gemini-3-flash-preview":
            config["thinking_config"] = types.ThinkingConfig(thinking_level="low")

        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )

        response_text = response.text.strip()
        
        # بررسی خطاهای شناخته شده در متن پاسخ
        error_type = APIError.detect_error_type(response_text)
        if error_type != "UNKNOWN" and error_type not in ["JSON_DECODE_ERROR", "NO_JSON_FOUND"]:
            return {
                "error_type": error_type,
                "error": response_text,
                "raw_response": response_text
            }

        # استخراج JSON از پاسخ
        match = re.search(r'(\{.*\}|\[.*\])', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError as e:
                return {
                    "error_type": "JSON_DECODE_ERROR",
                    "error": str(e),
                    "raw_response": response_text
                }
        else:
            return {
                "error_type": "NO_JSON_FOUND",
                "error": "ساختار JSON در پاسخ یافت نشد",
                "raw_response": response_text
            }

    except Exception as e:
        error_type = APIError.detect_error_type(str(e))
        return {
            "error_type": error_type,
            "error": str(e),
            "raw_response": None
        }


def get_fact_check_response(prompt: str, model_id: str, use_additional_instruction: bool = False, use_additional_instruction_2: bool = False):
    """دریافت پاسخ از API برای راستی‌آزمایی"""
    client = get_gemini_client()

    # تعیین متن دستورالعمل تکمیلی بر اساس وضعیت کلیدها
    additional_text = ""
    if use_additional_instruction:
        additional_text += ADDITIONAL_INSTRUCTION
    if use_additional_instruction_2:
        additional_text += ADDITIONAL_INSTRUCTION_2
    
    # جایگزینی placeholder با متن مناسب
    system_instruction = SYSTEM_INSTRUCTION_FACT_CHECK_BASE.replace(
        "<<ADDITIONAL_INSTRUCTIONS_PLACEHOLDER>>",
        additional_text
    )

    config = {
        "tools": [types.Tool(google_search=types.GoogleSearch())],
        "system_instruction": [types.Part.from_text(text=system_instruction)],
        "temperature": 0.3,
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
                            ],
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
    }
    if model_id == "gemini-3-flash-preview":
        config["thinking_config"] = types.ThinkingConfig(thinking_level="low")

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )
        return {"success": True, "response": response}
    except Exception as e:
        error_type = APIError.detect_error_type(str(e))
        return {
            "success": False,
            "error_type": error_type,
            "error": str(e)
        }


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
            table += f'<th>{h}</th>'
        table += "</tr></thead>"
    table += "<tbody>"
    for row in rows:
        table += "<tr>"
        for cell in row:
            table += f'<td>{cell}</td>'
        table += "</tr>"
    table += "</tbody></table>"
    return table


# ================== Initialize Session State ==================
if "source_results" not in st.session_state:
    st.session_state.source_results = None
if "source_input" not in st.session_state:
    st.session_state.source_input = ""
if "source_status" not in st.session_state:
    st.session_state.source_status = None
if "source_pending" not in st.session_state:
    st.session_state.source_pending = False
if "source_model" not in st.session_state:
    st.session_state.source_model = "gemini-3-flash-preview"

if "fact_check_results" not in st.session_state:
    st.session_state.fact_check_results = None
if "fact_check_status" not in st.session_state:
    st.session_state.fact_check_status = None
if "fact_check_response_obj" not in st.session_state:
    st.session_state.fact_check_response_obj = None
if "fact_check_pending" not in st.session_state:
    st.session_state.fact_check_pending = False
if "fact_check_input" not in st.session_state:
    st.session_state.fact_check_input = ""
if "fact_model" not in st.session_state:
    st.session_state.fact_model = "gemini-3-flash-preview"
if "use_additional_instruction" not in st.session_state:
    st.session_state.use_additional_instruction = False
if "use_additional_instruction_2" not in st.session_state:
    st.session_state.use_additional_instruction_2 = False


# ================== SIDEBAR - انتخاب ابزار ==================
with st.sidebar:
    # انتخاب ابزار در بالاترین قسمت
    st.markdown(
        """
        <div style="text-align: right; padding: 1rem 0;">
            <h2 style="margin: 0; font-size: 1.3rem;">انتخاب ابزار</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    selected_tool = st.radio(
         "ابزار مورد نظر را انتخاب کنید:",
        options=["🎯 یافتن منشأ ادعا", "✅ ابزار راستی آزمایی "],
        key="selected_tool",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # تنظیمات
    st.markdown(
        """
        <div style="text-align: right; padding: 0.5rem 0;">
            <h2 style="margin: 0; font-size: 1.2rem;">تنظیمات</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # تنظیمات بر اساس ابزار انتخاب شده
    if selected_tool == "🎯 یافتن منشأ ادعا":
        st.markdown(
            """
            <p style="font-size: 0.95rem; margin-bottom: 0.5rem;">
                🤖 انتخاب مدل
            </p>
            """,
            unsafe_allow_html=True
        )
        
        def on_source_model_change():
            st.session_state.source_model = st.session_state._source_model_temp
        
        # پیدا کردن index مدل انتخاب شده
        source_model_options = ["gemini-3-flash-preview", "gemini-3-pro-preview"]
        source_model_index = source_model_options.index(st.session_state.source_model) if st.session_state.source_model in source_model_options else 0
        
        st.selectbox(
            "مدل منشأ‌یابی:",
            options=source_model_options,
            index=source_model_index,
            key="_source_model_temp",
            label_visibility="collapsed",
            on_change=on_source_model_change
        )
        
        st.markdown("---")
        
        if st.button("🗑️ پاک کردن نتایج", key="clear_source", use_container_width=True):
            st.session_state.source_results = None
            st.session_state.source_input = ""
            st.session_state.source_status = None
            st.rerun()
    
    else:  # راستی‌آزمایی
        st.markdown(
            """
            <p style="font-size: 0.95rem; margin-bottom: 0.5rem;">
                🤖 انتخاب مدل
            </p>
            """,
            unsafe_allow_html=True
        )
        
        def on_fact_model_change():
            st.session_state.fact_model = st.session_state._fact_model_temp
        
        # پیدا کردن index مدل انتخاب شده
        fact_model_options = ["gemini-3-flash-preview", "gemini-3-pro-preview"]
        fact_model_index = fact_model_options.index(st.session_state.fact_model) if st.session_state.fact_model in fact_model_options else 0
        
        st.selectbox(
            "مدل راستی‌آزمایی:",
            options=fact_model_options,
            index=fact_model_index,
            key="_fact_model_temp",
            label_visibility="collapsed",
            on_change=on_fact_model_change
        )
        
        st.markdown("---")
        
        # کلید تکمیلی دستورالعمل
        st.markdown(
            """
            <p style="font-size: 0.95rem; margin-bottom: 0.5rem;">
                📝 تنظیمات پیشرفته
            </p>
            """,
            unsafe_allow_html=True
        )
        
        def on_checkbox1_change():
            st.session_state.use_additional_instruction = st.session_state._cb1_temp
        
        st.checkbox(
            "درخواست تحلیل جانبدارانه",
            value=st.session_state.use_additional_instruction,
            key="_cb1_temp",
            on_change=on_checkbox1_change
        )
        
        if st.session_state.use_additional_instruction:
            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; font-size: 0.8rem; margin-top: 0.5rem;">
                    تحلیل با تمرکز بر شواهدی که امکان دفاع مستند از عملکرد دولت را فراهم می‌کنند.
                </div>
                """,
                unsafe_allow_html=True
            )
        
        def on_checkbox2_change():
            st.session_state.use_additional_instruction_2 = st.session_state._cb2_temp
        
        st.checkbox(
            "درخواست استفاده از منابع رسمی",
            value=st.session_state.use_additional_instruction_2,
            key="_cb2_temp",
            on_change=on_checkbox2_change
        )
        
        if st.session_state.use_additional_instruction_2:
            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; font-size: 0.8rem; margin-top: 0.5rem;">
                   گردآوری شواهد صرفاً از منابع رسمی مانند بانک مرکزی، مرکز آمار ایران و مرکز پژوهش‌های مجلس، به نقل از خبرگزاری‌های معتبر.
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        if st.button("🗑️ پاک کردن نتایج", key="clear_fact", use_container_width=True):
            st.session_state.fact_check_results = None
            st.session_state.fact_check_input = ""
            st.session_state.fact_check_status = None
            st.session_state.fact_check_response_obj = None
            st.rerun()


# ================== تعیین عنوان هدر بر اساس ابزار انتخاب شده ==================
if selected_tool == "🎯 یافتن منشأ ادعا":
    header_icon = "🎯"
    header_title = "یافتن منشأ ادعا"
else:
    header_icon = "✅"
    header_title = "ابزار راستی آزمایی"

# ================== HEADER ==================
# عنوان اصلی سامانه - با باکس آبی
st.markdown(
    '''
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    ">
        <div style="text-align: center;">
            <h1 class="main-header-title">سامانه تحلیل ادعاهای رسانه‌ای</h1>
            <p class="main-header-subtitle">بررسی صحت و ردیابی منشأ اخبار و ادعاها</p>
        </div>
    </div>
    ''',
    unsafe_allow_html=True
)

# عنوان ابزار انتخاب شده - بدون باکس با گرادیانت
st.markdown(
    f'''
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <h2 style="margin: 0;">
            <span style="font-size: 1.5rem;">{header_icon}</span>
            <span class="tool-title">{header_title}</span>
        </h2>
    </div>
    ''',
    unsafe_allow_html=True
)

# ================== محتوای اصلی بر اساس ابزار انتخاب شده ==================

if selected_tool == "🎯 یافتن منشأ ادعا":
    # ================== یافتن منشأ ادعا ==================
    
    # راهنما در صفحه اصلی
    # راهنما فقط زمانی نمایش داده شود که نتیجه‌ای وجود نداشته باشد و در حال پردازش نباشد
    if not st.session_state.source_results and not st.session_state.source_pending and not st.session_state.source_status:
        st.markdown(
            """
            <div class="guide-box">
                <h4>💡 راهنمای استفاده از ابزار یافتن منشأ ادعا</h4>
                <p>این ابزار منبع اولیه یک ادعا را شناسایی می‌کند:</p>
                <ul>
                    <li><strong>چه کسی:</strong> شخص، گروه یا نهادی که اولین بار ادعا را مطرح کرده</li>
                    <li><strong>کجا:</strong> پلتفرم یا رسانه‌ای که ادعا در آن منتشر شده</li>
                    <li><strong>چه زمانی:</strong> تاریخ تقریبی یا دقیق اولین انتشار</li>
                    <li>مدل ممکن است دچار خطا و توهم شود؛ به همین منظور نتایج قبل از اقدام خاص بررسی شود</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # راهنمای ورود ادعا
    st.markdown(
        """
        <p style="color: #555; font-size: 0.9rem; margin-bottom: 0.3rem;">
            ادعای مورد نظر را در این مکان وارد کنید:
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Input
    source_input = st.text_area(
        "ادعای خود را وارد کنید:",
        height=150,
        placeholder="مثال: ایران بزرگترین تولیدکننده زعفران در جهان است...",
        key="source_input_area",
        value=st.session_state.source_input,
        label_visibility="collapsed"
    )
    
    # ذخیره فوری مقدار برای جلوگیری از پاک شدن با تغییر ابزار
    if source_input != st.session_state.source_input:
        st.session_state.source_input = source_input
    
    source_submit = st.button("🔍 جستجوی منشأ", key="source_submit", use_container_width=True)
    
    # Handle submit - پردازش مستقیم بدون rerun
    if source_submit:
        if not API_KEY:
            st.error("🔑 کلید API تنظیم نشده است.")
        elif not source_input.strip():
            st.markdown(
                """
                <div class="result-box result-box-warning">
                    <h4>⚠️ توجه</h4>
                    <p>لطفاً یک ادعا وارد کنید.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # ذخیره ورودی
            st.session_state.source_input = source_input
            st.session_state.source_results = None
            
            # نمایش وضعیت در حال پردازش با spinner
            with st.spinner(""):
                st.markdown(
                    """
                    <div class="loading-box">
                        <h4>⏳ در حال جستجو...</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                results = get_source_finder_response(source_input, st.session_state.source_model)
                
                # بررسی خطا
                if "error_type" in results or "error" in results:
                    error_type = results.get("error_type", "UNKNOWN")
                    raw_response = results.get("raw_response")
                    st.session_state.source_status = APIError.get_error_html(
                        error_type, 
                        details=raw_response,
                        show_details=True
                    )
                    st.session_state.source_results = None
                else:
                    st.session_state.source_results = sanitize_source_results(results)
                    st.session_state.source_status = None
            
            # بعد از اتمام پردازش، صفحه را refresh کن تا نتایج نمایش داده شود
            st.rerun()
    
    # نمایش خطا اگر وجود داشته باشد
    if st.session_state.source_status:
        st.markdown(st.session_state.source_status, unsafe_allow_html=True)
    
    # Display results
    if st.session_state.source_results:
        results = st.session_state.source_results
        
        # ادعای بررسی شده
        claim = results.get("claim_analyzed", "")
        if claim:
            st.markdown(
                f"""
                <div class="result-box">
                    <h4>📋 ادعای بررسی شده</h4>
                    <p>{claim}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # منشأ اولیه
        sources = results.get("original_source", [])
        if sources:
            sources_html = ""
            for src in sources:
                name = src.get("name", "نامشخص")
                src_type = src.get("type", "نامشخص")
                sources_html += f"<p><strong>👤 {name}</strong><br>نوع: {src_type}</p>"
            
            st.markdown(
                f"""
                <div class="result-box result-box-success">
                    <h4>🎯 منشأ اولیه ادعا</h4>
                    {sources_html}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # اولین انتشار
        publications = results.get("initial_publication", [])
        if publications:
            pubs_html = ""
            for pub in publications:
                platform = pub.get("platform", "نامشخص")
                title = pub.get("reference_title_or_description", "نامشخص")
                date = pub.get("publication_date", "نامشخص")
                pubs_html += f"""
                <p>
                    <strong>🌐 پلتفرم:</strong> {platform}<br>
                    <strong>📝 عنوان:</strong> {title}<br>
                    <strong>📅 تاریخ:</strong> {date}
                </p>
                """
            
            st.markdown(
                f"""
                <div class="result-box">
                    <h4>📰 اولین انتشار</h4>
                    {pubs_html}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # خلاصه تحلیل
        summary = results.get("analysis_summary", "")
        if summary:
            st.markdown(
                f"""
                <div class="result-box">
                    <h4>📊 جمع‌بندی یافته ها </h4>
                    <p>{summary}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # شواهد
        evidence = results.get("evidence_sources", [])
        if evidence:
            with st.expander("📚 شواهد و منابع کمکی"):
                for ev in evidence:
                    title = ev.get("title", "بدون عنوان")
                    snippet = ev.get("snippet", "")
                    st.markdown(f"**{title}**")
                    if snippet:
                        st.markdown(f"> {snippet}")
                    st.markdown("---")


else:
    # ================== راستی‌آزمایی کامل ==================
    
    # راهنما فقط زمانی نمایش داده شود که نتیجه‌ای وجود نداشته باشد و در حال پردازش نباشد
    if not st.session_state.fact_check_results and not st.session_state.fact_check_pending and not st.session_state.fact_check_status:
        st.markdown(
            """
            <div class="guide-box">
                <h4>💡 راهنمای استفاده از ابزار راستی‌آزمایی کامل</h4>
                <p>این ابزار صحت ادعاها را بررسی می‌کند.</p>
                <ul>
                    <li>تنها متن ادعا یا خلاصه آن کفایت دارد و از معرفی لینک خودداری شود</li>
                    <li>تنها ادعاهای رسانه‌ای اقتصادی پشتیبانی می‌شود</li>
                    <li>صحت‌سنجی براساس منابع و تحلیل سایت‌های داخلی و خارجی بررسی می‌شود</li>
                    <li>مدل ممکن است دچار خطا و توهم شود؛ به همین منظور نتایج قبل از اقدام خاص بررسی شود</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Input area - استفاده از value برای حفظ مقدار
    fact_input = st.text_area(
        "متن را وارد کنید:",
        height=200,
        placeholder="متن خبر یا ادعا را اینجا وارد کنید...",
        value=st.session_state.fact_check_input,
        key="fact_check_input_area",
        label_visibility="collapsed"
    )
    
    # ذخیره فوری مقدار برای جلوگیری از پاک شدن با تغییر چک‌باکس‌ها
    if fact_input != st.session_state.fact_check_input:
        st.session_state.fact_check_input = fact_input

    fact_submit = st.button("✅ ارسال برای راستی‌آزمایی", key="fact_submit", use_container_width=True)

    # Handle submit - پردازش مستقیم بدون rerun
    if fact_submit:
        if not API_KEY:
            st.error("🔑 کلید API تنظیم نشده است.")
        elif not fact_input.strip():
            st.markdown(
                """
                <div class="result-box result-box-warning">
                    <h4>⚠️ توجه</h4>
                    <p>لطفاً یک متن معتبر وارد کنید.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # ذخیره ورودی
            st.session_state.fact_check_input = fact_input
            st.session_state.fact_check_results = None
            st.session_state.fact_check_response_obj = None
            
            # نمایش وضعیت در حال پردازش با spinner
            with st.spinner(""):
                st.markdown(
                    """
                    <div class="loading-box">
                        <h4>⏳ در حال راستی‌آزمایی...</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                result = get_fact_check_response(
                    fact_input, 
                    st.session_state.fact_model,
                    st.session_state.use_additional_instruction,
                    st.session_state.use_additional_instruction_2
                )
                
                # بررسی خطای API
                if not result.get("success", False):
                    error_type = result.get("error_type", "UNKNOWN")
                    error_html = APIError.get_error_html(
                        error_type,
                        details=result.get("error"),
                        show_details=True
                    )
                    st.session_state.fact_check_status = error_html
                    st.session_state.fact_check_results = None
                    st.session_state.fact_check_response_obj = None
                else:
                    response = result["response"]
                    st.session_state.fact_check_results = response.text
                    st.session_state.fact_check_response_obj = response
                    st.session_state.fact_check_status = ""
            
            # بعد از اتمام پردازش، صفحه را refresh کن تا نتایج نمایش داده شود
            st.rerun()

    # نمایش خطا اگر وجود داشته باشد
    if st.session_state.fact_check_status:
        st.markdown(st.session_state.fact_check_status, unsafe_allow_html=True)

    # Display results
    if st.session_state.fact_check_results:
        text = st.session_state.fact_check_results
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)

                if (
                    "total_fact_checking" in data
                    and isinstance(data["total_fact_checking"], list)
                    and len(data["total_fact_checking"]) > 0
                ):
                    fact_check = data["total_fact_checking"][0]
                    summary_of_findings = fact_check.get("summary_of_findings", "")
                    verdict = fact_check.get("verdict", "")
                    reasoning = fact_check.get("reasoning", "")

                    verdict_class = ""
                    if verdict in ["درست"]:
                        verdict_class = "result-box-success"
                    elif verdict in ["نیمه درست", "گمراه کننده"]:
                        verdict_class = "result-box-warning"
                    elif verdict in ["نادرست"]:
                        verdict_class = "result-box-error"

                    if verdict:
                        st.markdown(
                            f"""
                            <div class="result-box {verdict_class}">
                                <h4>🏷️ برچسب نهایی</h4>
                                <p style="font-size: 1.2rem; font-weight: 700;">{verdict}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if summary_of_findings:
                        st.markdown(
                            f"""
                            <div class="result-box">
                                <h4>📊 نتیجه کلی راستی‌آزمایی</h4>
                                <p>{summary_of_findings}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if reasoning:
                        st.markdown(
                            f"""
                            <div class="result-box">
                                <h4>📚 استدلال</h4>
                                <p>{reasoning}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # Extract references
                    try:
                        if st.session_state.fact_check_response_obj:
                            extract_ref = st.session_state.fact_check_response_obj.candidates[0].grounding_metadata.search_entry_point.rendered_content
                            soup = BeautifulSoup(extract_ref, "html.parser")
                            chips = soup.select("div.carousel a.chip")
                            if chips:
                                chips_html = "<br>".join([f'• <a href="{chip.get("href")}" target="_blank" style="color: #667eea;">{chip.get_text(strip=True)}</a>' for chip in chips])
                                st.markdown(
                                    f"""
                                    <div class="result-box">
                                        <h4>🔎 پیشنهادات جستجو در گوگل</h4>
                                        <p>{chips_html}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                    except Exception:
                        pass

                # Full table in expander
                table_html = """
                <style>
                .fact-table-container table { 
                    font-family: 'B Homa', 'B Nazanin', Tahoma, sans-serif !important; 
                    font-size: 14px; 
                    direction: rtl; 
                    text-align: right;
                    border-collapse: collapse;
                    width: 100%;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    margin-bottom: 1rem;
                }
                .fact-table-container th {
                    background: #667eea !important;
                    color: white !important;
                    padding: 10px 12px !important;
                    font-weight: bold !important;
                    font-family: 'B Homa', 'B Nazanin', Tahoma, sans-serif !important;
                }
                .fact-table-container td {
                    padding: 8px 12px !important;
                    border-bottom: 1px solid #e0e0e0 !important;
                    font-family: 'B Homa', 'B Nazanin', Tahoma, sans-serif !important;
                    vertical-align: top;
                }
                .fact-table-container tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                .fact-table-container table table {
                    box-shadow: none;
                    margin: 0.5rem 0;
                }
                </style>
                <div class="fact-table-container">
                """
                table_html += build_table_from_dict(data)
                table_html += "</div>"
                
                with st.expander("📋 جزئیات کامل تحلیل", expanded=False):
                    st.markdown(table_html, unsafe_allow_html=True)

            except json.JSONDecodeError as e:
                error_html = APIError.get_error_html(
                    "JSON_DECODE_ERROR",
                    details=str(e),
                    show_details=True
                )
                st.markdown(error_html, unsafe_allow_html=True)
        else:
            error_html = APIError.get_error_html(
                "NO_JSON_FOUND",
                details=text[:500] if len(text) > 500 else text,
                show_details=True
            )
            st.markdown(error_html, unsafe_allow_html=True)
