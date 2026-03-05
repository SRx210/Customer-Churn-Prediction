import streamlit as st
import requests
import json

st.set_page_config(
    page_title="ChurnSight · Prediction Dashboard",
    page_icon="",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0b0f1a;
    color: #e8eaf6;
}

.hero {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 50%, #0f2232 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.3rem 0;
}
.hero p {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
    font-family: 'DM Mono', monospace;
}

.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 0.75rem;
}

.result-card {
    background: #111827;
    border: 1px solid #1f2d3d;
    border-radius: 14px;
    padding: 1.6rem;
    text-align: center;
}
.result-card.churn { border-color: #f87171; }
.result-card.no-churn { border-color: #34d399; }

.result-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.4rem;
}
.result-verdict {
    font-size: 2.5rem;
    font-weight: 800;
}
.result-verdict.churn { color: #f87171; }
.result-verdict.no-churn { color: #34d399; }

.prob-bar-wrap { margin-top: 1rem; }
.prob-bar-bg {
    background: #1e293b;
    border-radius: 999px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin-top: 0.3rem;
}
.prob-bar-fill {
    height: 8px;
    border-radius: 999px;
}

.strategy-section {
    margin-top: 1.5rem;
}
.strategy-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.strategy-header.critical { color: #f87171; }
.strategy-header.high { color: #fb923c; }
.strategy-header.medium { color: #facc15; }
.strategy-header.low { color: #34d399; }

.risk-badge {
    display: inline-block;
    padding: 0.25rem 0.9rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 1rem;
    font-family: 'DM Mono', monospace;
}
.risk-badge.critical { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid #f87171; }
.risk-badge.high     { background: rgba(251,146,60,0.15);  color: #fb923c; border: 1px solid #fb923c; }
.risk-badge.medium   { background: rgba(250,204,21,0.15);  color: #facc15; border: 1px solid #facc15; }
.risk-badge.low      { background: rgba(52,211,153,0.15);  color: #34d399; border: 1px solid #34d399; }

.strategy-card {
    background: #111827;
    border: 1px solid #1f2d3d;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.strategy-card:hover { border-color: #38bdf8; }

.strategy-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.2rem;
}
.strategy-desc {
    font-size: 0.75rem;
    color: #64748b;
    font-family: 'DM Mono', monospace;
    line-height: 1.5;
}
.strategy-tag {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    color: #38bdf8;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 0.1rem 0.45rem;
    text-transform: uppercase;
    margin-top: 0.35rem;
    font-family: 'DM Mono', monospace;
}

section[data-testid="stSidebar"] {
    background-color: #0d1421 !important;
    border-right: 1px solid #1e3a5f;
}

label { color: #94a3b8 !important; font-size: 0.85rem !important; }

div.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.65rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.85; }

hr { border-color: #1e293b; }
</style>
""", unsafe_allow_html=True)


def get_retention_strategies(prob_churn: float, customer: dict) -> dict:
    if prob_churn >= 0.75:
        risk_level = "critical"
        risk_label = "Critical Risk"
    elif prob_churn >= 0.50:
        risk_level = "high"
        risk_label = "High Risk"
    elif prob_churn >= 0.25:
        risk_level = "medium"
        risk_label = "Medium Risk"
    else:
        risk_level = "low"
        risk_label = "Low Risk"

    strategies = []

    if customer.get("contract") == "Month-to-month":
        strategies.append({
            "title": "Upgrade to Annual Contract",
            "desc": "Offer 2 months free if customer switches to a 1-year or 2-year plan — locks in loyalty and reduces monthly uncertainty.",
            "tag": "contract upgrade"
        })

    tenure = customer.get("tenure", 12)
    if tenure < 12:
        strategies.append({
            "title": "New Customer Loyalty Bonus",
            "desc": "Award 10 GB free data or 1 month bill credit to reward early commitment and build switching costs.",
            "tag": "early loyalty"
        })
    elif tenure >= 24:
        strategies.append({
            "title": "Long-Term Customer VIP Reward",
            "desc": "Recognise loyalty with a free device protection upgrade or exclusive VIP support tier at no extra cost.",
            "tag": "vip retention"
        })

    if customer.get("internet_service") in ["Fiber optic", "DSL"]:
        if customer.get("online_security") != "Yes":
            strategies.append({
                "title": "Free Online Security Trial — 3 Months",
                "desc": "Activate complimentary Online Security add-on for 3 months. Customers using bundles churn 30% less.",
                "tag": "bundle add-on"
            })
        if customer.get("tech_support") != "Yes":
            strategies.append({
                "title": "Priority Tech Support Upgrade",
                "desc": "Offer free upgrade to priority tech support for 6 months — reduces frustration-driven churn.",
                "tag": "service upgrade"
            })

    if customer.get("payment_method") in ["Electronic check", "Mailed check"]:
        strategies.append({
            "title": "Auto-Pay Discount — Save 5%",
            "desc": "Incentivise switch to automatic UPI/card payment with 5% monthly discount. Reduces involuntary churn from missed payments.",
            "tag": "billing"
        })

    monthly = customer.get("monthly_charges", 65)
    if monthly > 80:
        strategies.append({
            "title": "Personalised Rate Review Call",
            "desc": "Proactively offer a bill review call — propose a tailored bundle that reduces their monthly charge by 10-15%.",
            "tag": "price sensitivity"
        })

    if customer.get("streaming_tv") == "Yes" or customer.get("streaming_movies") == "Yes":
        strategies.append({
            "title": "Extended Streaming Pack Validity",
            "desc": "Extend current streaming validity by 30 days free, or offer a discounted upgrade to the premium unlimited stream tier.",
            "tag": "content offer"
        })

    if customer.get("phone_service") == "No" or customer.get("multiple_lines") == "No":
        strategies.append({
            "title": "Add a Voice Line — First Month Free",
            "desc": "Introduce bundled voice plan with first month waived. Bundled customers are significantly less likely to leave.",
            "tag": "cross-sell"
        })

    if customer.get("senior") == 1:
        strategies.append({
            "title": "Senior Care Plan — Dedicated Support Line",
            "desc": "Offer a dedicated senior helpline and simplified services summary to improve experience and reduce churn due to service confusion.",
            "tag": "senior plan"
        })

    if prob_churn >= 0.50:
        strategies.append({
            "title": "Free 10 GB Data Bonus — 2 Weeks",
            "desc": "Immediate high-value perk: top up their account with 10 GB free data valid for 2 weeks to re-engage and show goodwill.",
            "tag": "instant offer"
        })
        strategies.append({
            "title": "Proactive Retention Call",
            "desc": "Flag for outbound call from a retention specialist within 48 hours. Personal outreach is the single highest-converting retention tactic.",
            "tag": "outreach"
        })

    if prob_churn < 0.25:
        strategies = [
            {
                "title": "Reward Points Programme Enrolment",
                "desc": "Enrol customer in loyalty rewards programme to strengthen relationship and increase switching costs passively.",
                "tag": "engagement"
            },
            {
                "title": "Referral Incentive Offer",
                "desc": "Invite customer to refer a friend for mutual recharge credits — leverages satisfaction to drive acquisition at low cost.",
                "tag": "referral"
            },
            {
                "title": "Renewal Reminder with Early-Bird Discount",
                "desc": "Send proactive renewal reminder 60 days before contract end with an early-bird 10% discount to lock in another term.",
                "tag": "renewal"
            },
        ]

    return {"risk_level": risk_level, "risk_label": risk_label, "strategies": strategies}


def render_strategies(prob_churn: float, customer: dict):
    data = get_retention_strategies(prob_churn, customer)
    risk_level = data["risk_level"]
    risk_label = data["risk_label"]
    strategies = data["strategies"]

    st.markdown(f"""
    <div class="strategy-section">
        <div class="strategy-header {risk_level}">Retention Strategies</div>
        <div class="risk-badge {risk_level}">{risk_label} · {prob_churn:.0%} churn probability</div>
    </div>
    """, unsafe_allow_html=True)

    for s in strategies:
        st.markdown(f"""
        <div class="strategy-card">
            <div class="strategy-title">{s['title']}</div>
            <div class="strategy-desc">{s['desc']}</div>
            <div class="strategy-tag">{s['tag']}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>ChurnSight</h1>
    <p>customer churn prediction dashboard · powered by XGBoost</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="section-label">API Config</div>', unsafe_allow_html=True)
    api_url = st.text_input("Flask API URL", value="http://localhost:5000", help="Base URL of your running Flask server")

    st.markdown("---")
    st.markdown('<div class="section-label">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#64748b; font-size:0.82rem; font-family:'DM Mono',monospace; line-height:1.6;">
    Fill in the customer profile on the right, then click <strong style="color:#38bdf8;">Predict Churn</strong>
    to send the data to the Flask model API and see the result.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-label">Server Status</div>', unsafe_allow_html=True)
    if st.button("Check Health"):
        try:
            r = requests.get(f"{api_url}/health", timeout=4)
            data = r.json()
            if data.get("model_loaded"):
                st.success("API online · model loaded")
            else:
                st.warning("API online · model NOT loaded")
        except Exception as e:
            st.error(f"Cannot reach API\n{e}")

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<div class="section-label">Customer Profile</div>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with r1c2:
        senior = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    with r1c3:
        partner = st.selectbox("Partner", ["Yes", "No"])

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        dependents = st.selectbox("Dependents", ["Yes", "No"])
    with r2c2:
        tenure = st.number_input("Tenure (months)", min_value=0, max_value=72, value=12)
    with r2c3:
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])

    st.markdown("---")
    st.markdown('<div class="section-label">Services</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
    with s2:
        internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
    with s3:
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])

    s4, s5, s6 = st.columns(3)
    with s4:
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
    with s5:
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
    with s6:
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])

    st.markdown("---")
    st.markdown('<div class="section-label">Billing</div>', unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)
    with b1:
        paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
    with b2:
        payment_method = st.selectbox("Payment Method", [
            "Bank transfer (automatic)",
            "Credit card (automatic)",
            "Electronic check",
            "Mailed check"
        ])
    with b3:
        pass

    bc1, bc2 = st.columns(2)
    with bc1:
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=200.0, value=65.0, step=0.5)
    with bc2:
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=780.0, step=1.0)

with col_right:
    st.markdown('<div class="section-label">Prediction</div>', unsafe_allow_html=True)

    predict_btn = st.button("Predict Churn")

    if predict_btn:
        payload = {
            "gender": gender,
            "SeniorCitizen": senior,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": int(tenure),
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless,
            "PaymentMethod": payment_method,
            "MonthlyCharges": float(monthly_charges),
            "TotalCharges": float(total_charges),
        }

        with st.spinner("Sending to Model API..."):
            try:
                response = requests.post(
                    f"{api_url}/predict",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                response.raise_for_status()
                result_data = response.json()
                result = result_data["results"][0]

                pred = result["prediction"]
                status = result["churn_status"]
                prob_churn = result["probability_churn"]
                prob_no_churn = result["probability_no_churn"]

                card_class = "churn" if pred == 1 else "no-churn"
                verdict_label = "WILL CHURN" if pred == 1 else "RETAINED"

                st.markdown(f"""
                <div class="result-card {card_class}">
                    <div class="result-label">Prediction</div>
                    <div class="result-verdict {card_class}">{verdict_label}</div>
                    <div class="prob-bar-wrap">
                        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#64748b;font-family:'DM Mono',monospace;">
                            <span>Churn risk</span><span>{prob_churn:.1%}</span>
                        </div>
                        <div class="prob-bar-bg">
                            <div class="prob-bar-fill" style="width:{prob_churn*100:.1f}%;
                            background:{'#f87171' if pred==1 else '#34d399'};"></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#64748b;font-family:'DM Mono',monospace;margin-top:0.6rem;">
                            <span>Retention probability</span><span>{prob_no_churn:.1%}</span>
                        </div>
                        <div class="prob-bar-bg">
                            <div class="prob-bar-fill" style="width:{prob_no_churn*100:.1f}%;background:#34d399;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                customer_context = {
                    "contract": contract,
                    "tenure": int(tenure),
                    "internet_service": internet_service,
                    "online_security": online_security,
                    "tech_support": tech_support,
                    "payment_method": payment_method,
                    "monthly_charges": float(monthly_charges),
                    "streaming_tv": streaming_tv,
                    "streaming_movies": streaming_movies,
                    "phone_service": phone_service,
                    "multiple_lines": multiple_lines,
                    "senior": senior,
                }
                render_strategies(prob_churn, customer_context)

                with st.expander("Raw API response"):
                    st.json(result_data)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the Flask API. Make sure it's running.")
            except requests.exceptions.HTTPError as e:
                st.error(f"API error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

    else:
        st.markdown("""
        <div style="background:#111827;border:1px dashed #1e3a5f;border-radius:14px;
        padding:3rem 1.5rem;text-align:center;color:#334155;">
            <div style="font-family:'DM Mono',monospace;font-size:0.8rem;letter-spacing:1px;">
                Fill in the customer profile<br>and click <strong style="color:#38bdf8;">Predict Churn</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)