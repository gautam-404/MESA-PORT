#Matches all sections in an inlist file. First Group is name of section, second is content
regex_sections = r"&(\w+[_]*\w+)([\w_\s\.\'\=\!\(\)\/\>\<\-\,]+)\/"
#Matches all parameters from a content. First Group is name of variable, second is content
regex_read_parameter = r"^\s+([\w_\d\(\):]+)\s*=\s*([-\.\w_\d']+)"
#Matches floatingpoint values. First one is pre floatingpoint, second one is power to 10
regex_floatingValue = r"([-\d\.\d]+)[deDE]([\-\d]*)"
#Matches a whole section and allows for it to insert something you would want
regex = r'[\w_\s\.\'\=\!\(\)\/\>\<\-\,]+)(\/)'