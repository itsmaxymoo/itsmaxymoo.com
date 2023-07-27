#!/bin/python

from jekcms import *
import glob
from PIL import Image


PATH_ROOT = HTML_ROOT
PATH_EXCLUDE = [
	"_includes/",
	"_layouts/",
	"_sass/",
	"assets/"
]


# Define ContentObject class
class ContentObject:
	TYPE_OTHER = 0
	TYPE_CONTENTMEDIA = 1
	TYPE_LOCATION = 2
	TYPE_OBJVIEW = 3
	TYPE_DOCUMENT = 4

	def __init__(self, path: string, type = TYPE_OTHER):
		self.path = path
		self.type = type
		self.errors = []
		self.content = ""
		self.jekyll = {}
CO = ContentObject


# Check image attributes
def co_check_image(co: ContentObject):
	errors = []

	# If a REGULAR ENTRY/MD FILE has an image attribute
	a_image = co.jekyll["image"] if "image" in co.jekyll else ""
	if a_image:
		# Verify image ref exists
		if not co_exists(a_image, "content"):
			errors.append("Unknown content reference: " + a_image)
	
	co.errors.extend(errors)


# Check contentmedia content
def co_check_contentmedia(co: ContentObject):
	errors = []

	# Check contentmedia has filename attrib
	a_filename = co.jekyll["filename"] if "filename" in co.jekyll else False
	if a_filename and len(a_filename) > 0:
		cm_fullpath = HTML_ROOT + "/content/" + a_filename
		# Verify content file exists
		if file_exists(cm_fullpath):
			try:
				# Validate image is valid, get dimensions (jpg and md)
				im = Image.open(cm_fullpath)

				im_width, im_height = im.size
				jek_width = co.jekyll["width"] if "width" in co.jekyll else 0
				jek_height = co.jekyll["height"] if "height" in co.jekyll else 0

				# If there is a mismatch in image dimensions, correct them
				if im_width != jek_width or im_height != jek_height:
					errors.append(
						"(WARN) ContentMedia dimension mismatch, attempting autocorrect ("
						+ str(jek_width)
						+ ","
						+ str(jek_height)
						+ ") -> ("
						+ str(im_width)
						+ ","
						+ str(im_height)
						+ ")"
					)
					try:
						# Update dimensions in mdfile
						co.content = update_jekyll_page_value(co.content, "width", im_width)
						co.content = update_jekyll_page_value(co.content, "height", im_height)
						co.jekyll = jekyll_to_dict(co.content)
						file_put_contents(co.path, co.content)
					except:
						errors.append("Autocorrect FAILED")
			except:
				errors.append("Invalid image at " + cm_fullpath)
		else:
			errors.append("Invalid (full)path for filename: " + cm_fullpath)
	else:
		errors.append("Missing filename attribute")

	co.errors.extend(errors)


# ContentObject processing function
def check_content_object(co: ContentObject):
	co.content = file_get_contents(co.path)
	try:
		co.jekyll = jekyll_to_dict(co.content)
	except:
		co.errors.append("Could not process jekyll content")
		# Reset type to disallow jekyll attribute specific checks
		co.type = CO.TYPE_OTHER

	# Run each check on the content object.
	co_check_image(co)

	if co.type == CO.TYPE_CONTENTMEDIA:
		co_check_contentmedia(co)

	# Reset these when done processing to save memory
	co.content = ""
	co.jekyll = {}


# --- EXECUTION SECTION ---

co_error_count = 0

# Get all qualifying files
input_files = glob.glob(PATH_ROOT + "/**/*.md", recursive=True)
input_files_rem = []
for f in input_files:
	for e in PATH_EXCLUDE:
		if f.startswith(HTML_ROOT + "/" + e):
			input_files_rem.append(f)
for f in input_files_rem:
	input_files.remove(f)
del input_files_rem
input_files.sort()


# Classify mds
content_objects = []
for f in input_files:
	path = f.replace(HTML_ROOT + "/", "")
	type = CO.TYPE_OTHER

	if path.startswith("_content/"):
		type = CO.TYPE_CONTENTMEDIA
	
	content_objects.append(
		CO(f, type)
	)


# Process each file
for co in content_objects:
	check_content_object(co)
	if len(co.errors) > 0:
		co_error_count += 1


# Print final report
print("Processed " + str(len(content_objects)) + " file(s).")
print("Found " + str(co_error_count) + " error(s).")
for co in content_objects:
	if len(co.errors) > 0:
		print()
		print("- " + co.path)
		for e in (co.errors):
			print("  - " + e)
