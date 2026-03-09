import streamlit as st
import qrcode
from urllib.parse import quote
from io import BytesIO

st.set_page_config(page_title="Générateur de QR code", page_icon=" 📱")

st.title("Générateur de QR code - SAV WATALUX")
st.text("Générez le QR code à afficher sur le dispositif en sélectionnant le modèle et le numéro de série.")
st.image("WATA_logo_150px.png", width=200)

# Fixed WhatsApp number
phone_number = "393663489952"

# User inputs
model = st.selectbox(
    "Modèle du dispositif",
    ["Mini-WATA", "WATA-Standard", "WATA-Plus", "Maxi-WATA", "WataTest", "WataStab","WataBlue"]
)
serial = st.text_input("Numéro de série", value="1234")

if st.button("Générer le QR code"):
    if not model.strip() or not serial.strip():
        st.error("Veuillez sélectionner le modèle et saisir le numéro de série.")
    else:
        # Message
        msg = f"SUPPORT REQUEST\nModel: {model}\nSerial: {serial}"

        # Encode message
        encoded_message = quote(msg)

        # Build WhatsApp link
        whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )
        qr.add_data(whatsapp_link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save image in memory for display/download
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        st.success("QR code généré avec succès.")
        st.image(buffer, caption="Aperçu du QR code")

        st.text_area("Message généré", msg, height=100)
        st.text_area("Lien WhatsApp", whatsapp_link, height=100)

        st.download_button(
            label="Télécharger le QR code",
            data=buffer,
            file_name=f"qr_{model}_{serial}.png",
            mime="image/png"
        )