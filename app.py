import streamlit as st
from backend import *

st.set_page_config("Healthcare RAG Assistant", "🏥", layout="wide")

# ===== SCROLLING BANNER =====
st.markdown("""
<style>
@keyframes scroll {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

.scrolling-banner {
    background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
    padding: 15px;
    font-size: 22px;
    color: white;
    text-align: center;
    font-weight: bold;
    overflow: hidden;
    border-radius: 10px;
    margin-bottom: 20px;
}

.scroll-text {
    display: inline-block;
    animation: scroll 15s linear infinite;
    white-space: nowrap;
}

.card {
    background: #f9f9f9;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    border-left: 4px solid #2c5364;
}

.success-card {
    background: #d4edda;
    padding: 15px;
    border-radius: 10px;
    border-left: 4px solid #28a745;
    color: #155724;
}

.info-card {
    background: #e7f3ff;
    padding: 15px;
    border-radius: 10px;
    border-left: 4px solid #0066cc;
}

.metric-card {
    background: white;
    padding: 15px;
    border-radius: 8px;
    border: 2px solid #2c5364;
    text-align: center;
}
</style>

<div class="scrolling-banner">
    <span class="scroll-text">🏥 24/7 Healthcare Services Available | 📞 9248000000 | Get Expert Medical Advice | Book Appointments | Order Medicines Online | Emergency for Ambulance - 9345100000 </span>
</div>
""", unsafe_allow_html=True)

# ===== REORDERED TABS =====
tabs = st.tabs(["👨‍⚕️ Appointment", "💊 Medicines", "📦 Orders", "🔬 Diagnosis", "❓ Healthcare Assistant"])

# ===== TAB 1: APPOINTMENT =====
with tabs[0]:
    st.header("👨‍⚕️ Book Appointment with Doctor")
    
    doctors_df = list_doctors()
    
    if doctors_df is None or len(doctors_df) == 0:
        st.error("❌ No doctors found. Please check data folder.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name", placeholder="Enter your full name")
            patient_age = st.number_input("Patient Age", min_value=1, max_value=120, value=30)
            patient_sex = st.selectbox("Patient Sex", ["Male", "Female", "Other"])
            disease = st.text_input("Disease/Condition", placeholder="What is your health concern?")
        
        with col2:
            patient_contact = st.text_input("Patient Contact Number (10 digits)", placeholder="9876543210")
            doctor_options = [f"{row['Doctor_Name']} - {row['Specialization']}" for _, row in doctors_df.iterrows()]
            selected_option = st.selectbox("Select Doctor", doctor_options)
            doctor_name = selected_option.split(" - ")[0]
            appointment_date = st.date_input("Appointment Date")
        
        appointment_time = st.selectbox("Preferred Time", ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"])
        
        doctor_row = doctors_df[doctors_df["Doctor_Name"] == doctor_name].iloc[0]
        
        st.markdown(f"""
        <div class="info-card">
        <b>👨‍⚕️ Doctor Details:</b><br>
        📋 Specialization: {doctor_row['Specialization']}<br>
        📅 Experience: {doctor_row['Experience']} years<br>
        ⏰ Availability: {doctor_row['Availability']}<br>
        📞 Contact: {doctor_row['Phone']}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        if st.button("📅 Book Appointment", use_container_width=True, type="primary"):
            if not patient_name or len(patient_name) < 3:
                st.error("❌ Enter valid patient name")
            elif not patient_contact or len(patient_contact) != 10 or not patient_contact.isdigit():
                st.error("❌ Enter valid 10-digit contact number")
            elif not disease or len(disease) < 3:
                st.error("❌ Describe your condition")
            else:
                success = save_appointment({
                    "Patient_Name": patient_name,
                    "Patient_Age": patient_age,
                    "Patient_Sex": patient_sex,
                    "Patient_Contact": patient_contact,
                    "Disease": disease,
                    "Doctor": doctor_name,
                    "Date": str(appointment_date),
                    "Time": appointment_time
                })
                if success:
                    st.markdown("""
                    <div class="success-card">
                    ✅ <b>Appointment Booked!</b><br>
                    Confirmation details sent to your phone.
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error("❌ Error booking appointment. Check if Appointments.csv exists in data folder.")
        
        st.subheader("🥼 Our Medical Team")
        st.dataframe(doctors_df[["Doctor_Name", "Specialization", "Experience", "Availability"]], use_container_width=True, hide_index=True)


# ===== TAB 2: MEDICINES =====
with tabs[1]:
    st.header("💊 Order Medicines Online")
    
    meds = list_medicines()
    
    if meds is None or len(meds) == 0:
        st.error("❌ No medicines found. Please check data folder.")
    else:
        # Initialize filtered_meds with all medicines
        filtered_meds = meds
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            med_names = filtered_meds["Medicine_Name"].tolist()
            selected_med = st.selectbox("Select Medicine", med_names)
        
        with col2:
            st.write("")
        
        med_row = filtered_meds[filtered_meds["Medicine_Name"] == selected_med].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Category", med_row['Category'])
        with col2:
            st.metric("Dosage", med_row['Dosage'])
        with col3:
            st.metric("Stock", f"{int(med_row['Stock'])} units")
        with col4:
            st.metric("Price/Unit", f"₹{int(med_row['Price'])}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            qty = st.number_input("Quantity", min_value=1, max_value=int(med_row["Stock"]), value=1)
            phone = st.text_input("Phone Number (10 digits)", placeholder="9876543210")
            address = st.text_area("Delivery Address", height=100)
        
        with col2:
            st.subheader("Order Summary")
            total_price = int(med_row['Price']) * qty
            delivery = 50
            grand_total = total_price + delivery
            
            st.markdown(f"""
            <div class="card">
            <b>Medicine:</b> {selected_med}<br>
            <b>Quantity:</b> {qty} units<br>
            <b>Unit Price:</b> ₹{int(med_row['Price'])}<br>
            <b>Subtotal:</b> ₹{total_price}<br>
            <hr>
            <b>Delivery Charges:</b> ₹{delivery}<br>
            <b style='font-size: 20px; color: #d63031;'>Total: ₹{grand_total}</b>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Payment Method")
            payment = st.radio("Select Option", ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery"], horizontal=True)
        
        st.divider()
        
        if st.button("🛒 Place Order", use_container_width=True, type="primary"):
            if not phone or len(phone) != 10 or not phone.isdigit():
                st.error("❌ Enter valid 10-digit phone number")
            elif not address or len(address.strip()) < 10:
                st.error("❌ Enter complete delivery address")
            else:
                success = place_order(phone, address, selected_med, qty, payment)
                if success:
                    st.markdown("""
                    <div class="success-card">
                    ✅ <b>Order Placed Successfully!</b><br>
                    Your medicine will be delivered within 24-48 hours.<br>
                    Confirmation sent to your phone number.
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error("❌ Error placing order. Check if orders.csv exists in data folder.")
        
        st.divider()
        
        st.subheader("🔍 Available Medicines")
        search_query = st.text_input("Enter medicine name or category", placeholder="e.g., Paracetamol, Antibiotic, Pain Relief")
        
        if search_query:
            filtered_meds = meds[
                (meds["Medicine_Name"].str.contains(search_query, case=False, na=False)) |
                (meds["Category"].str.contains(search_query, case=False, na=False))
            ]
            if len(filtered_meds) > 0:
                st.dataframe(filtered_meds[["Medicine_Name", "Category", "Dosage", "Price", "Stock"]], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ No medicines found matching your search.")
        else:
            st.dataframe(meds[["Medicine_Name", "Category", "Dosage", "Price", "Stock"]], use_container_width=True, hide_index=True)


# ===== TAB 3: ORDERS =====
with tabs[2]:
    st.header("📦 Order History")
    
    orders = list_orders()
    
    if orders is None or len(orders) == 0:
        st.info("ℹ️ No orders placed yet. Start ordering medicines!")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", len(orders))
        with col2:
            st.metric("Total Spent", f"₹{orders['Total_Amount'].sum():.2f}")
        with col3:
            st.metric("Latest Status", orders.iloc[-1]['Status'])
        
        st.divider()
        st.dataframe(orders, use_container_width=True, hide_index=True)


# ===== TAB 4: DIAGNOSIS =====
with tabs[3]:
    st.header("🔬 Book Diagnosis Tests")
    
    diagnosis_type = st.selectbox(
        "Select Diagnosis Type",
        ["X-Ray", "MRI Scan", "CT Scan", "Ultrasound", "Blood Test", "ECG"]
    )
    
    doctors_df = list_doctors()
    if len(doctors_df) > 0:
        doctor_options = [f"{row['Doctor_Name']} ({row['Specialization']})" for _, row in doctors_df.iterrows()]
        selected_option = st.selectbox("Select Doctor", doctor_options)
        doctor_name = selected_option.split(" (")[0]
        selected_doctor = doctor_name
    else:
        st.error("❌ No doctors available")
        selected_doctor = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Patient Name", placeholder="Enter your full name", key="diag_name")
        patient_age = st.number_input("Patient Age (Diagnosis)", min_value=1, max_value=120, value=30, key="diag_age")
        patient_contact = st.text_input("Patient Contact Number", placeholder="9876543210", key="diag_contact")
    
    with col2:
        patient_sex = st.selectbox("Patient Sex (Diagnosis)", ["Male", "Female", "Other"], key="diag_sex")
        diagnosis_date = st.date_input("Preferred Test Date")
        test_time = st.selectbox("Preferred Time", ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"])
    
    notes = st.text_area("Medical Notes/Symptoms", placeholder="Describe your symptoms or medical history", height=80)
    
    st.divider()
    
    if st.button("📅 Book Test", use_container_width=True, type="primary"):
        if not patient_name or len(patient_name) < 3:
            st.error("❌ Enter valid patient name")
        elif not patient_contact or len(patient_contact) != 10 or not patient_contact.isdigit():
            st.error("❌ Enter valid 10-digit contact number")
        elif not notes or len(notes) < 5:
            st.error("❌ Provide medical notes/symptoms")
        elif selected_doctor is None:
            st.error("❌ No doctor selected")
        else:
            success = save_diagnosis({
                "Patient_Name": patient_name,
                "Patient_Age": patient_age,
                "Patient_Sex": patient_sex,
                "Patient_Contact": patient_contact,
                "Diagnosis_Type": diagnosis_type,
                "Doctor": selected_doctor,
                "Date": str(diagnosis_date),
                "Time": test_time,
                "Notes": notes
            })
            if success:
                st.markdown("""
                <div class="success-card">
                ✅ <b>Test Booked Successfully!</b><br>
                Your diagnosis appointment has been confirmed.<br>
                Confirmation sent to your phone.
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            else:
                st.error("❌ Error booking test. Check if Diagnosis.csv exists in data folder.")
    
    st.subheader("📊 Recent Diagnosis Bookings")
    diagnosis_list = list_diagnosis()
    if diagnosis_list is not None and len(diagnosis_list) > 0:
        st.dataframe(diagnosis_list, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No diagnosis bookings yet.")


# ===== TAB 5: HEALTHCARE ASSISTANT =====
with tabs[4]:
    st.header("❓ Healthcare Assistant - Ask Questions")
    
    st.info("💡 Ask general healthcare questions. For emergencies, call 911.")
    
    question = st.text_area(
        "Your Question",
        placeholder="E.g., What are terms and conditions for insurance?",
        height=100
    )
    answer = None
    if st.button("🤖 Get Answer", use_container_width=True, type="primary"):
        if not question or len(question) < 5:
            st.error("❌ Please ask a detailed question")
        else:
            with st.spinner("🔍 Getting response from healthcare database..."):
                answer = rag_query_pipeline(question)

    # =================================================
    # ✅ SAFE RENDERING OF answer
    # =================================================
    if answer:
        st.subheader("✅ Answer")
        for line in answer.split("\n"):
            if line.strip():
                st.markdown(f"- {line.replace('•','').strip()}")

    st.subheader("❓ FAQ")
    faqs = {
        "When should I consult a doctor?": "Consult if symptoms persist for 3+ days or are severe.",
        "How to book appointment?": "Use the Appointment tab to select doctor and date.",
        "What payment methods available?": "Credit/Debit Card, UPI, Net Banking, Cash on Delivery.",
        "Medicine delivery time?": "24-48 hours from order confirmation.",
        "What are terms and conditions for insurance?": "Includes coverage details, premiums, deductibles, co-pays, network providers, and more."
    }
    
    for q, a in faqs.items():
        with st.expander(f"❓ {q}"):
            st.write(a)