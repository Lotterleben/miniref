#! /usr/bin/env python

'''
The MIT License (MIT)

Copyright (c) 2014-2015 Lotte Steenbrink

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from __future__ import print_function
from tempfile import mkstemp
from shutil import move
from os import remove, close

import argparse
import re
import traceback
import sys

standard_signatures = "With kind regards|Cheers|Regards|So long and thanks for all the fish"

def number_references(file_str):
    # {"[original marker]": "[new reference number]"}
    ref_registry = {}

    #{"[reference number]": "[reference number] entry"}
    bib_buffer = {}

    ref_counter = 1
    prev_ref_number = ""
    is_bibliography = False

    try:
        if file_str == "-":
            new_file = sys.stdout
            old_file = sys.stdin
        else:
            fh, abs_path = mkstemp()
            new_file = open(abs_path, 'w')
            old_file = open(file_str)
    except:
        print("Error: couldn't find file. Aborting.", file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        return

    print("counting references...", file=sys.stderr)

    for line in old_file:
        if ("TODO" in line):
            print( "Caution: found a TODO:\n\t", line, file=sys.stderr)

        # reached end of e-mail, bring on the bibliography
        if (re.search(standard_signatures, line)):
            print("found text ending at: ", line.strip("\n"), file=sys.stderr)
            is_bibliography = True
            print("setting up bibliography...", file=sys.stderr)

        markers = re.findall("(\[\^[^\[\]]+\])", line)

        # still sifting though text, substitute placeholder markers with proper ones
        if (not is_bibliography):
            marker_index = 0
            rest = line
            new_line = ""

            for marker in markers:
                # If the line has multiple markers,
                # use only the chunk from this marker to the next.
                # this is to prevent newly created new_ref s from replacing
                # valid other new_ref s occuring earlier in the line 
                # if those realier new_refs happen to have the same value as marker.

                chunk, rest = rest.split(marker)
                chunk += marker # that split just removed our marker. :( re-add it.

                try:
                    # refs may be used more than once, but warn just in case.
                    ref_no = ref_registry[marker]
                    print("Warning: duplicate marker %s in line" % marker, file=sys.stderr)
                    print("\t%s" % line, file=sys.stderr)
                    chunk = chunk.replace(marker, ref_no)

                except:
                    new_ref = "[^%i]" % ref_counter
                    ref_registry[marker] = new_ref
                    ref_counter += 1
                    chunk = chunk.replace(marker, new_ref) 
    
                marker_index += 1
                new_line += chunk

            new_line += rest

            # save (possibly altered) line
            new_file.write(new_line)

        # working on actual references, match proper substitutes from text
        elif (is_bibliography):

            # check if line is ended by \n, correct if it is not
            if (line[-1] != "\n"):
                line += "\n"

            # no markers in line: assuming multi-line reference
            if (not markers):
                try:
                    # get previous line this line belongs to
                    prev_line = bib_buffer[prev_ref_number]
                    # attach line
                    prev_line += line
                    #store
                    bib_buffer[prev_ref_number] = prev_line

                except KeyError:
                    # we probably just caught the signature or so. Put it back.
                    new_file.write(line)
                    pass


            # beginning of a new ref
            else:
                for marker in markers:
                    try:
                        new_ref = ref_registry[marker]
                        line = line.replace(marker, new_ref)

                        if (new_ref in bib_buffer):
                            print("Error: duplicate marker in bibliography: ", marker, file=sys.stderr)
                            return

                        bib_buffer[new_ref] = line
                        prev_ref_number = new_ref

                    except:
                        print("Warning: removing reference with unknown marker: ", marker, file=sys.stderr)
                        new_file.write(line.replace(marker, ""))

    # sort references in "bibliography" and write to file
    for i in range (1, len(bib_buffer)+1):
        curr_ref = "[^%i]" % i
        line = bib_buffer[curr_ref]
        new_file.write(line)

    if file_str != "-":
        #close temp file
        new_file.close()
        close(fh)
        old_file.close()
        #Remove original file
        remove(file_str)
        #Move new file
        move(abs_path, file_str)

def main():
    parser = argparse.ArgumentParser(description='sort out your references')
    parser.add_argument('-f','--file', type=str,required=True, help='file to sort out')
    args = parser.parse_args()

    number_references(args.file)

    print("done!")

if __name__ == "__main__":
    main()
