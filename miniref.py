#! /usr/bin/env python
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

        # reached end of e-mail, bring on the bibliography
        if (re.search(standard_signatures, line)):
            print("found text ending at: ", line, file=sys.stderr)
            is_bibliography = True
            print("setting up bibliography...", file=sys.stderr)

        # TODO: make this work for digits >9 as well
        markers = re.findall("(\[[^\[\]]\])", line)

        # still sifting though text, substitute placeholder markers with proper ones
        if (not is_bibliography):

            for marker in markers:
                try:
                    ref_registry[marker]
                    print("Error: duplicate marker: ", marker, file=sys.stderr)
                    return
                except:
                    new_ref = "[%i]" % ref_counter
                    ref_registry[marker] = new_ref
                    ref_counter += 1
                    line = line.replace(marker, new_ref)
            # save (possibly altered) line
            new_file.write(line)

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
                        bib_buffer[new_ref] = line
                        prev_ref_number = new_ref

                    except:
                        print("Warning: removing reference with unknown marker: ", marker, file=sys.stderr)
                        new_file.write(line.replace(marker, ""))

    # sort references in "bibliography" and write to file
    for i in range (1, len(bib_buffer)+1):
        curr_ref = "[%i]" % i
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
