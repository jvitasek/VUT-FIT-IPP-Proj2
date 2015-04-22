#!/usr/bin/env python3

#CST:xvitas02

"""!
@package parser.py
Parsing C files for specified values.

This module carries out the most important function
in this project – it parses the assigned values from
the content of a file and returns the number of matches.
"""

import os
import re
import itertools
import sys


class Parser:
    # list to contain all the usable files to iterate over
    files_list = list()
    result_strings = list()
    # maximum length of a filepath/filename to be able to align the output
    maxlen = 0
    maxlen_num = 0

    # list of C keywords
    keywords_list = ['_Bool', '_Complex', '_Imaginary', 'auto', 'break', 'case', 'char', 'const', 'continue',
                     'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'inline',
                     'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch',
                     'typedef', 'union', 'unsigned', 'void', 'volatile', 'while']

    def get_all_filepaths(self, args_dict):
        """!
        @brief Gets filepaths from a directory.
        Gets all the filepaths from a specified directory (and subdirs).

        @param args_dict The dictionary of user-side arguments.
        """
        # if input wasn't specified, we use the current directory
        if args_dict['input_file'] is None:
            args_dict['input_file'] = '.'  # current directory

        # file or non-existent dir
        if not os.path.isdir(args_dict['input_file']):
            # either the path exists
            if os.path.exists(args_dict['input_file']):
                # in case it is readable (permissions)
                if os.access(args_dict['input_file'], os.R_OK):
                    # we don't care if it's .c or .h, we just process it
                    self.files_list.append(str(args_dict['input_file']))
                # otherwise we print an error
                else:
                    sys.stderr.write('The file you passed is not readable.\n')
                    sys.exit(21)  # exit code 21 => non-readable file
            # or it doesn't
            else:
                sys.stderr.write('The filepath you passed does not exist.\n')
                sys.exit(2)  # exit code 2 => non-existent filepath
        # directory
        else:
            # go into subdirectories
            if args_dict['subdirs'] is None:
                for path, subdirs, files in os.walk(args_dict['input_file']):
                    for filename in files:
                        filepath = os.path.join(path, filename)
                        self.get_usable_files(str(filepath))
            # do not go into subdirectories
            else:
                files = [f for f in os.listdir(args_dict['input_file']) if os.path.isfile(args_dict['input_file'] + '/' + f)]
                for f in files:
                    self.get_usable_files(args_dict['input_file'] + '/' + str(f))

    def get_usable_files(self, filepath):
        """!
        @brief Gets .c or .h filepaths.
        Gets all the usable files to get stats from.

        @param filepath The absolute or relative path to the file.
        """
        filename, fileext = os.path.splitext(filepath)
        # only including .c and .h files
        if fileext == '.c' or fileext == '.h':
            self.files_list.append(str(filepath))

    def process_file(self, filepath, args_dict):
        """!
        @brief Gets .c or .h filepaths.
        Reads the file pointed to by the filepath passed and executes
        the appropriate parsing function based on user-side arguments.

        @param filepath The absolute or relative path to the file.
        @param args_dict The dictionary of user-side arguments.
        @return Returns the number of occurrences to the caller.
        """
        # opening the file to read in the specified encoding
        filehandle = open(filepath, 'r', encoding='iso-8859-2')
        file_content = filehandle.read()
        output_file_handle = None
        if args_dict['output_file'] is not None:
            # opening the file to write to in the specified encoding
            output_file_handle = open(args_dict['output_file'], 'a', encoding='iso-8859-2')

        # handling formatted output
        for item in self.files_list:
            if args_dict['no_abs_path'] is False:
                if self.maxlen < len(os.path.abspath(item)):
                    self.maxlen = len(os.path.abspath(item))
            else:
                if self.maxlen < len(os.path.basename(item)):
                    self.maxlen = len(os.path.basename(item))

        file_occurrences = 0
        ### WORD/STRING OCCURRENCES ###
        if args_dict['word_search'] is not None:
            file_occurrences = self.get_number_of_occurrences(file_content, args_dict['word_search'])
            # print with absolute path
            if args_dict['no_abs_path'] is False:
                filepath = os.path.abspath(filepath)
            else:
                filepath = os.path.basename(filepath)
            if len(str(file_occurrences)) > self.maxlen_num:
                self.maxlen_num = len(str(file_occurrences))
            # formatting the output
            self.format_results(str(filepath), str(file_occurrences), output_file_handle)
            return file_occurrences
        ### END WORD/STRING OCCURRENCES ###

        # removing macros
        file_content = self.remove_macros(file_content)

        number_operators = 0
        ### OPERATORS ###
        if args_dict['simp_ops'] is True:
            number_operators = self.get_number_of_operators(file_content)
            if args_dict['no_abs_path'] is False:
                filepath = os.path.abspath(filepath)
            else:
                filepath = os.path.basename(filepath)
            if len(str(number_operators)) > self.maxlen_num:
                self.maxlen_num = len(str(number_operators))
            # formatting the output
            self.format_results(str(filepath), str(number_operators), output_file_handle)
            return number_operators
        ### END OPERATORS ###

        identifiers_occurrences = 0
        ### IDENTIFIERS OCCURRENCES ###
        if args_dict['identifiers'] is True:
            identifiers_occurrences = self.get_number_of_identifiers(file_content)
            # print with absolute path
            if args_dict['no_abs_path'] is False:
                filepath = os.path.abspath(filepath)
            else:
                filepath = os.path.basename(filepath)
            if len(str(identifiers_occurrences)) > self.maxlen_num:
                self.maxlen_num = len(str(identifiers_occurrences))
            # formatting the output
            self.format_results(str(filepath), str(identifiers_occurrences), output_file_handle)
            return identifiers_occurrences
        ### END IDENTIFIERS OCCURRENCES ###

        keyword_file_occurrences = 0
        ### KEYWORDS ###
        if args_dict['all_keywords'] is True:
            keyword_file_occurrences = self.get_number_of_keywords(file_content)
            # print with absolute path
            if args_dict['no_abs_path'] is False:
                filepath = os.path.abspath(filepath)
            else:
                filepath = os.path.basename(filepath)
            if len(str(keyword_file_occurrences)) > self.maxlen_num:
                self.maxlen_num = len(str(keyword_file_occurrences))
            # formatting the output
            self.format_results(str(filepath), str(keyword_file_occurrences), output_file_handle)
            return keyword_file_occurrences
        ### END KEYWORDS ###

        number_multiline, number_inline = 0, 0
        ### COMMENTS ###
        if args_dict['comments'] is True:
            number_inline = self.get_inline_comments_number(file_content)
            number_multiline = self.get_multiline_comments_number(file_content)
            # print with absolute path
            if args_dict['no_abs_path'] is False:
                filepath = os.path.abspath(filepath)
            else:
                filepath = os.path.basename(filepath)
            # formatting the output
            if len(str(number_multiline + number_inline)) > self.maxlen_num:
                self.maxlen_num = len(str(number_multiline + number_multiline))
            self.format_results(str(filepath), str(number_multiline + number_inline), output_file_handle)
            return number_multiline + number_inline
        ### END COMMENTS ###

        # cleaning up
        if args_dict['output_file'] is not None:
            output_file_handle.close()
        filehandle.close()

    def get_number_of_identifiers(self, file_content):
        """!
        @brief Matches all C identifiers.
        Matches all C identifiers and returns the number of occurrences.
        Does not look into comments or strings.

        @param file_content The content of the file passed.
        @return Returns the number of occurrences of C identifiers.
        """
        # removing strings and comments
        file_content = self.remove_content(True, True, file_content)
        # and also char literals
        file_content = self.remove_char_literals(file_content)
        # matching based on standard C naming conventions
        regex = re.compile(r'\b[_a-zA-Z][_a-zA-Z0-9]*\b')
        matches = re.findall(regex, file_content)
        # list comprehension to remove known C keywords from the final list
        identifiers = [match for match in matches if match not in self.keywords_list]
        return len(identifiers)

    def get_number_of_keywords(self, file_content):
        """!
        @brief Matches all C keywords.
        Matches all C keywords and returns the number of occurrences.
        Does not look into comments or strings.

        @param file_content The content of the file passed.
        @return Returns the number of occurrences of C keywords.
        """
        # removing strings and comments
        file_content = self.remove_content(True, True, file_content)

        found_keywords = list()
        for keyword in self.keywords_list:
            regex = re.compile(r'\b' + re.escape(keyword) + r'\b')
            matches = re.findall(regex, file_content)
            if len(matches) != 0:
                found_keywords.append(matches)

        # flattening the list to be able to use len to get the number of occurrences
        flat_found_keywords = list(itertools.chain.from_iterable(found_keywords))
        return len(flat_found_keywords)

    def get_number_of_operators(self, file_content):
        """!
        @brief Matches all C keywords.
        Matches all C keywords and returns the number of occurrences.
        Does not look into comments or strings.

        @param file_content The content of the file passed.
        @return Returns the number of occurrences of C keywords.
        """
        # removing macros
        file_content = self.remove_macros(file_content)
        # removing comments and strings
        file_content = self.remove_content(True, True, file_content)
        # removing char literals
        file_content = self.remove_char_literals(file_content)
        # finally removing pointers
        file_content = self.remove_pointers(file_content)

        # regexing for the equal sign prefix operators, double char operators and single char operators
        regex_operators = re.compile(r'((?:\+|-|\*|\/|%|<<|>>|<|>|!|&|\||\^)=|\+\+|--|\|\||&&|<<|>>|->|==|(?:\+|-|\*|\/|%|&|=|\||\.[_a-zA-Z\s]|>|<|!|~|\^))')
        results_operators = re.findall(regex_operators, file_content)

        return len(results_operators)

    def get_number_of_occurrences(self, file_content, find):
        """!
        @brief Matches a word/string passed.
        Matches all exact occurrences of the string passed in the arguments.
        Look everywhere (macros, comments, strings).

        @param file_content The content of the file passed.
        @param find The word/string to match.
        @return Returns the number of occurrences of the string.
        """
        regex = re.compile(r'\b' + re.escape(find) + r'\b')
        results = re.findall(regex, file_content)
        return len(results)

    def get_multiline_comments_number(self, file_content):
        """!
        @brief Matches C-style multiline comments.
        Matches all the C multiline comments (/* */) and returns the number.

        @param file_content The content of the file passed.
        @return Returns the number of chars found in multiline comments.
        """
        comment_content = self.match_multiline_comments(file_content, False)
        return len(comment_content)

    def get_inline_comments_number(self, file_content):
        """!
        @brief Matches C-style inline comments.
        Matches all the C inline comments (//) and returns the number.

        @param file_content The content of the file passed.
        @return Returns the number of chars found in inline comments.
        """
        comment_content = self.match_inline_comments(file_content, False)
        return len(comment_content)

    def format_results(self, filepath, number, output_file_handle):
        """!
        @brief Write to file or stdout.
        Decides if the user wants the results printed into a file
        or onto the standard output.

        @param string The string to print.
        @param output_file_handle The filehandle of a file (no output file == None)
        """
        num_padding = ''
        # aligning the filename
        filename_padding = ''.join([' ' for s in range(self.maxlen - len(filepath))])
        # accounting for right align of the resulting number
        num_padding = ''.join([' ' for s in range(self.maxlen_num - len(str(number)))])
        self.result_strings.append(filepath + filename_padding + ' ' + num_padding + number + '\n')

    def remove_macros(self, string):
        """!
        @brief Removes all C preprocessor macros.
        Matches all the C macros and removes them (substitutes with '').

        @param string The content of the file passed.
        @return Returns the edited content of the file.
        """
        # bool value to know if we're inside a macro
        inside_macro = False
        # list for stored non-macro chars
        final_content = list()
        for index in range(0, len(string)):
            # macro start
            if string[index] == '#':
                inside_macro = True
            # macro end if multiline \ isn't present
            if inside_macro is True and string[index] == '\n' and string[index-1] != '\\':
                inside_macro = False
            # only store the content that is not a macro
            if inside_macro is False:
                final_content.append(string[index])
        # make a string out of the char list
        final_content = ''.join(final_content)
        # returning the final string
        return final_content

    def remove_char_literals(self, string):
        """!
        @brief Removes all C char literals.
        Matches all the C char literals and removes them (substitutes with '').

        @param string The content of the file passed.
        @return Returns the edited content of the file.
        """
        # bool value to know if we're inside a char literal
        inside_char = False
        # bool value to know we just passed the first single quote
        first_pass = False
        final_content = list()
        # for every char of the content passed
        for index in range(0, len(string)):
            # start of the char literal
            if string[index] == '\'' and first_pass is False:
                inside_char = True
                first_pass = True
                continue
            # end of the char literal
            if string[index] == '\'':
                inside_char = False
                first_pass = False
                continue
            # storing the content outside of the char literal
            if inside_char is False:
                final_content.append(string[index])
        # joining the list contents into a string
        final_content = ''.join(final_content)
        # returning the final string
        return final_content

    def remove_strings(self, string):
        """!
        @brief Removes all C strings ("").
        Matches all the C strings and removes them (substitutes with '').

        @param string The content of the file passed.
        @return Returns the edited content of the file.
        """
        # bool value to know if we're inside a string
        inside_string = False
        # bool value to know we just passed the first single quote
        first_pass = False
        final_content = list()
        # for every char of the content passed
        for index in range(0, len(string)):
            # start of the string
            if string[index] == '"' and first_pass is False:
                inside_string = True
                first_pass = True
                continue
            # end of the string
            if string[index] == '"':
                inside_string = False
                first_pass = False
                continue
            # storing the content outside of the string
            if inside_string is False:
                final_content.append(string[index])
        # joining the list contents into a string
        final_content = ''.join(final_content)
        # returning the final string
        return final_content

    def remove_pointers(self, file_content):
        """!
        @brief Removes all C pointers.
        Matches all the C pointers and removes them (substitutes with '').

        @param string The content of the file passed.
        @return Returns the edited content of the file.
        """
        # regex to match all the pointers
        final_content = re.sub(r'\b(_Bool|_Complex|char|const|double|float|int|long|short|'
                               'void)(\s*,?\s*\(?\s*\*+\s*'
                               '\(?\w*\)?)+', '\\1', file_content)
        # returning the final string
        return final_content

    def remove_content(self, comments, strings, file_content):
        """!
        @brief Removes specified parts of C file content.
        Matches the specified C file content and removes it.

        @param comments True – remove/False – do not remove
        @param strings True – remove/False – do not remove
        @return Returns the edited content of the file.
        """
        # if we want to remove comments
        if comments is True:
            file_content = self.match_inline_comments(file_content, True)
            file_content = self.match_multiline_comments(file_content, True)
        # if we want to remove string
        if strings is True:
            file_content = self.remove_strings(file_content)
        # return the edited content
        return file_content

    def match_inline_comments(self, string, remove):
        """!
        @brief Matches (and removes) all C inline comments (//).
        Matches all the C inline comments.

        @param string The content of the file passed.
        @param remove True – remove/False – match
        @return Returns the edited content of the file.
        """
        # bool value to know if we're inside an inline comment
        inside_inline_comment = False
        final_content = list()
        # for each char of the content string
        for index in range(0, len(string)):
            # inline comment start
            if string[index] == '/' and string[index+1] == '/':
                inside_inline_comment = True
            # end of the inline comment
            if string[index] == '\n':
                if inside_inline_comment is True:
                    # appending the newline character too
                    final_content.append(string[index])
                inside_inline_comment = False
            # if we want to remove it
            if remove is True:
                if inside_inline_comment is False:
                    # appending only the non-comment sections
                    final_content.append(string[index])
            # if we want to match it
            else:
                if inside_inline_comment is True:
                    # appending only the comment chars
                    final_content.append(string[index])
        # joining the char list into a string
        final_content = ''.join(final_content)
        # returning the final string
        return final_content

    def match_multiline_comments(self, string, remove):
        """!
        @brief Matches (and removes) all C multiline comments (/**/).
        Matches all the C multiline comments.

        @param string The content of the file passed.
        @param remove True – remove/False – match
        @return Returns the edited content of the file.
        """
        # bool value to know if we're inside an multiline comment
        inside_multiline_comment = False
        final_content = list()
        # for each char of the content string
        for index in range(0, len(string)):
            # start multiline comment
            if string[index] == '/' and string[index+1] == '*':
                inside_multiline_comment = True
            # end multiline comment
            if string[index-1] == '/' and string[index-2] == '*':
                inside_multiline_comment = False
            # if we want to remove it
            if remove is True:
                if inside_multiline_comment is False:
                    # appending only the non-comment sections
                    final_content.append(string[index])
            # if we want to match it
            else:
                if inside_multiline_comment is True:
                    # appending only the comment chars
                    final_content.append(string[index])
        # joining the char list into a string
        final_content = ''.join(final_content)
        # returning the final string
        return final_content
