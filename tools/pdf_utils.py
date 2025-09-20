# tools/pdf_utils.py
import fitz  # PyMuPDF
import base64

def pdf_to_base64_images(pdf_path: str) -> list[str]:
    """
    将PDF文件的每一页转换为Base64编码的PNG图片字符串列表。
    """
    try:
        doc = fitz.open(pdf_path)
        base64_images = []
        for page in doc:
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            base64_images.append(base64_image)
        doc.close()
        return base64_images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []
