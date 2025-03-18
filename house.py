import streamlit as st
import pandas as pd
import joblib
import base64
from fpdf import FPDF

# Load the trained model
model_path = "house_price_model.pkl"
try:
    model = joblib.load(model_path)
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# Convert Image to Base64 for Background
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode()
    return base64_string

background_image_path = "C:/Users/91910/Downloads/Beautiful-luxury-home-exterior-iStock-1054759884.jpg"
base64_image = get_base64_image(background_image_path)

# Apply Background Image and Custom Styles
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{base64_image}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: red;
    }}
    .overlay {{
        background: rgba(255, 255, 255, 0.7);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
    }}
    .cool-button {{
        display: flex;
        justify-content: center;
        align-items: center;
        background: linear-gradient(90deg, #6a11cb, #2575fc);
        border: none;
        color: white;
        padding: 15px 35px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 30px;
        cursor: pointer;
        transition: 0.3s ease-in-out;
        box-shadow: 0px 4px 15px rgba(38, 50, 56, 0.5);
    }}
    .cool-button:hover {{
        background: linear-gradient(90deg, #2575fc, #6a11cb);
        transform: scale(1.1);
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; color: red;'>&#127969; House Price Prediction</h1>", unsafe_allow_html=True)

# Customer Details
st.sidebar.header("Customer Details")
customer_name = st.sidebar.text_input("Customer Name")
customer_id = st.sidebar.text_input("Customer ID")
customer_email = st.sidebar.text_input("Customer Email")

# Predict Button at the Top
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Predict Price", key="predict", help="Click to predict the house price", use_container_width=True):
        st.session_state["predict_clicked"] = True

st.markdown("<h3 style='text-align: center; color: red;'>Enter the house details below to get an accurate price estimation.</h3>", unsafe_allow_html=True)

# Dropdown Options According to Model
lot_config_options = ["Inside", "Corner", "CulDSac", "FR2", "FR3"]
bldg_type_options = ["1Fam", "2fmCon", "Duplex", "TwnhsE", "TwnhsI"]
ms_zoning_options = ["RL", "RM", "FV", "RH", "C (all)"]
exterior_options = ["VinylSd", "MetalSd", "Wd Sdng", "HdBoard", "BrkFace"]

# Input Fields According to Model Features
st.sidebar.header("Enter House Features")

input_data = {
    "LotConfig": st.sidebar.selectbox("Lot Configuration", lot_config_options),
    "BldgType": st.sidebar.selectbox("Building Type", bldg_type_options),
    "TotalBsmtSF": st.sidebar.number_input("Total Basement Area (sq ft)", min_value=0, step=1),
    "MSZoning": st.sidebar.selectbox("MS Zoning", ms_zoning_options),
    "Exterior1st": st.sidebar.selectbox("Exterior Covering", exterior_options),
    "YearBuilt": st.sidebar.number_input("Year Built", min_value=1800, step=1),
    "OverallCond": st.sidebar.number_input("Overall Condition", min_value=1, max_value=10, step=1),
    "LotArea": st.sidebar.number_input("Lot Area (sq ft)", min_value=0, step=1),
    "MSSubClass": st.sidebar.number_input("MS SubClass", min_value=0, step=1),
    "YearRemodAdd": st.sidebar.number_input("Year Remodeled", min_value=1800, step=1),
    "BsmtFinSF2": st.sidebar.number_input("Second Basement Finished Area (sq ft)", min_value=0, step=1)
}

# Convert to DataFrame
df_input = pd.DataFrame([input_data])

# Prediction Function
def predict_price(features):
    try:
        prediction = model.predict(features)[0]
        return prediction
    except Exception as e:
        return f"Prediction error: {e}"

# Generate PDF Report
def generate_pdf(customer_name, customer_id, customer_email, predicted_price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="House Price Prediction Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"Customer ID: {customer_id}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Email: {customer_email}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Predicted House Price: ${predicted_price:,.2f}", ln=True)
    
    pdf_file_path = "house_price_report.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Show Prediction if Button is Clicked
if "predict_clicked" in st.session_state:
    predicted_price = predict_price(df_input)
    if isinstance(predicted_price, str):  # If an error occurred
        st.error(predicted_price)
    else:
        st.markdown(f"<h2 style='text-align: center; color: red;'>Estimated House Price: ${predicted_price:,.2f}</h2>", unsafe_allow_html=True)
        pdf_path = generate_pdf(customer_name, customer_id, customer_email, predicted_price)
        with open(pdf_path, "rb") as file:
            pdf_bytes = file.read()
            st.download_button(label="Download PDF Report", data=pdf_bytes, file_name="House_Price_Report.pdf", mime="application/pdf")
