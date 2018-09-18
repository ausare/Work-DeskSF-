#! /bin/python 
import os, re, glob

for root, dirs, files in os.walk("/Users/admin/Desktop"):
    for file in files:
# This works and find the two python files (excluding itself, which was surprising)
# ./PagServerPurger.pl
# ./xml_feat_converter.pl
# Didn't seem to work when placing the function directly in the search.
        find = ""
        find = re.search(r'(.*)_JG\..*', file)
        find2 = find.group(0)
        if(find):
            print os.path.join(root, file)
            newName = find.group(1)

            print "This is the newName, or is it? " + newName
            os.rename(find2, newName)
