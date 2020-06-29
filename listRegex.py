# given a list of lists of regexen indentify which list was chosen by the user given some user input in python.
import re

# list of lists
create = ['create','set','add']
read = ['read', 'show', 'get']
update = ['update', 'replace']
delete = ['delete','remove']

user_input = input()

for word_list in (create, read, update, delete):
    for word in word_list:
        # Search through user input for word
        if re.search(word, user_input):
            # Index 0 is the name of the list
            print("Match found in", word_list[0], "list!") 
