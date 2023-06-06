import re
not_import_all_rule = re.compile("from .* import \*")

a = not_import_all_rule.sub("pass", " from aux import *; from bux import a")
print(a)