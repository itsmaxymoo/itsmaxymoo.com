#!/bin/python

from jekcms import *
import argparse
import os
import glob


MAX_CONTENT = 100
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)) + "/new-content.py"


# Veirfy SCRIPT_PATH
if not file_exists(SCRIPT_PATH):
	print("ERROR: Cannot find new-content.py!")
	exit(1)

print("New Content SERIES")

# Input file command line arg handling
parser = argparse.ArgumentParser(description="New content SERIES", allow_abbrev=False)
parser.add_argument("in_files", type=str, nargs="+", help="file(s) to include in the content series")
args = parser.parse_args()

in_files = []
for f in args.in_files:
	in_files.extend(glob.glob(f))

# Verify in_files
for f in in_files:
	if not file_exists(f):
		print("ERROR: input file does not exist: " + f)
		exit(1)

in_files_len = len(in_files)
if in_files_len > MAX_CONTENT:
	print("ERROR: Maximum of " + str(MAX_CONTENT) + " inputs (" + str(in_files_len) + " given)")
	exit(1)

# User input
include_default_ctags = "1"
series_basename = prompt("Series basename")
series_date = prompt("Default content date", CURRENT_DATE_STR)
include_default_ctags = prompt("Include default ctags (0/1)", "1")

default_ctags = ""
if include_default_ctags == "1":
	default_ctags = prompt("Default ctags", slugify(series_basename + "-album"))

# Begin new-content automation
series_i = 1

for f in in_files:
	series_i_padded = str(series_i * 10).zfill(3)

	print("\n!!!!! PROCESSING: " + series_i_padded + ": " + f)
	prompt("Press enter to continue")

	os.system(SCRIPT_PATH + " \"" + f + "\" -s \"" + series_i_padded + "\" -b \"" + series_basename + "\"" + ((" -t \"" + default_ctags + "\"") if len(default_ctags) > 1 else "") + " -d \"" + series_date + "\"")

	series_i += 1

print()
print("Series done!")
