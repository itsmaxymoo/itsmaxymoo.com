import string
import random
import re
import os
import json
import glob
from PIL import Image, ImageOps
from datetime import datetime


JEKCMS_VERSION = "1.2"

HTML_ROOT = "."

JEKCMS_AUTHOR = "Max Loiacono"
CURRENT_YEAR_STR = str(datetime.now().year)
CURRENT_DATE_STR = datetime.now().strftime("%d %B %Y")

IMAGE_MAX_SIZE = 1500, 1500
IMAGE_WATERMARK_PATH = os.path.join(HTML_ROOT, "assets", "branding", "watermark.png")
IMAGE_EXPORT_QUALITY = 50
IMAGE_EXIF_DATETIME = 36867


def rand_string(length: int = 10):
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def file_get_contents(file_path: string):
	f = open(file_path, "r")
	contents = f.read()
	f.close()

	return contents


def file_put_contents(file_path: string, data: string, append: bool = False):
	f = open(file_path, "w" if not append else "a")
	f.write(data)
	f.close()


def file_exists(file_path: string) -> bool:
	return os.path.exists(file_path)


def file_get_ext(file: string) -> string:
	return file.split(".")[-1]


def file_get_basename(file: string) -> string:
	return os.path.splitext(os.path.basename(file))[0]


def file_count_lines(file: string) -> int:
	return len(open(file).readlines())


def co_exists(id: string, collection: string = "*") -> bool:
	for f in glob.glob(HTML_ROOT + "/_" + collection + "/*.md", recursive=True):
		if file_get_basename(f) == id:
			return True
	
	return False


def slugify(text: string) -> string:
	text = text.lower().rstrip().lstrip()
	text = re.sub(r"&", " and ", text)
	# Remove duplicate whitespace
	text = " ".join(text.split())
	text = re.sub(r"[^0-9A-Za-z \-_]", "", text)
	text = re.sub(r" ", "-", text)
	text = re.sub(r"-+", "-", text)
	text = text.rstrip("-").lstrip("-")
	return text


def jekyll_to_dict(data: string) -> dict:
	# Files must have trailing slash
	if data.endswith("---"):
		data += "\n"
	front_matter_raw = re.search(r"(?<=---\n).*?(?=\n---\n)", data, re.DOTALL)[0].rstrip().lstrip()
	body = re.findall(r"(?<=\n---\n).*", data, re.DOTALL)[-1].rstrip().lstrip()
	
	final_dict = {
		"_raw": data,
		"_body": body
	}

	for line in front_matter_raw.split("\n"):
		if line.startswith("#") or line == "":
			continue

		attr = line.split(":", 1)

		for i in range(0, len(attr)):
			attr[i] = attr[i].rstrip().lstrip()
		
		# Try to convert value to py type, remove padding quotes
		try:
			attr_val = json.loads(attr[1])
		except json.decoder.JSONDecodeError:
			attr_val = attr[1]
		
		final_dict[attr[0]] = attr_val
	
	return final_dict


def update_jekyll_page_value(in_data: string, attribute: string, value, pad_value_as_string = False) -> str:
	# Handle py -> jekyll type conversions
	if type(value) is bool:
		value = str(value).lower()
	elif type(value) is list:
		value = "[" + ", ".join(value) + "]"
	else:
		value = str(value)

	# Remove padding whitespace
	value = value.lstrip().rstrip()

	# If the value is empty, we MUST pad it as a string for Jekyll
	if not value:
		pad_value_as_string = True
	
	# If the value is a museum ref, we MUST pad with string for Jekyll
	if value.startswith("[[") and attribute != "_body":
		pad_value_as_string = True
	
	# Pad value with quotes if necessary
	if pad_value_as_string:
		value = "\"" + value + "\""

	# Create attribute: value line
	attrval = attribute + ": " + value

	# If regular attribute
	if attribute != "_body":
		# See if attribute already exists
		attr_regex = r"(?<=\n)" + re.escape(attribute) + r"[^\n]*(?=.*\n---\n)"
		if re.search(attr_regex, in_data, flags=re.DOTALL):
			# Update attribute if true
			return re.sub(attr_regex, attrval, in_data, flags=re.DOTALL)
		else:
			# Otherwise, create new attribute at the end of front matter.
			return re.sub(r"(?=\n---\n)", "\n" + attrval, in_data, flags=re.DOTALL)
	else:
		# The attribute is _body, update file body.
		return re.sub(r"(?<=\n---\n).*", "\n" + value + "\n", in_data, flags=re.DOTALL)


def dict_to_jekyll(data: dict) -> str:
	final_jekyll = ""
	data_keys = data.keys()
	is_existing = ("_raw" in data_keys)

	if is_existing:
		final_jekyll = data["_raw"]
	else:
		final_jekyll = "---\n---\n"
	
	for k in data_keys:
		if k != "_raw":
			final_jekyll = update_jekyll_page_value(final_jekyll, k, data[k])
	
	return final_jekyll


def prompt(prompt: string = "", default: string = ""):
	cin = input(prompt + " [" + default + "]: ")

	if cin == "":
		cin = default
	
	return cin


def process_image(image_input_path: string, image_output_path: string, brand = False) -> None:
	brand = False
	im = Image.open(image_input_path)

	im = ImageOps.exif_transpose(im)
	im.thumbnail(IMAGE_MAX_SIZE, Image.LANCZOS)

	im_width, im_height = im.size

	if brand:
		wm = Image.open(IMAGE_WATERMARK_PATH)
		wm_width, wm_height = wm.size
		
		im.convert("RGBA")
		wm.convert("RGBA")

		im.paste(wm, (im_width - wm_width, im_height - wm_height), wm)
	
	# subsampling=2 equivelant to 4:2:0 -> https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
	im.save(image_output_path, quality=IMAGE_EXPORT_QUALITY, subsampling=2, optimize=True)


def get_image_exif(image_path: string, exif: int) -> str:
	ime = Image.open(image_path)._getexif()

	if ime is not None and exif in ime:
		return ime[exif]
	else:
		return None
