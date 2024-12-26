import qrcode


def create_qr_code(self, data: str) -> None:
    qr = qrcode.QRCode(
        version=1, error_correction=qrcode.ERROR_CORRECT_L, box_size=10, border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
