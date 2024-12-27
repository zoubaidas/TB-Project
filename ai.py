import os
import time

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from command_execution import get_tool_help
from prompts import BASE_SYSTEM_PROMPT, OUTPUT_PROMPT, COMMAND_PROMPT, REPORT_PROMPT
from datetime import datetime


class TaskTree:
    """
    A class to represent an AI-based penetration testing assistant.

    Attributes:
    ----------
    target : str
        The target IP address or domain for the penetration test.
    llm : ChatOpenAI
        The language model used for generating and updating the task tree.
    current_task_tree : str
        The current state of the task tree.
    system_message : SystemMessage
        The initial system message for the language model.

    Methods:
    -------
    __init__(self, target: str):
        Initializes the AI object with the target and sets up the language model.

    update_task_tree_with_tool_command(self, tool) -> str | None:
        Updates the task tree with the command for the specified tool.

    update_task_tree_with_output(self, output_text: str) -> str:
        Updates the task tree with the output of the executed command.

    get_next_command(self) -> str | None:
        Retrieves the next command to be executed from the task tree.

    extract_tool_name(self) -> str | None:
        Extracts the name of the tool to be used from the task tree.

    generate_report(self):
        Generates a detailed penetration test report based on the task tree.
    """

    def __init__(self, target: str):
        """
        Initializes the AI object with the target and sets up the language model.

        Parameters:
        ----------
        target : str
            The target IP address or domain for the penetration test.
        """
        self.target = target
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="google/gemini-pro-1.5",
        )
        self.current_task_tree = ""
        self.system_message = SystemMessage(content=BASE_SYSTEM_PROMPT.format(target=target))
        response = self.llm.invoke([self.system_message])
        self.current_task_tree = response.content

    def update_task_tree_with_tool_command(self, tool) -> str | None:
        """
        Updates the task tree with the command for the specified tool.

        Parameters:
        ----------
        tool : str
            The name of the tool to be used.

        Returns:
        -------
        str | None
            The updated task tree or None if the update fails.
        """
        context = (f"Current Task Tree:\n"
                   f"{self.current_task_tree}\n\n"
                   f"Tool usage: \n\n"
                   f"Tool: {get_tool_help(tool)}")
        context_prompt = HumanMessage(content=COMMAND_PROMPT.format(context=context, tool=tool, target=self.target))
        response = self.llm.invoke([self.system_message, context_prompt])
        self.current_task_tree = response.content
        return self.current_task_tree

    def update_task_tree_with_output(self, output_text: str) -> str:
        """
        Updates the task tree with the output of the executed command.

        Parameters:
        ----------
        output_text : str
            The output of the executed command.

        Returns:
        -------
        str
            The updated task tree.
        """
        context = (f"Current Task Tree:\n"
                   f"{self.current_task_tree}\n\n"
                   f"Tool Output:\n"
                   f"{output_text}")
        context_prompt = HumanMessage(content=OUTPUT_PROMPT.format(context=context))
        response = self.invoke_with_retries([self.system_message, context_prompt])
        self.current_task_tree = response.content
        return self.current_task_tree

    def get_next_command(self) -> str | None:
        """
        Retrieves the next command to be executed from the task tree.

        Returns:
        -------
        str | None
            The next command to be executed or None if no command is found.
        """
        lines = self.current_task_tree.strip().splitlines()
        command = None
        for line in reversed(lines):
            clean_line = ''.join(c for c in line if c.isprintable()).strip()
            if clean_line.lower().startswith("command:"):
                command = clean_line.split("Command:", 1)[1].strip()
                break
        if command.startswith("`"):
            command = command[1:]
        if command.endswith("`"):
            command = command[:-1]
        return command

    def extract_tool_name(self) -> str | None:
        """
        Extracts the name of the tool to be used from the task tree.

        Returns:
        -------
        str | None
            The name of the tool or None if no tool is found.
        """
        lines = self.current_task_tree.strip().splitlines()
        for line in reversed(lines):
            if "Tool:" in line:
                tool_name = line.split("Tool:", 1)[1].strip()
                return tool_name
        print("No more commands to execute.")
        return None

    def generate_report(self):
        """
        Generates a detailed report based on the current task tree and writes it to a file.

        The method creates a prompt for generating a report, invokes an LLM (Language Model)
        to process the prompt, and saves the resultant report into a timestamped file.

        Returns
        -------
        str
            The content of the generated report.
        """
        context_prompt = HumanMessage(content=REPORT_PROMPT.format(task_tree=self.current_task_tree))
        response = self.llm.invoke([context_prompt])
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"report_{self.target}_{timestamp}.txt"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(response.content)
        print(f"Report generated successfully. Saved as: {file_name}")
        return response.content

    def invoke_with_retries(self, messages, max_retries=3, delay=2):
        """
        Invoke the ChatOpenAI API with retries for handling transient errors.
        """
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(messages)
            except ValueError as e:
                if isinstance(e.args[0], dict) and e.args[0].get("code") == 500:
                    print(f"Server Error: {e.args[0].get('message')}. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(delay)
                else:
                    raise  # Re-raise non-server errors
        raise ValueError("Max retries reached. Unable to invoke API.")
