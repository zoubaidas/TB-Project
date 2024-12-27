from ai import TaskTree
from command_execution import execute_command
from datetime import datetime

def main():
    """
    Main function to perform penetration testing on a specified target.

    This function initializes a TaskTree object for the given target, retrieves and executes
    commands iteratively, updates the task tree with the command outputs, and displays the
    updated task tree after each command execution. The process stops after 50 commands or
    when no more commands are available.

    Parameters:
    ----------
    None

    Returns:
    -------
    None
    """
    # Target to perform penetration testing on
    target = input("Enter the target: ")

    # Maximum number of commands to execute
    max_commands = int(input("Enter the maximum number of commands to execute: "))

    # Create a TaskTreeChain object
    task_tree = TaskTree(target)

    # Display the initial tree
    print(task_tree.current_task_tree, "\n")

    command_number = 0
    command_outputs = []

    while True:
        # Fetch the next command
        tool = task_tree.extract_tool_name()
        if tool is None:
            print("No more commands to execute.")
            break

        task_tree.update_task_tree_with_tool_command(tool)
        # Display the updated task tree
        print("==================== Command update ====================")
        print(task_tree.current_task_tree, "\n")

        next_command = task_tree.get_next_command()
        # Execute the command on a Linux machine, then retrieve the output.
        output = execute_command(next_command)

        # Add the command and its output to the list
        command_outputs.append({
            "command": next_command,
            "output": output
        })

        # Update the task tree with the output
        updated_tree = task_tree.update_task_tree_with_output(output)

        # Display the updated task tree
        print("==================== Updated Task Tree ====================")
        print(updated_tree, "\n")

        command_number += 1
        if command_number > max_commands:
            break

    # Generate a timestamp in the format YYYY-MM-DD_HH-MM-SS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Save the command outputs to a file with the timestamp in the file name
    file_name = f"command_outputs_{timestamp}.md"
    with open(file_name, "w") as file:
        for command_output in command_outputs:
            file.write(f"Command: {command_output['command']}\n")
            file.write(f"Output: {command_output['output']}\n\n")

    # Generate the final report
    task_tree.generate_report()

if __name__ == "__main__":
    main()