import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Quadtree Image Compression", layout="centered")
st.title("🧩 Quadtree Image Compression Visualizer")

# Sidebar parameters
THRESHOLD = st.sidebar.slider("Color Variance Threshold", 0, 100, 15)
MIN_SIZE = st.sidebar.slider("Minimum Block Size (px)", 4, 64, 16)

# File uploader
uploaded_file = st.file_uploader("Upload an Image (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.subheader("Original Image")
    st.image(image, use_container_width=True)

    img_array = np.array(image)
    draw_img = image.copy()
    draw = ImageDraw.Draw(draw_img)
    
    block_counter = [0]  # Using a list so it can be updated inside the function

    def is_uniform(block):
        if block.size == 0:
            return True
        std = np.std(block.reshape(-1, 3), axis=0)
        return np.max(std) < THRESHOLD

    def quadtree(x, y, w, h):
        block = img_array[y:y+h, x:x+w]
        if w <= MIN_SIZE or h <= MIN_SIZE or is_uniform(block):
            draw.rectangle([x, y, x+w, y+h], outline="red")
            block_counter[0] += 1
        else:
            hw, hh = w // 2, h // 2
            quadtree(x, y, hw, hh)
            quadtree(x+hw, y, w-hw, hh)
            quadtree(x, y+hh, hw, h-hh)
            quadtree(x+hw, y+hh, w-hw, h-hh)

    # Run compression
    quadtree(0, 0, img_array.shape[1], img_array.shape[0])

    st.subheader("Compressed (Visualized) Image")
    st.image(draw_img, use_container_width=True)

    # Size and compression info
    st.markdown("### 📊 Compression Details")

    width, height = image.size
    original_pixels = width * height
    original_data_bytes = original_pixels * 3  # RGB
    estimated_compressed_bytes = block_counter[0] * 8  # Approx 8 bytes per block

    st.write(f"**Original Dimensions:** {width} × {height}")
    st.write(f"**Original Pixel Count:** {original_pixels:,}")
    st.write(f"**Blocks Used in Compression:** {block_counter[0]:,}")
    st.write(f"**Estimated Original Size:** {original_data_bytes / 1024:.2f} KB")
    st.write(f"**Estimated Compressed Size:** {estimated_compressed_bytes / 1024:.2f} KB")

    if estimated_compressed_bytes > 0:
        compression_ratio = original_data_bytes / estimated_compressed_bytes
        st.write(f"**Estimated Compression Ratio:** {compression_ratio:.2f}×")
    else:
        st.warning("Compression resulted in zero blocks — check your threshold or image.")

else:
    st.info("Upload an image to begin.")
