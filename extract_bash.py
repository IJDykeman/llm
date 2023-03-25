import re

def extract_bash_commands(text):
    pattern = r'COMMAND (.+?)(?=COMMAND|\Z)'
    commands = re.findall(pattern, text, flags=re.DOTALL)
    return [command.strip() for command in commands]

input_text = '''
I'm going to say something!
COMMAND echo "hello world"

Now I'm going to add some lines to a file!
COMMAND echo "
hello
world
multiline
" >> file.txt
'''

bash_commands = extract_bash_commands(input_text)
print(bash_commands)
