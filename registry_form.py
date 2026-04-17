import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Registry Enrollment | Alameda County SSA",
    page_icon="📋",
    layout="centered"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
  h1,h2,h3 { font-family: 'IBM Plex Mono', monospace; }
  .cmist-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }
  .section-desc { color: #7a9bb5; font-size: 13px; margin-bottom: 12px; }
  .consent-box {
    background: #0f1923;
    border: 1px solid #2a3f52;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    color: #c0d8eb;
    line-height: 1.7;
    margin-bottom: 16px;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📋 Disaster Evacuation Registry")
st.markdown("**Alameda County Social Services Agency · Adult Protective Services**")
st.info("This form is **voluntary**. Information is shared only with emergency responders during a declared disaster. You may withdraw at any time by contacting your caseworker or calling **(510) 577-1900**.")
st.markdown("---")

# ── Progress indicator ────────────────────────────────────────────────────────
steps = ["Client Info", "C — Communication", "M — Health", "I — Independence", "S — Supervision", "T — Transport", "Consent"]
if "form_step" not in st.session_state:
    st.session_state.form_step = 0

cols = st.columns(len(steps))
for i, (col, step) in enumerate(zip(cols, steps)):
    with col:
        if i < st.session_state.form_step:
            st.markdown(f"<div style='text-align:center;font-size:11px;color:#2ecc71;'>✓</div>", unsafe_allow_html=True)
        elif i == st.session_state.form_step:
            st.markdown(f"<div style='text-align:center;font-size:10px;font-weight:600;color:#1a8cff;border-bottom:2px solid #1a8cff;padding-bottom:2px;'>{step}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:center;font-size:10px;color:#4a6a80;'>{step}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Initialize session state storage ─────────────────────────────────────────
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

def save_and_next(data: dict):
    st.session_state.form_data.update(data)
    st.session_state.form_step += 1
    st.rerun()

def go_back():
    st.session_state.form_step -= 1
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 0 — CLIENT INFO
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.form_step == 0:
    st.markdown("### Client Information")

    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First name *")
    with col2:
        last_name = st.text_input("Last name *")

    col1, col2, col3 = st.columns(3)
    with col1:
        dob = st.date_input("Date of birth *", min_value=date(1920,1,1), max_value=date.today())
    with col2:
        phone = st.text_input("Phone number", placeholder="(510) 000-0000")
    with col3:
        case_id = st.text_input("APS / IHSS Case ID", placeholder="Case ID")

    address = st.text_input("Home address *", placeholder="Street address, city, ZIP",
                            help="Used for parcel-level hazard zone matching — not shared beyond emergency responders")

    col1, col2 = st.columns(2)
    with col1:
        ec_name = st.text_input("Emergency contact name")
    with col2:
        ec_phone = st.text_input("Emergency contact phone", placeholder="(510) 000-0000")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Next →", type="primary", use_container_width=True):
        if not first_name or not last_name or not address:
            st.error("Please fill in all required fields (marked with *).")
        else:
            save_and_next({
                "first_name": first_name, "last_name": last_name,
                "dob": str(dob), "phone": phone, "case_id": case_id,
                "address": address, "ec_name": ec_name, "ec_phone": ec_phone
            })

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — C: COMMUNICATION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 1:
    st.markdown('<span class="cmist-badge" style="background:#1a3a5c;color:#77bbff;">C — COMMUNICATION</span>', unsafe_allow_html=True)
    st.markdown("### Communication needs")
    st.markdown('<p class="section-desc">How should emergency alerts and responders reach you?</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Primary language", [
            "English","Spanish","Cantonese","Mandarin",
            "Vietnamese","Tagalog","Punjabi","Arabic","Other"
        ])
    with col2:
        contact_method = st.selectbox("Preferred contact method", [
            "Phone call","Text message (SMS)","In-person visit",
            "TTY / relay service","Through caregiver"
        ])

    st.markdown("**Communication accommodations** (select all that apply)")
    col1, col2, col3 = st.columns(3)
    with col1:
        large_print = st.checkbox("Large print materials")
        hearing = st.checkbox("Hearing impairment")
    with col2:
        vision = st.checkbox("Vision impairment")
        interpreter = st.checkbox("Interpreter needed")
    with col3:
        tty = st.checkbox("TTY device")
        cognitive_comm = st.checkbox("Cognitive support")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True): go_back()
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            save_and_next({
                "language": language, "contact_method": contact_method,
                "large_print": large_print, "hearing_impairment": hearing,
                "vision_impairment": vision, "interpreter": interpreter,
                "tty": tty, "cognitive_comm": cognitive_comm
            })

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — M: MAINTAINING HEALTH
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 2:
    st.markdown('<span class="cmist-badge" style="background:#3a0a0a;color:#ff7777;">M — MAINTAINING HEALTH</span>', unsafe_allow_html=True)
    st.markdown("### Medical and health needs")
    st.markdown('<p class="section-desc">Equipment, medications, or conditions requiring special handling during evacuation</p>', unsafe_allow_html=True)

    st.markdown("**Power-dependent equipment** (select all that apply)")
    col1, col2, col3 = st.columns(3)
    with col1:
        oxygen = st.checkbox("Home oxygen / ventilator")
        dialysis = st.checkbox("Dialysis equipment")
    with col2:
        elec_chair = st.checkbox("Electric wheelchair / scooter")
        feeding_tube = st.checkbox("Feeding tube / IV pump")
    with col3:
        refrig_meds = st.checkbox("Refrigerated medications")
        stairlift = st.checkbox("Stairlift / home lift")

    col1, col2 = st.columns(2)
    with col1:
        medications = st.text_area("Critical medications",
            placeholder="List medications requiring refrigeration or regular dosing during evacuation")
    with col2:
        conditions = st.text_area("Medical conditions relevant to evacuation",
            placeholder="e.g. severe asthma, dialysis 3x/week, insulin-dependent diabetes")

    col1, col2 = st.columns(2)
    with col1:
        backup_power = st.selectbox("Backup power source", [
            "None",
            "Generator (own)",
            "Battery backup",
            "None — power-dependent equipment at risk during PSPS"
        ])
    with col2:
        hospital = st.text_input("Nearest hospital / dialysis center", placeholder="Facility name and city")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True): go_back()
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            save_and_next({
                "oxygen": oxygen, "dialysis": dialysis, "elec_chair": elec_chair,
                "feeding_tube": feeding_tube, "refrig_meds": refrig_meds,
                "stairlift": stairlift, "medications": medications,
                "conditions": conditions, "backup_power": backup_power,
                "hospital": hospital
            })

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — I: INDEPENDENCE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 3:
    st.markdown('<span class="cmist-badge" style="background:#0a2a0a;color:#77dd77;">I — INDEPENDENCE</span>', unsafe_allow_html=True)
    st.markdown("### Functional independence and mobility aids")
    st.markdown('<p class="section-desc">What assistive equipment must travel with you?</p>', unsafe_allow_html=True)

    st.markdown("**Assistive devices** (select all that apply)")
    col1, col2, col3 = st.columns(3)
    with col1:
        wheelchair_m = st.checkbox("Wheelchair (manual)")
        walker = st.checkbox("Walker / rollator")
        prosthetic = st.checkbox("Prosthetic limb")
    with col2:
        wheelchair_e = st.checkbox("Wheelchair (electric)")
        cane = st.checkbox("Cane")
        hearing_aid = st.checkbox("Hearing aid")
    with col3:
        service_animal = st.checkbox("Service animal")
        comm_device = st.checkbox("Communication device")
        no_device = st.checkbox("None")

    col1, col2 = st.columns(2)
    with col1:
        self_evac = st.selectbox("Self-evacuation ability", [
            "Can evacuate independently with notice",
            "Can evacuate with minimal assistance",
            "Requires full physical assistance",
            "Requires ambulance-level transport",
            "Bedridden — cannot self-mobilize"
        ])
    with col2:
        floor_level = st.selectbox("Floor level of residence", [
            "Ground floor",
            "1st floor (elevator access)",
            "1st floor (stairs only)",
            "2nd+ floor (elevator access)",
            "2nd+ floor (stairs only)"
        ])

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True): go_back()
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            save_and_next({
                "wheelchair_manual": wheelchair_m, "wheelchair_electric": wheelchair_e,
                "walker": walker, "cane": cane, "prosthetic": prosthetic,
                "service_animal": service_animal, "hearing_aid": hearing_aid,
                "comm_device": comm_device, "no_device": no_device,
                "self_evac": self_evac, "floor_level": floor_level
            })

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — S: SUPERVISION & SAFETY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 4:
    st.markdown('<span class="cmist-badge" style="background:#2a1a00;color:#ffcc77;">S — SUPERVISION & SAFETY</span>', unsafe_allow_html=True)
    st.markdown("### Supervision and support needs")
    st.markdown('<p class="section-desc">Who else must be contacted or present during evacuation?</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        living_situation = st.selectbox("Living situation", [
            "Lives alone",
            "With spouse / partner",
            "With family member",
            "With paid caregiver (IHSS)",
            "Assisted living / board & care"
        ])
    with col2:
        ihss_provider = st.text_input("IHSS provider name (if applicable)",
            help="Provider will be notified during evacuation activation")

    st.markdown("**Cognitive / behavioral needs** (select all that apply)")
    col1, col2, col3 = st.columns(3)
    with col1:
        dementia = st.checkbox("Dementia / Alzheimer's")
        intellectual = st.checkbox("Intellectual disability")
    with col2:
        anxiety = st.checkbox("Severe anxiety / PTSD")
        resist = st.checkbox("May resist evacuation")
    with col3:
        nonverbal = st.checkbox("Non-verbal communication")
        no_cognitive = st.checkbox("None")

    safety_notes = st.text_area("Additional safety notes for responders",
        placeholder="e.g. Client has a dog and will refuse to leave without it. Caregiver arrives at 8am daily. Do not separate from oxygen tank.",
        height=100)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True): go_back()
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            save_and_next({
                "living_situation": living_situation, "ihss_provider": ihss_provider,
                "dementia": dementia, "intellectual": intellectual,
                "anxiety": anxiety, "resist_evac": resist,
                "nonverbal": nonverbal, "no_cognitive": no_cognitive,
                "safety_notes": safety_notes
            })

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — T: TRANSPORTATION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 5:
    st.markdown('<span class="cmist-badge" style="background:#1a0a2a;color:#bb88ff;">T — TRANSPORTATION</span>', unsafe_allow_html=True)
    st.markdown("### Transportation needs")
    st.markdown('<p class="section-desc">How will you get out — and what do you need?</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        vehicle_status = st.selectbox("Vehicle ownership", [
            "Yes — can self-evacuate by car",
            "Yes — but cannot drive (medical)",
            "No vehicle"
        ])
    with col2:
        transport_type = st.selectbox("Transport type required", [
            "Standard vehicle",
            "Wheelchair-accessible van",
            "Stretcher / medical transport",
            "Ambulance",
            "Can use public transit if accessible"
        ])

    st.markdown("**Transport barriers** (select all that apply)")
    col1, col2, col3 = st.columns(3)
    with col1:
        no_vehicle = st.checkbox("No vehicle")
        no_stairs = st.checkbox("Cannot use stairs")
    with col2:
        oxygen_transit = st.checkbox("Requires oxygen during transit")
        large_equip = st.checkbox("Large medical equipment")
    with col3:
        animal_transit = st.checkbox("Service animal must accompany")
        escort = st.checkbox("Requires escort / companion")

    col1, col2 = st.columns(2)
    with col1:
        shelter_pref = st.text_input("Preferred evacuation shelter", placeholder="Shelter name or area (if known)")
    with col2:
        alt_dest = st.text_input("Alternate destination (if refusing shelter)", placeholder="Family member address or other")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True): go_back()
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            save_and_next({
                "vehicle_status": vehicle_status, "transport_type": transport_type,
                "no_vehicle": no_vehicle, "no_stairs": no_stairs,
                "oxygen_transit": oxygen_transit, "large_equip": large_equip,
                "animal_transit": animal_transit, "escort": escort,
                "shelter_pref": shelter_pref, "alt_dest": alt_dest
            })

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — CONSENT & SUBMIT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 6:
    st.markdown("### Voluntary enrollment and data consent")

    st.markdown("""
    <div class="consent-box">
    By signing below, I voluntarily enroll in the Alameda County SSA Disaster Evacuation Registry. I understand that:<br><br>
    (1) My information will be stored securely and shared <strong>only</strong> with authorized emergency responders during a declared disaster;<br>
    (2) Enrollment does not guarantee evacuation but places me on a <strong>priority outreach list</strong>;<br>
    (3) I may <strong>withdraw from this registry at any time</strong> by contacting my APS caseworker or calling (510) 577-1900;<br>
    (4) My registry information will be reviewed and updated <strong>annually</strong> by my caseworker.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        signature = st.text_input("Client signature * (type full name)", placeholder="Full legal name")
    with col2:
        sig_date = st.date_input("Date *", value=date.today())
    with col3:
        signer_rel = st.selectbox("Relationship (if signing on behalf)", [
            "Client signing directly",
            "Authorized representative",
            "Legal guardian",
            "IHSS provider",
            "APS caseworker (verbal consent documented)"
        ])

    caseworker = st.text_input("Caseworker name and ID completing this intake")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True): go_back()
    with col2:
        if st.button("✓ Submit Enrollment", type="primary", use_container_width=True):
            if not signature:
                st.error("Please provide a signature to complete enrollment.")
            else:
                st.session_state.form_data.update({
                    "signature": signature, "sig_date": str(sig_date),
                    "signer_rel": signer_rel, "caseworker": caseworker,
                    "enrolled": True
                })
                st.session_state.form_step = 7
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — CONFIRMATION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.form_step == 7:
    st.success("## Enrollment Complete")
    data = st.session_state.form_data
    name = f"{data.get('first_name','')} {data.get('last_name','')}".strip()

    st.markdown(f"""
    **{name}** has been successfully enrolled in the Alameda County SSA Disaster Evacuation Registry.

    A confirmation will be sent to the caseworker on file. The client profile is now active and will be shared with Alameda County OES and the Care & Shelter Branch during any declared disaster.
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Client", name)
    col2.metric("Address on file", data.get("address","—")[:25] + "..." if len(data.get("address","")) > 25 else data.get("address","—"))
    col3.metric("Transport needed", data.get("transport_type","—"))

    st.markdown("---")
    st.markdown("**Registry profile summary**")

    summary_data = {
        "Field": [
            "Primary language", "Contact method", "Living situation",
            "Self-evacuation ability", "Transport type", "Power-dependent equipment",
            "Service animal", "IHSS provider"
        ],
        "Value": [
            data.get("language","—"), data.get("contact_method","—"),
            data.get("living_situation","—"), data.get("self_evac","—"),
            data.get("transport_type","—"),
            "Yes" if any([data.get("oxygen"), data.get("dialysis"), data.get("refrig_meds"), data.get("feeding_tube")]) else "No",
            "Yes" if data.get("service_animal") else "No",
            data.get("ihss_provider","None listed")
        ]
    }
    st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Enroll another client", use_container_width=True):
        st.session_state.form_step = 0
        st.session_state.form_data = {}
        st.rerun()
