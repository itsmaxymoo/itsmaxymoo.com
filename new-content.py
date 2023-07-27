#!/bin/python

from jekcms import *
import argparse
from datetime import datetime
from PIL import Image


PROTECTED_NAME_STRING_LENGTH = 20


print("New Content")

# Input file command line arg handling
parser = argparse.ArgumentParser(description="New content", allow_abbrev=False)
parser.add_argument("c_in_file", type=str, help="content file")
parser.add_argument("-s", "--sequence", type=str, help="text representing this image's order in a sequence")
parser.add_argument("-b", "--basename", type=str, help="text to be prepended to the content name")
parser.add_argument("-t", "--ctag", type=str, help="default ctag(s)")
parser.add_argument("-n", "--default-name", type=str, help="default name")
parser.add_argument("-l", "--default-license", type=str, help="default license type")
parser.add_argument("-m", "--default-museum", type=str, help="default museum entry")
parser.add_argument("-d", "--default-date", type=str, help="default date")
parser.add_argument("-loc", "--default-location", type=str, help="default location")
parser.add_argument("--existing-content-file", action="store_true", help="Do not copy or prep input file (existing content) - DANGEROUS - This should be used by scripts only")

args = parser.parse_args()
c_in_file = args.c_in_file
c_existing_content_file = args.existing_content_file

# Process default values
default_name = args.default_name
default_license = args.default_license
default_museum = args.default_museum
default_date = args.default_date
default_location = args.default_location
default_name = default_name if default_name else ""
default_license = default_license if default_license else "1"
default_museum = default_museum if default_museum else ""
default_location = default_location if default_location else ""
default_date = default_date if default_date else CURRENT_DATE_STR

if not file_exists(c_in_file) and not c_existing_content_file:
	print("ERROR: file does not exist: " + c_in_file)
	exit(1)

# Attempt to auto fetch date from image
if not (c_existing_content_file):
	date_exif = get_image_exif(c_in_file, IMAGE_EXIF_DATETIME)
	if date_exif is not None:
		default_date = datetime.strptime(date_exif, '%Y:%m:%d %H:%M:%S').strftime('%d %B %Y, at %H:%M')

# User input
c_in_file = c_in_file
c_basename = args.basename
c_sequence = args.sequence
c_default_ctags = args.ctag
c_basename = c_basename if c_basename else ""
c_sequence = c_sequence if c_sequence else ""
c_default_ctags = c_default_ctags if c_default_ctags else ""

print()
print("USING:")
print("sequence: " + c_sequence)
print("basename: " + c_basename)
print("default ctags: " + c_default_ctags)
print()

c_name = prompt("Content name", default_name)
print("--- LICENSE ---")
print("\t0) All rights reserved")
print("\t1) CC-BY-SA 4.0")
print("\t2) Public Domain")
print("\t3) Fair use, but copywritten")
print("\t(other) - type manually")
c_license = prompt("License", default_license)
c_author = prompt("Author", JEKCMS_AUTHOR)
c_date_made = prompt("Date made", default_date)
c_location = prompt("Location (manual)", default_location)
c_additional_tags = prompt("Additonal tags (comma sep)", "")
c_type = "0" # Always "0" for image
if not c_existing_content_file:
	pass
	brand_image = prompt("Brand image (0/1)", "0")

# Calculated values
c_id = slugify((" ".join(c_basename.split() + c_sequence.split() + c_name.split())))
c_name = " ".join(c_basename.split() + c_name.split())
c_filename = c_id + "." + file_get_ext(c_in_file)
out_file = HTML_ROOT + "/_content/" + c_id + ".md"
# Content protection
if not (c_license == "1" or c_license == "2"):
	c_filename = rand_string(PROTECTED_NAME_STRING_LENGTH) + "." + file_get_ext(c_in_file)
# Handle c_existing_content_file
if c_existing_content_file:
	c_filename = c_in_file
c_ctags = [c_id]
# Append default (cli) ctags
if len(c_default_ctags) > 0:
	c_ctags.extend([ct.strip() for ct in c_default_ctags.split(",")])
# Append added extra ctags
if len(c_additional_tags) > 0:
	c_ctags.extend([ct.strip() for ct in c_additional_tags.split(",")])
# Setup image final dimensions
c_width = 0
c_height = 0

# Final conflict check before output
if file_exists(HTML_ROOT + "/content/" + c_filename) and not c_existing_content_file:
	print("ERROR: " + c_filename + " already exists in content!")
	exit(1)
if file_exists(out_file):
	print("ERROR: Duplicate content id: " + c_id)
	exit(1)

if not c_existing_content_file:
	process_image(c_in_file, HTML_ROOT + "/content/" + c_filename, (brand_image == "1"))
c_width, c_height = Image.open(HTML_ROOT + "/content/" + c_filename).size

jekyll_content = {
	"title": c_name,
	"license": c_license,
	"author": c_author,
	"date_made": c_date_made,
	"location": c_location,
	"ctags": c_ctags,
	"filename": c_filename,
	"width": c_width,
	"height": c_height,
	"_body": c_name
}

file_put_contents(out_file, dict_to_jekyll(jekyll_content))

out_file_body_line = file_count_lines(out_file)

os.system("nano +" + str(out_file_body_line) + " " + out_file)

print("Done!")
