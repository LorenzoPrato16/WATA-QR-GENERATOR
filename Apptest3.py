import streamlit as st
import qrcode
from urllib.parse import quote
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os

st.set_page_config(
    page_title="Générateur de QR code",
    page_icon="WATA-logo-400x400px.ico",
    layout="centered"
)

st.image("WATA_logo_150px.png", width=200)
st.title("Générateur de QR code - SAV WATALUX")
st.text("Générez un QR code à afficher sur le dispositif pour contacter le portail SAV.")

phone_number = "41225483400"

model = st.selectbox(
    "Modèle du dispositif",
    [
        "Mini-WATA",
        "WATA-Standard",
        "WATA-Plus",
        "Maxi-WATA",
        "WataTest",
        "WataBlue",
        "WATAFLOW"
    ]
)

kits = ["WataTest", "WataBlue"]


def load_font(size, bold=False):
    font_candidates = []
    if bold:
        font_candidates = [
            "Montserrat-Bold.ttf",
        ]
    else:
        font_candidates = [
            "Montserrat-Regular.ttf",
        ]

    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue

    return ImageFont.load_default()


def safe_filename(text):
    return text.replace("/", "-").replace(" ", "_").replace(":", "-")


def generate_whatsapp_link(message, phone_number):
    encoded_message = quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"


def generate_qr_code(whatsapp_link):
    qr = qrcode.QRCode(version=1, box_size=15, border=1)
    qr.add_data(whatsapp_link)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="none").get_image().convert("RGB")


def fit_text(draw, text, max_width, start_size=28, min_size=14, bold=False):
    for size in range(start_size, min_size - 1, -1):
        font = load_font(size, bold=bold)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return font
    return load_font(min_size, bold=bold)


def create_square_label(qr_img, title, info_lines):
    canvas_size = 900
    bg_color = "none"
    text_color = "black"
    secondary_text = "black"

    final_img = Image.new("RGB", (canvas_size, canvas_size), bg_color)
    draw = ImageDraw.Draw(final_img)

    title_font = fit_text(draw, title, max_width=canvas_size - 80, start_size=60, min_size=40, bold=True)
    subtitle = "Scan this QR to contact us"
    subtitle_font = fit_text(draw, subtitle, max_width=canvas_size - 80, start_size=38, min_size=38, bold=False)
    info_font = load_font(38, bold=False)
    footer_font = load_font(42, bold=False)

    # Title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(
        ((canvas_size - title_width) / 2, 55),
        title,
        fill=text_color,
        font=title_font
    )

    # Subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(
        ((canvas_size - subtitle_width) / 2, 145),
        subtitle,
        fill=text_color,
        font=subtitle_font
    )

    # Device info
    info_text = "\n".join(info_lines)
    info_bbox = draw.multiline_textbbox((0, 0), info_text, font=info_font, spacing=14)
    info_width = info_bbox[2] - info_bbox[0]
    draw.multiline_text(
        ((canvas_size - info_width) / 2, 205),
        info_text,
        fill=text_color,
        font=info_font,
        spacing=14,
        align="center"
    )

    # QR code
    qr_size = 410
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = (canvas_size - qr_size) // 2
    qr_y = 340

    draw.rounded_rectangle(
        (qr_x - 16, qr_y - 16, qr_x + qr_size + 16, qr_y + qr_size + 16),
        radius=20,
        outline="black",
        width=3,
        fill="none"
    )
    final_img.paste(qr_img, (qr_x, qr_y))

    # Footer
    footer = (
        "Whatsapp: +41 22 548 34 00"
    )
    footer_bbox = draw.multiline_textbbox((0, 0), footer, font=footer_font, spacing=8)
    footer_width = footer_bbox[2] - footer_bbox[0]
    draw.multiline_text(
        ((canvas_size - footer_width) / 2, 795),
        footer,
        fill=secondary_text,
        font=footer_font,
        spacing=8,
        align="center"
    )

    return final_img


def create_qr_image_serial(model, serial, phone_number):
    msg = f"SERVICE REQUEST\nModel: {model}\nSerial: {serial}"
    whatsapp_link = generate_whatsapp_link(msg, phone_number)
    qr_img = generate_qr_code(whatsapp_link)

    info_lines = [
        f"Model : {model}",
        f"Serial Number : {serial}"
    ]

    final_img = create_square_label(qr_img, "SERVICE WATALUX", info_lines)
    return final_img, msg, whatsapp_link


def create_qr_image_kit(model, production_date, expiry_date, phone_number):
    prod_str = production_date.strftime("%d/%m/%Y")
    exp_str = expiry_date.strftime("%d/%m/%Y")

    msg = (
        f"SUPPORT REQUEST\n"
        f"Model: {model}\n"
        f"Production date: {prod_str}\n"
        f"Expiry date: {exp_str}"
    )

    whatsapp_link = generate_whatsapp_link(msg, phone_number)
    qr_img = generate_qr_code(whatsapp_link)

    info_lines = [
        f"Modèle : {model}",
        f"Date de production : {prod_str}",
        f"Date de péremption : {exp_str}"
    ]

    final_img = create_square_label(qr_img, "SERVICE WATALUX", info_lines)
    return final_img, msg, whatsapp_link


if model in kits:
    production_date = st.date_input("Date de production")
    expiry_date = st.date_input("Date de péremption")

    if st.button("Générer le QR code"):
        if expiry_date < production_date:
            st.error("La date de péremption doit être postérieure ou égale à la date de production.")
        else:
            img, msg, whatsapp_link = create_qr_image_kit(
                model,
                production_date,
                expiry_date,
                phone_number
            )

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            st.image(buffer, caption="Aperçu du QR code")
            st.download_button(
                label="Télécharger le QR code",
                data=buffer,
                file_name=f"qr_{safe_filename(model)}_{production_date.strftime('%Y%m%d')}_{expiry_date.strftime('%Y%m%d')}.png",
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
                            img, msg, whatsapp_link = create_qr_image_serial(model, serial_i, phone_number)

                            img_buffer = BytesIO()
                            img.save(img_buffer, format="PNG")
                            img_buffer.seek(0)

                            file_name = f"qr_{safe_filename(model)}_{serial_i}.png"
                            zip_file.writestr(file_name, img_buffer.getvalue())

                            if not preview_done:
                                st.image(img_buffer, caption=f"Aperçu du premier QR code : {serial_i}")
                                preview_done = True

                    zip_buffer.seek(0)

                    total = end - start + 1
                    st.success(f"{total} QR codes générés avec succès.")

                    st.download_button(
                        label="Télécharger tous les QR codes (.zip)",
                        data=zip_buffer,
                        file_name=f"qr_codes_{safe_filename(model)}_{first_serial}_to_{last_serial}.zip",
                        mime="application/zip"
                    )

        else:
            if not model.strip() or not serial.strip():
                st.error("Veuillez sélectionner le modèle et saisir le numéro de série.")
            else:
                img, msg, whatsapp_link = create_qr_image_serial(model, serial, phone_number)

                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)

                st.success("QR code généré avec succès.")
                st.image(buffer, caption="Aperçu du QR code")
                st.download_button(
                    label="Télécharger le QR code",
                    data=buffer,
                    file_name=f"qr_{safe_filename(model)}_{serial}.png",
                    mime="image/png"
                )