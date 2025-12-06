import streamlit as st
import requests
import base64
import time

st.set_page_config(
    page_title="LittleHeroes - Pediatric Storybooks",
    page_icon="https://cdn-icons-png.flaticon.com/512/2232/2232688.png",
    layout="wide"
)

# Initialize session state for animation
if 'animation_complete' not in st.session_state:
    st.session_state.animation_complete = False

# Custom CSS with video background and high-contrast design
st.markdown("""
    <style>
    /* Import external icon library */
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* Video Background */
    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        overflow: hidden;
    }
    
    .video-background::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1;
    }
    
    .video-background video {
        position: absolute;
        top: 50%;
        left: 50%;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        transform: translate(-50%, -50%);
        object-fit: cover;
    }
    
    /* Animated gradient background fallback */
    .main {
        background: linear-gradient(-45deg, #1e3c72, #2a5298, #7e22ce, #c026d3);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 0;
        min-height: 100vh;
        position: relative;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Content overlay with high contrast */
    .content-overlay {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 30px;
        padding: 2.5rem;
        margin: 2rem;
        box-shadow: 0 25px 70px rgba(0,0,0,0.5);
        animation: fadeInUp 1s ease-out;
        backdrop-filter: blur(10px);
        border: 3px solid rgba(124, 58, 237, 0.3);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Startup Animation Container */
    .startup-animation {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100vh;
        background: linear-gradient(135deg, #1e1e2e 0%, #2d1b69 50%, #1e1e2e 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeOutStartup 0.8s ease-out 3s forwards;
    }
    
    @keyframes fadeOutStartup {
        to {
            opacity: 0;
            visibility: hidden;
        }
    }
    
    .startup-logo {
        text-align: center;
        animation: logoZoomIn 2.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    @keyframes logoZoomIn {
        0% {
            opacity: 0;
            transform: scale(0.2) rotate(-20deg);
        }
        60% {
            opacity: 1;
            transform: scale(1.15) rotate(5deg);
        }
        80% {
            transform: scale(0.95) rotate(-2deg);
        }
        100% {
            opacity: 1;
            transform: scale(1) rotate(0deg);
        }
    }
    
    .startup-logo-icon {
        background: white;
        border-radius: 25px;
        padding: 2rem;
        display: inline-block;
        box-shadow: 0 15px 30px rgba(124, 58, 237, 0.8);
        animation: iconGlow 2s ease-in-out infinite;
    }
    
    .startup-logo-icon img {
        width: 160px;
        height: 160px;
        display: block;
    }
    
    @keyframes iconGlow {
        0%, 100% {
            box-shadow: 0 15px 30px rgba(124, 58, 237, 0.8);
        }
        50% {
            box-shadow: 0 20px 50px rgba(192, 38, 211, 1);
        }
    }
    
    .startup-logo-text {
        color: #ffffff;
        font-size: 4rem;
        font-weight: 900;
        text-shadow: 4px 4px 8px rgba(0,0,0,0.5);
        margin: 1.5rem 0 0 0;
        letter-spacing: 2px;
    }
    
    .startup-tagline {
        color: #e0e0ff;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        font-weight: 300;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .loading-bar {
        width: 300px;
        height: 4px;
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        margin: 2rem auto 0;
        overflow: hidden;
    }
    
    .loading-bar::after {
        content: '';
        display: block;
        width: 50%;
        height: 100%;
        background: linear-gradient(90deg, #7c3aed, #c026d3);
        animation: loadingProgress 2s ease-in-out infinite;
        border-radius: 10px;
    }
    
    @keyframes loadingProgress {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(300%); }
    }
    
    /* Logo container at top with enhanced visibility */
    .logo-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 25px;
        text-align: center;
        margin: 0 auto 2.5rem auto;
        max-width: 350px;
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.4);
        border: 4px solid #6366f1;
        animation: zoomIn 0.8s ease-out 0.3s both;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .logo-container:hover {
        transform: scale(1.05);
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.6);
    }
    
    @keyframes zoomIn {
        from {
            opacity: 0;
            transform: scale(0.4);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .logo-container img {
        max-width: 200px;
        height: auto;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 5px 15px rgba(99, 102, 241, 0.3));
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    
    .logo-text {
        color: #1e293b;
        font-size: 1.2rem;
        margin-top: 1rem;
        font-weight: 700;
    }
    
    /* Main title section */
    .main-title {
        text-align: center;
        margin: 2rem 0;
        animation: slideDown 0.8s ease-out 0.5s both;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-60px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main-title h1 {
        color: #6366f1;
        font-size: 3.5rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(99, 102, 241, 0.2);
    }
    
    .main-title p {
        color: #475569;
        font-size: 1.5rem;
        margin-top: 0.8rem;
        font-weight: 600;
    }
    
    /* Story display box with high contrast */
    .story-box {
        background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);
        color: #1e293b;
        padding: 3.5rem;
        border-radius: 30px;
        border: 4px solid #6366f1;
        margin-top: 2.5rem;
        box-shadow: 0 20px 50px rgba(99, 102, 241, 0.4);
        animation: slideInLeft 0.8s ease-out;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-60px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .story-box h2 {
        color: #6366f1;
        font-size: 3rem;
        margin-bottom: 2rem;
        border-bottom: 5px solid #6366f1;
        padding-bottom: 1rem;
        font-weight: 800;
    }
    
    .story-box p {
        color: #1e293b;
        font-size: 1.3rem;
        line-height: 2.2;
        font-weight: 500;
    }
    
    /* Enhanced button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 800;
        padding: 1.5rem;
        border-radius: 20px;
        border: none;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.5);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.4);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 400px;
        height: 400px;
    }
    
    .stButton>button:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.7);
    }
    
    /* Success banner with high visibility */
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: #ffffff;
        padding: 2.5rem;
        border-radius: 25px;
        border: 3px solid #059669;
        margin: 2.5rem 0;
        text-align: center;
        font-size: 1.6rem;
        font-weight: 800;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.5);
        animation: bounceIn 0.8s ease-out;
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.2);
        }
        50% {
            opacity: 1;
            transform: scale(1.08);
        }
        70% {
            transform: scale(0.92);
        }
        100% {
            transform: scale(1);
        }
    }
    
    /* Storybook preview with pulsing animation */
    .storybook-preview {
        background: linear-gradient(135deg, #ef4444 0%, #f59e0b 50%, #eab308 100%);
        border: 3px solid #dc2626;
        border-radius: 30px;
        padding: 3rem;
        color: #ffffff;
        text-align: center;
        box-shadow: 0 20px 50px rgba(239, 68, 68, 0.5);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 20px 50px rgba(239, 68, 68, 0.5);
        }
        50% { 
            transform: scale(1.04);
            box-shadow: 0 25px 60px rgba(239, 68, 68, 0.7);
        }
    }
    
    .storybook-preview h2 {
        color: #ffffff;
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    }
    
    .storybook-preview p {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Page card with enhanced visibility */
    .page-card {
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        padding: 3rem;
        border-radius: 30px;
        margin: 3rem 0;
        box-shadow: 0 20px 50px rgba(99, 102, 241, 0.3);
        border: 4px solid #6366f1;
        animation: flipIn 0.8s ease-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .page-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 60px rgba(99, 102, 241, 0.4);
    }
    
    @keyframes flipIn {
        from {
            opacity: 0;
            transform: perspective(600px) rotateY(90deg);
        }
        to {
            opacity: 1;
            transform: perspective(600px) rotateY(0deg);
        }
    }
    
    .page-number {
        color: #6366f1;
        font-size: 2.2rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(99, 102, 241, 0.2);
    }
    
    /* Text content with enhanced readability */
    .text-content {
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-top: 2rem;
        border-left: 8px solid #6366f1;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.2);
    }
    
    .text-content p {
        font-size: 1.4rem;
        line-height: 2.2;
        color: #1e293b;
        margin: 0;
        font-weight: 600;
    }
    
    /* Sidebar removal - make it invisible */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Main content takes full width */
    .main .block-container {
        max-width: 100%;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    /* Form container styling */
    .form-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 3rem;
        border-radius: 30px;
        border: 4px solid #6366f1;
        margin: 2rem 0;
        box-shadow: 0 15px 40px rgba(99, 102, 241, 0.4);
        animation: slideInLeft 0.8s ease-out 0.6s both;
    }
    
    .form-container h3 {
        color: #6366f1;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        text-align: center;
        border-bottom: 4px solid #6366f1;
        padding-bottom: 1rem;
    }
    
    /* Input styling for main page */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background: #ffffff !important;
        border: 3px solid #6366f1 !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        padding: 0.8rem !important;
    }
    
    .stTextInput label,
    .stNumberInput label,
    .stTextArea label,
    .stRadio label {
        color: #6366f1 !important;
        font-weight: 800 !important;
        font-size: 1.3rem !important;
    }
    
    /* Section headers */
    .stMarkdown h4 {
        color: #6366f1 !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Info cards with high contrast */
    .info-card {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        padding: 2.5rem;
        border-radius: 25px;
        border: 4px solid #3b82f6;
        margin: 2rem 0;
        color: #1e40af;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        animation: slideInRight 0.8s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(60px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .info-card h3 {
        color: #1e3a8a;
        margin-top: 0;
        font-size: 1.8rem;
        font-weight: 800;
    }
    
    .info-card p, .info-card li {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        line-height: 1.9;
    }
    
    .tips-card {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        padding: 2.5rem;
        border-radius: 25px;
        border: 4px solid #f97316;
        margin: 2rem 0;
        color: #7c2d12;
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.3);
        animation: slideInRight 0.8s ease-out 0.2s both;
    }
    
    .tips-card h3 {
        color: #7c2d12;
        margin-top: 0;
        font-size: 1.8rem;
        font-weight: 800;
    }
    
    .tips-card p, .tips-card li {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        line-height: 1.9;
    }
    
    /* Warning box with high visibility */
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 4px solid #f59e0b;
        color: #92400e;
        box-shadow: 0 8px 20px rgba(245, 158, 11, 0.3);
        animation: shake 0.5s ease-out;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-12px); }
        75% { transform: translateX(12px); }
    }
    
    /* Error box with high visibility */
    .error-box {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 4px solid #ef4444;
        color: #7f1d1d;
        box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3);
        animation: shake 0.5s ease-out;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* Download container with glow effect */
    .download-container {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        padding: 3rem;
        border-radius: 30px;
        text-align: center;
        margin: 3rem 0;
        border: 3px solid #059669;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.6);
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 40px rgba(16, 185, 129, 0.6); }
        50% { box-shadow: 0 0 60px rgba(16, 185, 129, 0.9); }
    }
    
    .download-container h3 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Footer with enhanced visibility */
    .footer {
        text-align: center;
        padding: 3rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
        border-radius: 30px;
        color: #ffffff;
        margin-top: 4rem;
        box-shadow: 0 -15px 40px rgba(30, 41, 59, 0.5);
        animation: slideUp 0.8s ease-out;
        border: 3px solid rgba(99, 102, 241, 0.3);
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(60px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .footer h2 {
        color: #ffffff;
        font-size: 3rem;
        font-weight: 900;
    }
    
    .footer p {
        color: #e5e7eb;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 14px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    }
    
    /* Ensure all text is readable */
    p, span, div, li {
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
    }
    </style>
""", unsafe_allow_html=True)

# Video background
st.markdown("""
<div class="video-background">
    <video autoplay muted loop playsinline>
        <source src="https://cdn.pixabay.com/vimeo/351031397/bokeh-26888.mp4?width=1280&hash=f47a61c7ce858df44fb859d0f9d38b7a3d4a0d2e" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# Startup Animation with logo only
if not st.session_state.animation_complete:
    st.markdown("""
    <div class="startup-animation" id="startupAnimation">
        <div class="startup-logo">
            <div class="startup-logo-icon">
                <img src="https://cdn-icons-png.flaticon.com/512/2232/2232688.png" alt="LittleHeroes Logo">
            </div>
            <h1 class="startup-logo-text">LITTLEHEROES</h1>
            <p class="startup-tagline">Creating Magical Stories for Children</p>
            <div class="loading-bar"></div>
        </div>
    </div>
    <script>
        setTimeout(function() {
            document.getElementById('startupAnimation').style.display = 'none';
        }, 3800);
    </script>
    """, unsafe_allow_html=True)
    time.sleep(4)
    st.session_state.animation_complete = True
    st.rerun()

# Main content wrapper
st.markdown('<div class="content-overlay">', unsafe_allow_html=True)

# Logo at the top
st.markdown("""
<div class="logo-container">
    <img src="https://cdn-icons-png.flaticon.com/512/2232/2232688.png" alt="LittleHeroes Logo">
    <p class="logo-text">LITTLEHEROES</p>
</div>
""", unsafe_allow_html=True)

# Main title
st.markdown("""
<div class="main-title">
    <h1><i class="fas fa-book-medical"></i> LITTLEHEROES</h1>
    <p>Creating Beautiful Medical Storybooks for Children</p>
</div>
""", unsafe_allow_html=True)

# Child Information Form
st.markdown("""
<div class="form-container">
    <h3><i class="fas fa-pencil-alt"></i> LITTLE ONE'S ADVENTURE DETAILS</h3>
</div>
""", unsafe_allow_html=True)

# Create two columns for form layout
form_col1, form_col2 = st.columns(2)

with form_col1:
    # Child's Name
    child_name = st.text_input(
        "👤 Child's Name", 
        placeholder="e.g., Emma, Noah", 
        help="Enter the child's first name", 
        key="child_name"
    )

with form_col2:
    # Age
    age = st.number_input(
        "🎂 Age", 
        min_value=3, 
        max_value=18, 
        value=7, 
        help="Child's age (3-18 years)",
        key="child_age"
    )

# Medical Condition Section
st.markdown("#### 🏥 Medical Condition")

# Medical Condition Quick Select (above input)
st.markdown('<p style="color: #6366f1; font-weight: 700; font-size: 0.9rem; margin: 0.5rem 0;">💡 Quick Select:</p>', unsafe_allow_html=True)

condition_cols = st.columns(6)
with condition_cols[0]:
    if st.button("🦷 Braces", key="rec_braces", use_container_width=True):
        st.session_state.condition_input = "braces"
        st.rerun()
with condition_cols[1]:
    if st.button("🦷 Cavities", key="rec_cavities", use_container_width=True):
        st.session_state.condition_input = "cavities"
        st.rerun()
with condition_cols[2]:
    if st.button("🦷 Extraction", key="rec_extraction", use_container_width=True):
        st.session_state.condition_input = "tooth extraction"
        st.rerun()
with condition_cols[3]:
    if st.button("👓 Eye Exam", key="rec_eye_exam", use_container_width=True):
        st.session_state.condition_input = "eye exam"
        st.rerun()
with condition_cols[4]:
    if st.button("👓 Glasses", key="rec_glasses", use_container_width=True):
        st.session_state.condition_input = "glasses"
        st.rerun()
with condition_cols[5]:
    if st.button("👁️ Myopia", key="rec_myopia", use_container_width=True):
        st.session_state.condition_input = "myopia"
        st.rerun()

# Medical Condition Input (below buttons)
condition = st.text_input(
    "Or type your own:", 
    placeholder="Type medical condition here...",
    help="Enter the medical condition",
    key="condition_input",
    max_chars=100,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# Interests & Hobbies Section
st.markdown("#### 🎨 Interests & Hobbies")

# Interests Quick Select (above input)
st.markdown('<p style="color: #6366f1; font-weight: 700; font-size: 0.9rem; margin: 0.5rem 0;">💡 Quick Select:</p>', unsafe_allow_html=True)

interest_cols = st.columns(6)
with interest_cols[0]:
    if st.button("🎨 Art", key="rec_art", use_container_width=True):
        st.session_state.interests_input = "art, drawing, painting"
        st.rerun()
with interest_cols[1]:
    if st.button("🗺️ Adventure", key="rec_adventure", use_container_width=True):
        st.session_state.interests_input = "adventure, exploration, treasure hunting"
        st.rerun()
with interest_cols[2]:
    if st.button("🦖 Dinosaurs", key="rec_dino", use_container_width=True):
        st.session_state.interests_input = "dinosaurs, fossils, prehistoric animals"
        st.rerun()
with interest_cols[3]:
    if st.button("🚀 Space", key="rec_space", use_container_width=True):
        st.session_state.interests_input = "space, planets, rockets, astronauts"
        st.rerun()
with interest_cols[4]:
    if st.button("⚽ Sports", key="rec_sports", use_container_width=True):
        st.session_state.interests_input = "soccer, basketball, running"
        st.rerun()
with interest_cols[5]:
    if st.button("🐾 Animals", key="rec_animals", use_container_width=True):
        st.session_state.interests_input = "animals, pets, wildlife"
        st.rerun()

# Interests Input (below buttons)
interests = st.text_input(
    "Or type your own:", 
    placeholder="Type interests here (comma separated)...",
    help="These will be woven into the story!",
    key="interests_input",
    max_chars=200,
    label_visibility="collapsed"
)

st.markdown("---")

# Output format selection
st.markdown("### 📦 Choose Your Output Format")
col_format1, col_format2, col_format3 = st.columns([1, 2, 1])

with col_format2:
    output_type = st.radio(
        "",
        ["Text Story Only (5-10 seconds)", "Illustrated Storybook PDF (2-3 minutes)"],
        help="Storybook includes custom AI-generated illustrations"
    )
    
    if "Illustrated Storybook" in output_type:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                    padding: 1.5rem; border-radius: 15px; border: 3px solid #3b82f6; 
                    text-align: center; margin-top: 1rem;">
            <p style="color: #1e40af; font-weight: 700; font-size: 1.2rem; margin: 0;">
                <i class="fas fa-book"></i> Creates a beautiful 4-page illustrated storybook with custom artwork!
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Generate button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate_btn = st.button("✨ CREATE MY STORY", type="primary", use_container_width=True)

# Info sections in organized layout
st.markdown("---")
st.markdown("## 📚 Everything You Need to Know")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3><i class="fas fa-magic"></i> HOW IT WORKS</h3>
        <ol style="line-height: 2.2;">
            <li><strong>Fill in</strong> child's details above</li>
            <li><strong>Choose</strong> your preferred format</li>
            <li><strong>Click</strong> Create My Story</li>
            <li><strong>Read together</strong> with your child</li>
            <li><strong>Keep forever!</strong> Print & treasure</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3><i class="fas fa-book-open"></i> STORYBOOK FEATURES</h3>
        <ul style="line-height: 2.2;">
            <li><i class="fas fa-palette"></i> Custom AI-generated illustrations</li>
            <li><i class="fas fa-child"></i> Child-friendly artwork & language</li>
            <li><i class="fas fa-rainbow"></i> Personalized to their interests</li>
            <li><i class="fas fa-file-pdf"></i> Professional PDF format</li>
            <li><i class="fas fa-images"></i> 4 beautifully illustrated pages</li>
            <li><i class="fas fa-print"></i> Print-ready quality</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <h3><i class="fas fa-clock"></i> GENERATION TIMES</h3>
        <p style="margin: 0.8rem 0; font-size: 1.15rem;"><strong>Text Story:</strong> 5-10 seconds <i class="fas fa-bolt"></i></p>
        <p style="margin: 0.8rem 0; font-size: 1.15rem;"><strong>Illustrated Storybook:</strong> 2-3 minutes <i class="fas fa-hourglass-half"></i></p>
        <p style="margin-top: 1.5rem; font-style: italic; font-size: 1.05rem; color: #1e40af;">
            Custom illustrations take time but are worth the wait! ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

col4, col5 = st.columns(2)

with col4:
    st.markdown("""
    <div class="tips-card">
        <h3><i class="fas fa-lightbulb"></i> TIPS FOR BEST RESULTS</h3>
        <ul style="line-height: 2.2;">
            <li>Be <strong>specific</strong> about interests</li>
            <li>Use <strong>positive</strong> language</li>
            <li>Include <strong>2-3 hobbies</strong></li>
            <li><strong>Visual interests</strong> work best (animals, space, art)</li>
            <li>Print the storybook for a <strong>special keepsake!</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="info-card">
        <h3><i class="fas fa-gift"></i> WHAT YOU'LL GET</h3>
        <p style="font-weight: 700; margin: 0.8rem 0; font-size: 1.1rem;">
            <strong>Cover Page:</strong> Personalized title with child's name
        </p>
        <p style="font-weight: 700; margin: 1.2rem 0 0.5rem 0; font-size: 1.1rem;">
            <strong>4 Story Pages Include:</strong>
        </p>
        <ul style="line-height: 2;">
            <li>Custom AI illustration per page</li>
            <li>2-3 sentences of engaging story</li>
            <li>Large, readable font</li>
            <li>Preview in your browser</li>
            <li>Downloadable PDF format</li>
        </ul>
        <p style="margin-top: 1.5rem; font-weight: 700; font-size: 1.15rem; color: #1e40af;">
            <i class="fas fa-print"></i> Print & Bind: Create a lasting memory! 💙
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Backend status check
try:
    health = requests.get("http://localhost:8000/health", timeout=2).json()
    if not health.get('openai_configured'):
        st.markdown('<div class="warning-box"><i class="fas fa-exclamation-triangle"></i> <strong>NOTICE:</strong> OpenAI API key not configured. Storybook illustrations will be limited.</div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="error-box"><i class="fas fa-times-circle"></i> <strong>BACKEND OFFLINE:</strong> Please start the backend with: <code>uvicorn main:app --reload</code></div>', unsafe_allow_html=True)

st.markdown("---")

# Main content area - Story generation results
if generate_btn:
    if not all([child_name, condition, interests]):
        st.markdown('<div class="error-box"><i class="fas fa-times-circle"></i> <strong>ERROR:</strong> Please fill in all fields to create your story!</div>', unsafe_allow_html=True)
    else:
        output_format = "storybook" if "Illustrated Storybook" in output_type else "text"
        
        # Progress indicator
        if output_format == "storybook":
            progress_text = "Creating your personalized storybook (2-3 minutes)..."
            st.markdown("""
            <div class="storybook-preview">
                <h2><i class="fas fa-magic"></i> CREATING YOUR MAGICAL STORYBOOK...</h2>
                <p style="font-size: 1.4rem; margin: 1.5rem 0;">We're generating 4 custom illustrations just for you!</p>
                <p style="font-size: 1.2rem;"><em>This takes a few minutes but will be worth the wait ✨</em></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            progress_text = "Creating your personalized story..."
        
        progress_bar = st.progress(0, text=progress_text)
        
        try:
            progress_bar.progress(20, text="📝 Writing your story...")
            
            response = requests.post(
                "http://localhost:8000/generate-story",
                json={
                    "child_name": child_name,
                    "age": age,
                    "condition": condition,
                    "treatment": condition,  # Use condition as treatment since we removed the field
                    "interests": interests,
                    "output_type": output_format
                },
                timeout=600
            )
            
            progress_bar.progress(100, text="✅ Complete!")
            time.sleep(0.5)
            progress_bar.empty()
            
            if response.status_code == 200:
                data = response.json()
                
                # Success message
                if data.get('pdf_data'):
                    st.balloons()
                    st.markdown('<div class="success-banner"><i class="fas fa-check-circle"></i> YOUR PERSONALIZED STORYBOOK IS READY!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-banner"><i class="fas fa-check-circle"></i> YOUR STORY IS READY! 🎉</div>', unsafe_allow_html=True)
                
                # Display story
                st.markdown(f"""
                <div class="story-box">
                    <h2><i class="fas fa-book"></i> {child_name.upper()}'S SPECIAL STORY</h2>
                    <p>{data['story'].replace('\n', '<br><br>')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display pages with images
                if data.get('pages'):
                    st.markdown("---")
                    st.markdown("### 📖 YOUR ILLUSTRATED STORYBOOK PREVIEW")
                    
                    for page_data in data['pages']:
                        st.markdown(f"""
                        <div class="page-card">
                            <div class="page-number"><i class="fas fa-file-alt"></i> PAGE {page_data['page']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        img_bytes = base64.b64decode(page_data['image'])
                        st.image(img_bytes, use_container_width=True)
                        
                        st.markdown(f"""
                        <div class="text-content">
                            <p>{page_data['text']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                
                # PDF download
                if data.get('pdf_data'):
                    st.markdown("---")
                    pdf_bytes = base64.b64decode(data['pdf_data'])
                    
                    st.markdown('<div class="download-container">', unsafe_allow_html=True)
                    st.markdown("<h3><i class='fas fa-download'></i> DOWNLOAD YOUR STORYBOOK</h3>", unsafe_allow_html=True)
                    
                    col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
                    with col_pdf2:
                        st.download_button(
                            label="📥 DOWNLOAD ILLUSTRATED STORYBOOK (PDF)",
                            data=pdf_bytes,
                            file_name=f"{child_name}_storybook.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="tips-card"><i class="fas fa-lightbulb"></i> <strong>TIP:</strong> Print the storybook and read it together! Create a lasting memory 💙</div>', unsafe_allow_html=True)
                    
                elif data.get('message'):
                    st.markdown(f'<div class="warning-box"><i class="fas fa-exclamation-triangle"></i> {data["message"]}</div>', unsafe_allow_html=True)
                
                # Text download
                if not data.get('pdf_data'):
                    st.markdown("---")
                    st.download_button(
                        label="📥 DOWNLOAD STORY TEXT",
                        data=data['story'],
                        file_name=f"{child_name}_story.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.markdown(f'<div class="error-box"><i class="fas fa-times-circle"></i> FAILED TO GENERATE STORY. STATUS: {response.status_code}</div>', unsafe_allow_html=True)
                
        except requests.exceptions.Timeout:
            st.markdown('<div class="error-box"><i class="fas fa-clock"></i> <strong>TIMEOUT:</strong> Generation can take up to 10 minutes. Try "Text Story Only".</div>', unsafe_allow_html=True)
        except requests.exceptions.RequestException as e:
            st.markdown(f'<div class="error-box"><i class="fas fa-times-circle"></i> <strong>ERROR:</strong> {str(e)}<br><br>Make sure backend is running: <code>uvicorn main:app --reload</code></div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <h2 style="margin: 0; font-size: 3rem;"><i class="fas fa-heart"></i> LITTLEHEROES</h2>
    <p style="margin: 1.2rem 0; font-size: 1.4rem;">Making medical journeys easier for children 🌟</p>
    <p style="margin: 0.8rem 0 0 0; font-size: 1rem; opacity: 0.9;">Storybook generation takes 2-3 minutes</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)