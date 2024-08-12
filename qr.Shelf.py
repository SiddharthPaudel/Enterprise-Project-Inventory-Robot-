# # import qrcode

# # def generate_qr_code(data, filename):
# #     # Generate QR code
# #     qr = qrcode.QRCode(
# #         version=1,
# #         error_correction=qrcode.constants.ERROR_CORRECT_L,
# #         box_size=10,
# #         border=4,
# #     )
# #     qr.add_data(data)
# #     qr.make(fit=True)

# #     # Generate an image from the QR code
# #     img = qr.make_image(fill_color="black", back_color="white")

# #     # Save the image
# #     img.save(filename)

# # # Example usage:
# # shelf_identifier = "Shelf_A"  # Replace with your shelf identifier or location
# # filename = "shelf_qr.png"  # Output filename
# # generate_qr_code(shelf_identifier, filename)
# # print(f"QR code saved as {filename}")





# import qrcode

# def generate_qr_code(data, filename):
#     # Generate QR code
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)

#     # Generate an image from the QR code
#     img = qr.make_image(fill_color="black", back_color="white")
import qrcode

def generate_qr_code(data, filename):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Generate an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image
    img.save(filename)

# Example usage:
shelf_identifier = "Shelf_A"  # Replace with your shelf identifier or location
filename = "shelf_qr.png"  # Output filename
generate_qr_code(shelf_identifier, filename)
print(f"QR code saved as {filename}")

#     # Save the image
#     img.save(filename)

# # Example usage:
# shelf_identifier = "Shelf_A"  # Replace with your shelf identifier or location
# filename = "shelf_qr.png"  # Output filename
# generate_qr_code(shelf_identifier, filename)
# print(f"QR code saved as {filename}")






