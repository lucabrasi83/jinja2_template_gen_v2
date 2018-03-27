import sys
from gen_inputs_yaml import yaml_input_gen, extract_variable
from gen_template import generate_frmtpl


args_const = ("-gi", "-xv", "-gt")


if len(sys.argv) == 3:
    if sys.argv[1] in args_const:
        if sys.argv[1] == "-gi":
            yaml_input_gen(sys.argv[2])

        elif sys.argv[1] == "-gt":
            generate_frmtpl(sys.argv[2])

        elif sys.argv[1] == "-xv":
            extract_variable(sys.argv[2])
    else:
        print('\033[91m', "Invalid Argument Specified", '\033[0m')


elif len(sys.argv) == 2:
    if sys.argv[1] == "-h":
        usage_str_literal = \
        """
            \033[94m
          ========================================
          Anuta Template Generation Helper v1.0
          ========================================
          
          Usage:
          
          -gi <base_frmtpl_file_name> will generate variable inputs file from the template file specified.
          
          -gt <yaml_input_file_name>  will generate .frmtpl template from the input yaml file.
          
          -xv <base_frmtpl_file_name> will display the variables extracted from the .frmtpl file
          \033[0m
         """

        print(usage_str_literal)
    else:
        print('\033[91m', "Missing Additional Argument. Enter python start.py -h for usage description", '\033[0m')
else:
    print('\033[91m', "Invalid Argument Specified", '\033[0m')