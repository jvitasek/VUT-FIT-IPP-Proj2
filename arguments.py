#!/usr/bin/env python3

#CST:xvitas02

"""!
@package arguments.py
Parsing arguments and storing them.

This module takes care of the user-side arguments
and their storage by saving each of the values
into a dictionary called args_dict.
"""

import argparse
import sys


class Arguments:
    args_dict = dict()
    args_dict['input_file'] = None  # --input
    args_dict['subdirs'] = None  # --nosubdir
    args_dict['output_file'] = None  # --output
    args_dict['all_keywords'] = False  # -k
    args_dict['simp_ops'] = False  # -o
    args_dict['identifiers'] = False  # -i
    args_dict['word_search'] = None  # -w
    args_dict['comments'] = False  # -c
    args_dict['no_abs_path'] = False  # -p

    def get_args(self):
        """!
        @brief Get the user-side arguments.
        Gets all the user-side arguments and send them to a helper method.
        """
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--help", action="store_true")  # help statement
        parser.add_argument("--input", action="store")  # input file
        parser.add_argument("--nosubdir", action="store_true")  # without subdirectories
        parser.add_argument("--output", action="store")  # output file
        # OPTIONS
        parser.add_argument("-k", action="store_true")  # all keywords
        parser.add_argument("-o", action="store_true")  # simple operators
        parser.add_argument("-i", action="store_true")  # all operators, no keywords
        parser.add_argument("-w", action="store")  # search pattern
        parser.add_argument("-c", action="store_true")  # comments
        parser.add_argument("-p", action="store_true")  # without absolute path
        parsed_args, unknown = parser.parse_known_args()
        # any unrecognized commands end in an error message
        if len(unknown) > 0:
            sys.stderr.write('Unrecognized command(s):\n')
            for command in unknown:
                sys.stderr.write(command + '\n')
            exit(1)
        # processing the known arguments
        self.process_and_validate_args(parsed_args)

    def process_and_validate_args(self, args):
        """!
        @brief Validates and stores the user-side arguments.
        Params -k, -o, -i, -w and -c cannot be combined, thus the
        validation. Also, the argument values are stored into
        a dictionary attribute of the class.

        @param args The object returned by the ArgumentParser.parse_args() method.
        """
        ### STORING ARGS ###
        if args.help:
            self.output_help()
        if args.input:
            self.args_dict['input_file'] = args.input
        if args.nosubdir:
            self.args_dict['subdirs'] = args.nosubdir
        if args.output:
            self.args_dict['output_file'] = args.output
        if args.k:
            self.args_dict['all_keywords'] = args.k
        if args.o:
            self.args_dict['simp_ops'] = args.o
        if args.i:
            self.args_dict['identifiers'] = args.i
        if args.w:
            self.args_dict['word_search'] = args.w
        if args.c:
            self.args_dict['comments'] = args.c
        if args.p:
            self.args_dict['no_abs_path'] = args.p
        ### END STORING ARGS ###

        ### VALIDATION ###
        boolVals = sum([self.args_dict['all_keywords'], self.args_dict['simp_ops'], self.args_dict['identifiers'],
                        self.args_dict['comments']])
        if (boolVals > 1) or (boolVals == 1 and self.args_dict['word_search'] is not None):
            sys.stderr.write('You have passed an invalid combination of arguments.\n'
                             'Get help by passing the argument --help.\n')
            sys.exit(1)  # exit code 1 => forbidden combination of arguments
        if boolVals == 0 and self.args_dict['word_search'] is None:
            sys.stderr.write('No arguments passed. Get help by passing the argument --help.\n')
            sys.exit(1)  # exit code 1 => forbidden combination of arguments
        ### END VALIDATION ###

    def output_help(self):
        print("Usage:")
        print("--help " + "Prints the help statement.")
        print("--input=<fileordir> " + "Sets the input C file/dir to be checked.")
        print("--nosubdir " + "Do not go into subdirectories of the directory passed.")
        print("--output=<filename> " + "Sets the filename of the output file.")
        print("-k " + "Prints the number of keywords (in each source code and the total amount).")
        print("-o " + "Prints the number of simple operators (defined in the assignment).")
        print("-i " + "Prints the number of identifiers (in each source code and the total amount).")
        print("-w=<pattern> " + "Searches for the exact string <pattern> in all source codes and prints the number of occurences.")
        print("-c " + "Prints the total number of comment characters including //, /* and */.")
        print("-p " + "Combined with every option (except --help), prints the files without the absolute file path.")
        sys.exit(0)
