
# Project Title
Jinja2 Template Generation for Anuta NCX


The tool gives the ability to generate Anuta NCX form templates using Jinja2 Template Engine.


Details on how to define template variables, expressions and filters can be found here: [**Jinja2 Template Designer Documentation**](http://jinja.pocoo.org/docs/2.10/templates/)<br>


# Table of Contents
**[Pre-Requisites](#pre-requisites)**<br>
**[Getting Started](#getting-started)**<br>
**[User Guide](#user-guide)**<br>
**[Feedback](#feedback)**<br>


# Pre-Requisites

Mininum Python 3.5.2 installed on Windows, Mac OSX, Linux


Jinja2, PyYaml Python libraries (installation details in next section)

# Getting Started

Tool can be downloaded via GitHub clone repository. Ensure you have a valid GitHub account.


To download via Git CLI: ```git clone https://github.com/lucabrasi83/jinja2_template_gen_v2.git```


If you use GitHub Desktop, specify the following repository URL: ```https://github.com/lucabrasi83/jinja2_template_gen_v2.git```


From your GitHub desktop client, click Clone Repository:


![Alt text](doc_screenshots/github_gui_clone_repo.png?raw=true)



Enter Repository URL as below and select local folder where you want repository to be cloned:


![Alt text](https://raw.githubusercontent.com/lucabrasi83/jinja2_template_gen_v2/master/doc_screenshots/github_gui_clone.png)



After Repository is cloned, verify folder GitHub/jinja2_template_gen_v2 exists in folder specified as above:


![Alt text](https://raw.githubusercontent.com/lucabrasi83/jinja2_template_gen_v2/master/doc_screenshots/windows_github_folder.png)



To get colored output on Windows, use PowerShell interpreter (ideally you should run it as local administrator).


You can start PowerShell in the same context folder by clicking "Files" in Windows Explorer as below:


![Alt text](https://raw.githubusercontent.com/lucabrasi83/jinja2_template_gen_v2/master/doc_screenshots/openpowershell.png)



Make sure you the required libraries installed by running command ```pip install -r requirements.txt```


If you have multiple Python versions installed, you may need to run ```pip3 install -r requirements.txt```


![Alt text](https://raw.githubusercontent.com/lucabrasi83/jinja2_template_gen_v2/master/doc_screenshots/pip_install_requirements.png)



Verify Tool by entering command in PowerShell prompt: ```python start.py -h```


You should get below output with help context:


![Alt text](https://raw.githubusercontent.com/lucabrasi83/jinja2_template_gen_v2/master/doc_screenshots/start_py_help.png)



# User Guide

The tool is structured in 3 folders:

. Base_Template_Files : Includes baseline template files for each customer within a subfolder. The subfolder name represents the customer treegram.

. Templates_Inputs: Includes YAML file to gather service specific inputs. Same as above, subfolders are organized based on customer treegram.

. Templates_Generated: Includes generated templates organized in subfolders by customer name and site name.


1. To view the current variables defined in a base template file, you can run command: ```python start.py -xv <TREEGRAM>/<BASE_TEMPLATE_FILE>```

Example below displays the output of this command:

![Alt text](https://raw.githubusercontent.com/lucabrasi83/jinja2_template_gen_v2/master/doc_screenshots/extract_var.png)


2. To generate YAML file inputs from variables defined in base template, run command: ```python start.py -gi <TREEGRAM>/<BASE_TEMPLATE_FILE>```

3. To generate template file to be used to provision service, run command: ```python start.py -gt <TREEGRAM>/<INPUT_YAML_FILE>```


# Feedback

All bugs, feature requests, pull requests, feedback, etc., are welcome. [Create an issue](https://github.com/lucabrasi83/jinja2_template_gen_v2/issues).
