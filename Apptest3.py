import streamlit as st
import qrcode
from urllib.parse import quote
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os

st.set_page_config(page_title="Générateur de QR code", page_icon="WATA-logo-400x400px.ico", layout="centered")
st.image("WATA_logo_150px.png", width=200)
st.title("Générateur de QR code - SAV WATALUX")
st.text("Générez le QR code à afficher sur le dispositif en sélectionnant le modèle et le numéro de série.")

phone_number = "15551384702"

model = st.selectbox(
    "Modèle du dispositif",
    [
        "Mini-WATA",
        "WATA-Standard",
        "WATA-Plus",
        "Maxi-WATA",
        "WataTest",
        "WataBlue"
    ]
)

kits = ["WataTest", "WataBlue"]


def create_qr_image(model, serial, phone_number):
    msg = f"SUPPORT REQUEST\nModel: {model}\nSerial: {serial}"
    encoded_message = quote(msg)
    whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(whatsapp_link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").get_image().convert("RGB")

    width, height = img.size
    top_margin = 80
    new_img = Image.new("RGB", (width, height + top_margin), "white")
    new_img.paste(img, (0, top_margin))

    draw = ImageDraw.Draw(new_img)

    font = ImageFont.truetype("DejaVuSans.ttf", 20)

    text = f"{model}\nSerial Number:{serial}"

    draw.text((40, 30), text, fill="black", font=font)

    return new_img, msg, whatsapp_link


if model in kits:
    production_date = st.date_input("Date de production")
    expiry_date = st.date_input("Date de péremption")

    if st.button("Générer le QR code"):
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

        width, height = img.size
        top_margin = 80
        new_img = Image.new("RGB", (width, height + top_margin), "white")
        new_img.paste(img, (0, top_margin))

        draw = ImageDraw.Draw(new_img)

        
        font = ImageFont.truetype("DejaVuSans.ttf", 20)

        text = f"{model}\nPrd:{production_date.strftime('%d/%m/%Y')} Exp:{expiry_date.strftime('%d/%m/%Y')}"
       
        draw.text((40, 30), text, fill="black", font=font)

        buffer = BytesIO()
        new_img.save(buffer, format="PNG")
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
    multiple = st.checkbox("Générer plusieurs QR codes")

    if multiple:
        first_serial = st.text_input("Premier numéro de série", value="0001")
        last_serial = st.text_input("Dernier numéro de série", value="0010")
    else:
        serial = st.text_input("Numéro de série", value="0001")

    if st.button("Générer les QR codes" if multiple else "Générer le QR code"):

        if multiple:
            if not model.strip() or not first_serial.strip() or not last_serial.strip():
                st.error("Veuillez sélectionner le modèle et saisir les numéros de série.")
            elif not first_serial.isdigit() or not last_serial.isdigit():
                st.error("Les numéros de série doivent être des entiers.")
            else:
                start = int(first_serial)
                end = int(last_serial)

                if start > end:
                    st.error("Le premier numéro de série doit être inférieur ou égal au dernier.")
                else:
                    serial_width = max(len(first_serial), len(last_serial))
                    zip_buffer = BytesIO()

                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        preview_done = False

                        for i in range(start, end + 1):
                            serial_i = str(i).zfill(serial_width)
                            img, msg, whatsapp_link = create_qr_image(model, serial_i, phone_number)

                            img_buffer = BytesIO()
                            img.save(img_buffer, format="PNG")
                            img_buffer.seek(0)

                            safe_model = model.replace("/", "-").replace(" ", "_")
                            file_name = f"qr_{safe_model}_{serial_i}.png"
                            zip_file.writestr(file_name, img_buffer.getvalue())

                            if not preview_done:
                                st.image(img_buffer, caption=f"Aperçu du premier QR code : {serial_i}")
                                st.text_area("Message généré (premier QR code)", msg, height=100)
                                st.text_area("Lien WhatsApp (premier QR code)", whatsapp_link, height=100)
                                preview_done = True

                    zip_buffer.seek(0)

                    total = end - start + 1
                    st.success(f"{total} QR codes générés avec succès.")

                    safe_model = model.replace("/", "-").replace(" ", "_")
                    st.download_button(
                        label="Télécharger tous les QR codes (.zip)",
                        data=zip_buffer,
                        file_name=f"qr_codes_{safe_model}_{first_serial}_to_{last_serial}.zip",
                        mime="application/zip"
                    )

        else:
            if not model.strip() or not serial.strip():
                st.error("Veuillez sélectionner le modèle et saisir le numéro de série.")
            else:
                img, msg, whatsapp_link = create_qr_image(model, serial, phone_number)

                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)

                st.success("QR code généré avec succès.")
                st.image(buffer, caption="Aperçu du QR code")
                st.text_area("Message généré", msg, height=100)
                st.text_area("Lien WhatsApp", whatsapp_link, height=100)

                safe_model = model.replace("/", "-").replace(" ", "_")
                st.download_button(
                    label="Télécharger le QR code",
                    data=buffer,
                    file_name=f"qr_{safe_model}_{serial}.png",
                    mime="image/png"
                )