from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import letter
import os

# To allow large input file size in PILLOW
Image.MAX_IMAGE_PIXELS = None
from pathlib import Path

def extract_path_details(file_path):
    path = Path(file_path)
    folder_path = path.parent
    file_name = path.name
    file_stem = path.stem
    file_extension = path.suffix
    return folder_path.absolute().as_posix(), file_name, file_stem, file_extension


def join_path_details(folder_path, file_stem, file_extension):
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension

    full_path = Path(folder_path).joinpath(file_stem + file_extension)

    return full_path.absolute().as_posix()
  

def list_files(folder_path, file_postfix):
    path = Path(folder_path)
    file_paths = [file.absolute() for file in path.glob(f'*{file_postfix}') if file.is_file()]

    return file_paths

def crop_image_sides(image_path, output_image_path, left_ratio=0.20, right_ratio=0.20):
  """
  Crop an image left and right by a ratio.
  """
  img = Image.open(image_path)
  img_width, img_height = img.size

  left = img_width * left_ratio
  right = img_width * (1-right_ratio)
  top = 0
  bottom = img_height

  cropped_img = img.crop((left, top, right, bottom))

  cropped_img.save(output_image_path)


def split_image(image_path, output_pdf_path, page_height):
  """
  Split a long image into pages and export them in a PDF file
  """
  img = Image.open(image_path)
  img_width, img_height = img.size

  c = canvas.Canvas(output_pdf_path, pagesize=A4)
  width, height = A4

  scale = width / img_width
  scaled_img_width = img_width * scale
  pages = int(img_height / (page_height / scale)) + 1

  for i in range(pages):
      start = i * (page_height / scale)
      end = start + (page_height / scale)
      crop_area = (0, start, img_width, min(end, img_height))

      cropped_img = img.crop(crop_area)

      c.drawImage(ImageReader(cropped_img), 0, 50, width=scaled_img_width, height=page_height, preserveAspectRatio=True)
      c.showPage()

  c.save()


current_folder = os.path.dirname(os.path.abspath(__file__))
input_folder = Path(current_folder).joinpath('input').absolute().as_posix()
for input_file in list_files(input_folder, '.png'):
  print(input_file)
  folder, file_name, file_stem, file_ext = extract_path_details(input_file)
  output_image = join_path_details(Path(current_folder).joinpath('output'), file_stem, file_ext)
  output_pdf =  join_path_details(Path(current_folder).joinpath('output'), file_stem, 'pdf')

  print(output_image)
  print(output_pdf)

  crop_image_sides(input_file, output_image)
  split_image(output_image, output_pdf, 700)
