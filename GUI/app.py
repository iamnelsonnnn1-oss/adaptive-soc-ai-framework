import streamlit as st

st.set_page_config(
    page_title="SECUREX Maintenance",
    page_icon="🛠️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #020202;
        color: #EAEAEA;
        font-family: Arial, sans-serif;
    }
    .wrap {
        min-height: 70vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .card {
        width: 100%;
        max-width: 800px;
        background: rgba(10, 10, 10, 0.92);
        border: 1px solid rgba(0, 245, 255, 0.18);
        border-radius: 12px;
        padding: 40px 32px;
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.08);
        text-align: center;
    }
    .eyebrow {
        color: #00F5FF;
        font-size: 0.8rem;
        letter-spacing: 0.18rem;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: #FFFFFF;
    }
    .body {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #B8B8B8;
        margin-bottom: 24px;
    }
    .badge {
        display: inline-block;
        padding: 10px 16px;
        border: 1px solid #FFBF00;
        border-radius: 999px;
        color: #FFBF00;
        background: rgba(255, 191, 0, 0.08);
        font-size: 0.9rem;
        font-weight: 600;
    }
    .foot {
        margin-top: 24px;
        color: #777;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="wrap">
      <div class="card">
        <div class="eyebrow">SECUREX STATUS</div>
        <div class="title">SecureX is under maintenance</div>
        <div class="body">
          We are currently performing updates and stabilization work.<br>
          The platform will be back online soon.
        </div>
        <div class="badge">Scheduled Maintenance In Progress</div>
        <div class="foot">Thank you for your patience.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
