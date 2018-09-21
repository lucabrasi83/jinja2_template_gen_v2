import sys
import argparse
from lib.gen_inputs_yaml import yaml_input_gen, \
    extract_variable
from lib.gen_template import generate_frmtpl


class ColoredParseArgs(argparse.ArgumentParser):
    # color_dict is a class attribute, here we avoid compatibility
    # issues by attempting to override the __init__ method
    # RED : Error, GREEN : Okay, YELLOW : Warning, Blue: Help/Info
    color_dict = {'RED': '1;91', 'GREEN': '1;92',
                  'YELLOW': '1;93', 'BLUE': '1;96'}

    def print_usage(self, file=None):
        if file is None:
            file = sys.stdout
        self._print_message(self.format_usage()[0].upper() +
                            self.format_usage()[1:],
                            file, self.color_dict['YELLOW'])

    def print_help(self, file=None):
        if file is None:
            file = sys.stdout

        self._print_message(self.format_help(),
                            file, self.color_dict['BLUE'])

    def _print_message(self, message, file=None, color=None):
        if message:
            if file is None:
                file = sys.stdout
            # Print messages in bold, colored text if color is given.
            if color is None:
                file.write(message)
            else:
                # \x1b[ is the ANSI Control Sequence Introducer (CSI)
                file.write('\033[' + color + 'm' + message.strip() + '\033[0m\n')

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr, self.color_dict['RED'])
        sys.exit(status)

    def error(self, message):
        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, '%(prog)s: error: %(message)s\n' % args)


def switcher(arg):
    switcher_dict = {
        "show_template_vars": extract_variable,
        "generate_inputs": yaml_input_gen,
        "generate_template": generate_frmtpl,
        "create_customer": "cust_creation",
        "create_device": "dev_creation"
    }
    return switcher_dict.get(arg)


if __name__ == '__main__':

    parser = ColoredParseArgs(description='===Anuta Template Generation Helper v2.0===')

    # Set Arguments
    parser.add_argument('-gi', '--generate-inputs', help='Generate Template Inputs File')
    parser.add_argument('-gt', '--generate-template', help='Generate Service Template File')
    parser.add_argument('-cc', '--create-customer', help='Create Customer from standard model '
                                                         'from YAML input file')
    parser.add_argument('-xv', '--show-template-vars', help='Display Template File variables')
    parser.add_argument('-cd', '--create-device', help='Create a Device from YAML input file')

    # Parse Arguments into object
    _args = parser.parse_args()
    args_dict = _args.__dict__
    arg_found = False
    for k, v in args_dict.items():
        if k == "create_customer" and v:
            from lib.obj_create import cust_creation
            arg_found = True
            cust_creation(template_file=v)
        elif k == "create_device" and v:
            from lib.obj_create import create_device
            arg_found = True
            create_device(template_file=v)
        elif v:
            func = switcher(k)
            try:
                arg_found = True
                func(v)
            except TypeError:
                print("\033[91m", "Invalid Option Given", "\033[0m")
                sys.exit(2)
    if not arg_found:
        parser.error(
                "At least one argument is required. Type 'python start.py -h' to see usage")
