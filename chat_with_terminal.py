import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subprocess import Popen, PIPE
from shlex import split
from print_colors import *
from llm.chatgpt import *
import subprocess
from repo_helpers import get_git_repo_root

# Command functions


def grep_file(pattern, file_path):
    result = subprocess.run(["grep", pattern, file_path],
                            capture_output=True, text=True)
    return result.stdout.strip()


def list_directory(directory="."):
    return os.listdir(directory)


def cat_file(file_path):
    result = subprocess.run(["cat", file_path], capture_output=True, text=True)
    return result.stdout.strip()


def run_bash_command(command, timeout_seconds=3):
    # get user consent to run the command
    print_red(f"Running command: {command}")
    

    try:
        proc1 = subprocess.run(
            [command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=timeout_seconds)
        result_stdout = proc1.stdout.decode()
        result_stderr = ""
        if proc1.stderr:
            result_stderr = proc1.stderr.decode()
        return result_stdout, result_stderr
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout_seconds} seconds."


def parse_command_and_args(response):
    command_parts = response.split()
    command = command_parts[0]
    args = command_parts[1:]
    return command, args


def read_file(file_path):
    with open(file_path) as f:
        return f.read()


prompt = read_file(get_git_repo_root() +
                   "/python/llm/prompts/top_level_prompt.md")

print_blue(prompt)

conversation = [system_message(prompt)]
conversation.append(user_message("Hello"))
conversation.append(assistant_message("Hello!  I am an agent who can use Unix commands and interact with the internet.  "
                                      "I can access files on your system using bash.  How can I help you?"))
conversation.append(user_message("take a look around with ls"))
conversation.append(assistant_message("I have access to your terminal, so I can run ls directly.\nCOMMAND ls"))
conversation.append(user_message(("OUTPUT FROM ls\nSTDOUT: clojure\ndata\ndocker\njulia\nnotes.md\n"
                                  "python\nrust\nscheme\nsummary.txt\ntest_gitlab_tools.py\n\nSTDERR: "
                                  "\nNote that no human has reviewed the output of this command.\n")))
conversation.append(assistant_message("INFO What would you like to do next?"))
conversation.append(user_message("Create a python file that prints hello world."))
cmd1 = "echo \"# this file is a basic hello world example\" > hello.py"
cmd2 = "echo \"print(\'Hello world\')\" >> hello.py"
conversation.append(assistant_message(f"COMMAND {cmd1}\nCOMMAND {cmd2}"))
conversation.append(user_message((f"OUTPUT FROM {cmd1}\nSTDOUT:\nSTDERR:"
                                  "\nNote that no human has reviewed the output of this command.\n"
                                  f"OUTPUT FROM {cmd2}\nSTDOUT:\nSTDERR:"
                                  "\nNote that no human has reviewed the output of this command.\n")))
conversation.append(assistant_message("INFO What would you like to do next?"))
conversation.append(user_message("Write a summary of what you did to summary.txt."))
cmd = "echo \"I created a python file that prints hello world.\" >> summary.txt"
conversation.append(assistant_message(f"COMMAND {cmd}"))
conversation.append(user_message(f"OUTPUT FROM {cmd}\nSTDOUT:\nSTDERR:"))
conversation.append(assistant_message("INFO Done!  What would you like to do next?"))




def main():
    iteration = 0
    # initial_prompt = "Take a look around and summarize a file that you find.  Use `echo \"...\" >> summary.txt` to record your findings."
    initial_prompt = ""
    while True:
        if iteration == 0 and initial_prompt:
            user_prompt = initial_prompt
        else:
            user_prompt = input("Enter your prompt: ")

            if user_prompt == "DEBUG":
                for message in conversation:
                    role = message['role']
                    print_fn = print_green if role == "assistant" else print_blue
                    content = message['content']
                    print_fn(f"{role.capitalize()}: {content}\n")

                continue
        iteration += 1

        conversation.append(user_message(user_prompt))

        gpt3_response = generate_chat_response(conversation)
        conversation.append(assistant_message(gpt3_response))

        while True:
            command_output = ""

            needs_confirmation = True
            for raw_line in gpt3_response.splitlines():
                line = raw_line.replace("`", "")

                if line.strip().startswith("COMMAND"):
                    if needs_confirmation:
                        print_red("Are you sure you want to run these commands? (y/n)")
                        user_input = input()
                        if user_input != "y":
                            break
                        needs_confirmation = False
                    gpt_issued_command = line.replace("COMMAND", "").strip()
                    command_output += "OUTPUT FROM " + gpt_issued_command + "\n"
                    try:
                        result_stdout, result_stderr = run_bash_command(gpt_issued_command)
                        if not result_stdout or result_stdout == "":
                            command_output += "STDOUT and STDERR are empty.\n"
                        else:
                            command_output += "STDOUT: " + result_stdout + "\n"
                            command_output += "STDERR: " + result_stderr + "\n"
                    except Exception as e:
                        command_output += f"Error executing {gpt_issued_command}: {e}" + "\n"

            if command_output:
                command_output += "Note that no human has reviewed this output.\n"
                print_yellow(command_output)
                conversation.append(user_message(command_output))
                gpt3_response = generate_chat_response(conversation)
                conversation.append(assistant_message(gpt3_response))

                
            else:
                if gpt3_response.startswith("INFO"):
                    break

                encouragement = "Your last reply was empty.  Please say something to the human user by starting your reply with \"INFO\""
                if not gpt3_response == "":
                    encouragement = ("This reply is autogenerated; a human has not read your last message. I do not not see a COMMAND, INFO or STUCK in your reply.\n"
                                    "If you believe that you have useful information for the human user or if you are stuck, start your "
                                    "message with INFO.    A human will look at the output or help you as needed.  "
                                    "Until you do STUCK or INFO you will be in a loop of messages "
                                    "like this one.")
                print_yellow("<encouraging the robot...>")
                conversation.append(user_message(encouragement))
                gpt3_response = generate_chat_response(conversation)
                if gpt3_response.strip() == "":
                    gpt3_response = "Is there anything else I can do for you?"
                conversation.append(assistant_message(gpt3_response))
            # print (conversation)



if __name__ == "__main__":
    print()
    print()
    # run_bash_command("find . -name \"*.py\" | xargs grep -i \"physics\"")
    # print(run_bash_command("ls"))
    main()
