import cv2
import numpy as np
from PIL import Image,ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

root = tk.Tk()
root.title("Image Steganography")
root.iconbitmap("images/logo_stego.ico")
root.geometry("300x300")
# Convert data to binary format
def data2binary(data):
    # If the data is a string, convert each character to its binary representation
    if isinstance(data, str):
        p = ''.join([format(ord(i), '08b') for i in data])
    # If the data is bytes or numpy array, convert each element to its binary representation
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        p = [format(i, '08b') for i in data]
    return p

# Hide data in the given image
def hide_data(img, data):
    data += "$$"  # '$$' -> secret key
    d_index = 0
    b_data = data2binary(data)
    len_data = len(b_data)

    # Iterate over each pixel in the image and update pixel values with hidden data
    for value in img:
        for pix in value:
            r, g, b = data2binary(pix)
            if d_index < len_data:
                pix[0] = int(r[:-1] + b_data[d_index])  # Update red channel
                d_index += 1
            if d_index < len_data:
                pix[1] = int(g[:-1] + b_data[d_index])  # Update green channel
                d_index += 1
            if d_index < len_data:
                pix[2] = int(b[:-1] + b_data[d_index])  # Update blue channel
                d_index += 1
            if d_index >= len_data:
                break
    return img

# Encode a message into an image
def encode():
    img_path = filedialog.askopenfilename(title="Choose an image file")
    if img_path:
        img = cv2.imread(img_path)
        img_pil = Image.open(img_path, 'r')
        w, h = img_pil.size

        message = entry_message.get()
        if len(message) == 0:
            messagebox.showwarning("Warning", "Empty message")
            return

        enc_img_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")],
                                                    title="Save the encoded image")

        if enc_img_path:
            enc_img = hide_data(img, message)
            cv2.imwrite(enc_img_path, enc_img)

            img1 = Image.open(enc_img_path, 'r')
            img1 = img1.resize((w, h), Image.ANTIALIAS)

            # Optimize image with 65% quality (if the image is not square)
            if w != h:
                img1.save(enc_img_path, optimize=True, quality=65)
            else:
                img1.save(enc_img_path)

            messagebox.showinfo("Success", "Image encoded successfully.")

# Find hidden data in an image
def find_data(img):
    bin_data = ""
    for value in img:
        for pix in value:
            r, g, b = data2binary(pix)
            bin_data += r[-1]  # Extract the least significant bit from the red channel
            bin_data += g[-1]  # Extract the least significant bit from the green channel
            bin_data += b[-1]  # Extract the least significant bit from the blue channel

    all_bytes = [bin_data[i: i + 8] for i in range(0, len(bin_data), 8)]

    readable_data = ""
    for x in all_bytes:
        readable_data += chr(int(x, 2))
        if readable_data[-2:] == "$$":
            break
    return readable_data[:-2]

# Decode a message from an encoded image
def decode():
    img_path = filedialog.askopenfilename(title="Choose an image file")
    if img_path:
        img = cv2.imread(img_path)
        message = find_data(img)
        label_decoded_message.config(text="Decoded Message: " + message)

# Create UI elements
style = ttk.Style()
style.theme_use("clam")  # Choose a modern theme

frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky="nsew")

label_message = ttk.Label(frame, text="Enter Message:")
label_message.grid(row=0, column=0, sticky="w")

entry_message = ttk.Entry(frame, width=40)
entry_message.grid(row=1, column=0, pady=10, sticky="w")

button_encode = ttk.Button(frame, text="Encode", command=encode)
button_encode.grid(row=2, column=0, pady=10)

button_decode = ttk.Button(frame, text="Decode", command=decode)
button_decode.grid(row=3, column=0, pady=10)

label_decoded_message = ttk.Label(frame, text="Decoded Message: ")
label_decoded_message.grid(row=4, column=0, pady=10)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

root.mainloop()
