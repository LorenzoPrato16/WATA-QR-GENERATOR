import qrcode
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont


PHONE_NUMBER = "41225483400"
OUTPUT_FILE = "qr_watalux_service.png"


def load_font(size, bold=False):
    font_candidates = ["Montserrat-Bold.ttf"] if bold else ["Montserrat-Regular.ttf"]

    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue

    return ImageFont.load_default()


def generate_whatsapp_link(message, phone_number):
    encoded_message = quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"


def generate_qr_code(whatsapp_link):
    qr = qrcode.QRCode(version=1, box_size=15, border=1)
    qr.add_data(whatsapp_link)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # make white transparent
    datas = qr_img.getdata()
    new_data = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    qr_img.putdata(new_data)

    return qr_img


def fit_text(draw, text, max_width, start_size=28, min_size=14, bold=False):
    for size in range(start_size, min_size - 1, -1):
        font = load_font(size, bold=bold)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return font
    return load_font(min_size, bold=bold)


def create_square_label(qr_img):
    canvas_size = 900
    bg_color = (255, 255, 255, 0)
    text_color = "black"
    secondary_text = "black"

    final_img = Image.new("RGBA", (canvas_size, canvas_size), bg_color)
    draw = ImageDraw.Draw(final_img)

    title = "SERVICE WATALUX"
    subtitle = "Scan this QR to contact us"
    footer = "Contactez-nous\nWhatsapp: +41 22 548 34 00"

    title_font = fit_text(draw, title, max_width=canvas_size - 80, start_size=60, min_size=40, bold=True)
    subtitle_font = fit_text(draw, subtitle, max_width=canvas_size - 80, start_size=38, min_size=30, bold=False)
    footer_font = load_font(42, bold=False)

    # Title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((canvas_size - title_width) / 2, 55), title, fill=text_color, font=title_font)

    # Subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((canvas_size - subtitle_width) / 2, 145), subtitle, fill=text_color, font=subtitle_font)

    # QR code
    qr_size = 450
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = (canvas_size - qr_size) // 2
    qr_y = 260

    draw.rounded_rectangle(
        (qr_x - 16, qr_y - 16, qr_x + qr_size + 16, qr_y + qr_size + 16),
        radius=20,
        outline="black",
        width=3
    )

    final_img.paste(qr_img, (qr_x, qr_y), qr_img)

    footer_bbox = draw.multiline_textbbox((0, 0), footer, font=footer_font, spacing=6)
    footer_width = footer_bbox[2] - footer_bbox[0]

    draw.multiline_text(
    ((canvas_size - footer_width) / 2, 770),
    footer,
    fill=secondary_text,
    font=footer_font,
    spacing=6,
    align="center"
    )

    return final_img


def create_qr_image(phone_number):
    msg = "SUPPORT REQUEST"
    whatsapp_link = generate_whatsapp_link(msg, phone_number)
    qr_img = generate_qr_code(whatsapp_link)
    final_img = create_square_label(qr_img)
    return final_img, whatsapp_link


if __name__ == "__main__":
    img, whatsapp_link = create_qr_image(PHONE_NUMBER)
    img.save(OUTPUT_FILE, format="PNG")
    print(f"QR code saved as: {OUTPUT_FILE}")
    print(f"WhatsApp link: {whatsapp_link}")