#!/usr/bin/env python3

#CST:xvitas02

"""!
@package cst.py
.c/.h file statistics.

This module is able to utilize helper classes in order to
be able to inform the user of the number of occurrences of
specified data – keywords, patterns, operators, identifiers
and so on. More info in the assignment.
"""

import sys
from arguments import Arguments
from parser import Parser


def main():
    """!
    @brief Puts the bits and pieces together.
    Uses the available classes from the imported modules to carry
    out the functionality specified by the assignment. For more
    information, consult the enclosed documentation.
    """
    ### INITIATING NEEDED OBJECTS ###
    arguments = Arguments()
    arguments.get_args()
    parser = Parser()
    parser.get_all_filepaths(arguments.args_dict)
    ### END INITIATING NEEDED OBJECTS ###

    ### CLEANING THE OUTPUT FILE ###
    if arguments.args_dict['output_file'] is not None:
        try:
            open(arguments.args_dict['output_file'], 'w').close()
        except:
            sys.stderr.write('The output file ' + arguments.args_dict['output_file'] +
                             ' cannot be opened.')
            sys.exit(3)
    ### END CLEANING THE OUTPUT FILE ###

    ### GETTING THE FINAL NUMBER OF OCCURRENCES ###
    total_num = 0
    for file in parser.files_list:
        num = parser.process_file(file, arguments.args_dict)
        total_num += num
    ### END GETTING THE FINAL NUMBER OF OCCURRENCES ##

    ### ALIGNING THE TOTAL NUMBER ###
    total_text = 'CELKEM: '
    total_num_padding = ''
    total_padding = ''.join([' ' for s in range(parser.maxlen - len(total_text))])
    total_num_padding = ''.join([' ' for s in range(parser.maxlen_num - len(str(total_num)))])
    ### END ALIGNING THE TOTAL NUMBER ###

    ### SORTING THE RESULTS ###
    results = parser.result_strings
    results.sort()
    ### END SORTING THE RESULTS ###

    ### PRINTING THE SEMI-RESULTS ###
    for item in sorted(results):
        if arguments.args_dict['output_file'] is not None:
            with open(arguments.args_dict['output_file'], 'a', encoding='iso-8859-2') as output_file_handle:
                output_file_handle.write(item)
        else:
            sys.stdout.write(item)
    ### END PRINTING THE SEMI-RESULTS ###

    ### PRINTING THE TOTAL NUMBER ###
    if arguments.args_dict['output_file'] is not None:
        with open(arguments.args_dict['output_file'], 'a', encoding='iso-8859-2') as output_file_handle:
            output_file_handle.write(total_text + total_padding + total_num_padding + str(total_num) + '\n')
    else:
        if len(str(total_num)) == 2 and parser.maxlen_num != 1:
            sys.stdout.write(total_text + total_padding + ' ' + total_num_padding + str(total_num) + '\n')
        else:
            sys.stdout.write(total_text + total_padding + total_num_padding + str(total_num) + '\n')
    ### END PRINTING THE RESULTS ###

    if arguments.args_dict['output_file'] is not None:
        output_file_handle.close()

##########################
if __name__ == '__main__':
    main()
