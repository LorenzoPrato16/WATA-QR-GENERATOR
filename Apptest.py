import streamlit as st
import qrcode
from urllib.parse import quote
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Générateur de QR code", page_icon="WATA-logo-400x400px.ico", layout="centered")
st.image("WATA_logo_150px.png", width=200)
st.title("Générateur de QR code - SAV WATALUX")
st.text("Générez le QR code à afficher sur le dispositif en sélectionnant le modèle et le numéro de série.")


phone_number = "393663489952"

# User inputs
model = st.selectbox(
    "Modèle du dispositif",
    [
        "Mini-WATA (Appareil)",
        "Mini-WATA (Alimentation Solaire)",
        "WATA-Standard (Appareil)",
        "WATA-Standard (Alimentation Secteur)",
        "WATA-Standard (Alimentation Solaire)",
        "WATA-Plus (Appareil)",
        "WATA-Plus (Alimentation Secteur)",
        "WATA-Plus (Alimentation Solaire)",
        "WATA-Plus (Boîtier Solaire)",
        "Maxi-WATA (Appareil)",
        "Maxi-WATA (Alimentation Secteur)",
        "WataTest",
        "WataBlue"
    ]
)

special_models = ["WataTest", "WataBlue"]

if model in special_models:
    production_date = st.date_input("Date de production")
    expiry_date = st.date_input("Date de péremption")
else:
    serial = st.text_input("Numéro de série", value="0000")

if st.button("Générer le QR code"):
    if model in special_models:
        if not model.strip():
            st.error("Veuillez sélectionner un modèle.")
        else:
            msg = (
                f"SUPPORT REQUEST\n"
                f"Model: {model}\n"
                f"Production date: {production_date.strftime('%d/%m/%Y')}\n"
                f"Expiry date: {expiry_date.strftime('%d/%m/%Y')}"
            )

            encoded_message = quote(msg)
            whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(whatsapp_link)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white").get_image().convert("RGB")
            # Create canvas bigger than QR
            width, height = img.size
            new_img = Image.new("RGB", (width, height + 60), "white")

            # Paste QR code
            new_img.paste(img, (0, 60))

            # Add text
            draw = ImageDraw.Draw(new_img)
            text = f"{model} - Prd:{production_date.strftime('%d/%m/%Y')} Exp:{expiry_date.strftime('%d/%m/%Y')}"

            draw.text((10, 20), text, fill="black", fontsize=14)

            img = new_img



            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            st.success("QR code généré avec succès.")
            st.image(buffer, caption="Aperçu du QR code")
            st.text_area("Message généré", msg, height=120)
            st.text_area("Lien WhatsApp", whatsapp_link, height=100)

            st.download_button(
                label="Télécharger le QR code",
                data=buffer,
                file_name=f"qr_{model}_{production_date}_{expiry_date}.png",
                mime="image/png"
            )

    else:
        if not model.strip() or not serial.strip():
            st.error("Veuillez sélectionner le modèle et saisir le numéro de série.")
        else:
            msg = f"SUPPORT REQUEST\nModel: {model}\nSerial: {serial}"

            encoded_message = quote(msg)
            whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(whatsapp_link)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white").get_image().convert("RGB")


            # Create canvas bigger than QR
            width, height = img.size
            new_img = Image.new("RGB", (width, height + 60), "white")

            # Paste QR code
            new_img.paste(img, (0, 60))

            # Add text
            draw = ImageDraw.Draw(new_img)
            text = f"{model} - NS:{serial}"

            draw.text((10, 30), text, fill="black")

            img = new_img




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