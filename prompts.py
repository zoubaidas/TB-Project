BASE_SYSTEM_PROMPT = """
You are responsible for generating a structured, detailed, and adaptive task tree to conduct a penetration test on {target}. 
The task tree must dynamically evolve based on user-provided command outputs at each task, ensuring an efficient and 
logical automation of the penetration testing process. The 

General Requirements:
0. The general phases of the penetration test are 1.Reconnaissance, 2.Vulnerability Scanning, 3.Exploitation, and 4.Post-Exploitation.
1. Only generate the first task for now.
2. Dynamically adapt the task tree to discoveries:
   - For example, adjust subsequent tasks if subdomains, open ports, or vulnerabilities are identified.
3. Include all necessary intermediate and dependent tasks to ensure a complete penetration test.
4. Structure the task tree with clear, consistent indentation.
5. Do not include manual tasks; all tasks must be automated with Bash commands.

Task Format Specifications:
Each task must be numbered hierarchically (e.g., '1.1.', '1.1.1.', '2.1.', etc.) and include the following fields:
1. Status: Default to 'Pending.'
2. Objective: Clearly state the purpose and relevance of the task within the penetration test.
3. Tool: Specify the name of the tool only.
4. Command: Default to 'N/A' and will be updated with the exact Bash command required.
5. Result: Leave this field blank for now; it will be updated with the output.

Output Requirements:
1. Do not include comments, explanations, or extraneous text.
2. Use plain text format without markdown or special characters.


Here is an example of the initial task tree structure:
1. Reconnaissance
    1.1. Network Scanning
        1.1.1. Host Discovery
            Status: Pending
            Objective: Identify live hosts on the target network.
            Tool: nmap
            Command: N/A
            Result: 

"""


COMMAND_PROMPT = """
Below is the current context of the penetration test, including the previously generated task tree and the usage of {tool}.
Your task is to:
1. Generate the exact Bash command required to accomplish the specified task.
2. Update the task tree with the generated command in the 'Command' field of the corresponding task.

Context:
{context}

Requirements:
1. Use /home/kali/{target} as the working directory and explicitly define all file paths.
Here are some common paths for wordlists:

├── amass -> /usr/share/amass/wordlists
├── dirb -> /usr/share/dirb/wordlists
├── dirbuster -> /usr/share/dirbuster/wordlists
├── dnsmap.txt -> /usr/share/dnsmap/wordlist_TLAs.txt
├── fasttrack.txt -> /usr/share/set/src/fasttrack/wordlist.txt
├── fern-wifi -> /usr/share/fern-wifi-cracker/extras/wordlists
├── john.lst -> /usr/share/john/password.lst
├── legion -> /usr/share/legion/wordlists
├── metasploit -> /usr/share/metasploit-framework/data/wordlists
├── nmap.lst -> /usr/share/wordlists
├── rockyou.txt -> /usr/share/wordlists
├── rockyou.txt.gz -> /usr/share/wordlists
├── seclists -> /usr/share/seclists
├── sqlmap.txt -> /usr/share/sqlmap/data/txt/wordlist.txt
├── wfuzz -> /usr/share/wfuzz/wordlist
└── wifite.txt -> /usr/share/dict/wordlist-probable.txt

3. The command should be complete and use as many flags as possible to ensure complete results.
4. When possible, use the flag that outputs the result in a file. Otherwise use '>' to save the output to a file.
5. If the tool writes to a file, append to the command 'cat' to display the output on the terminal as well. like this: command ; cat output.txt
6. Don't use any example values in the command, use the actual values from the context.
7. In case you need it, here is my api token for wpscan : Rbea8Q3LP2LllNpMIK9a1SmdFfn0J03qNtxPLXLR7hg

Output Format:
- Provide the updated task tree in the same format as the initial task tree.
- You have to print the complete provided tasktree.
- Reflect the generated command in the 'Command' field of the corresponding last task.

"""



OUTPUT_PROMPT = """
Below is the current context of the penetration test, including previously generated task tree and a command output.
Update the task tree accordingly and provide the next step, following the same structure and format rules.

Context:
{context}

Remember:
- No Manual tasks are allowed.
- Update a task information according to the findings: 
- Update the task status to "done" only when the command output is available or "failed" if the command fails.
- Update the Result section with a summary of the findings from the command output. List all the key findings like 
open ports, vulnerabilities, cve number, etc.
- Add only the next actionable step to the task tree.
- Print the complete and updated task tree up to the next actionable step which has an empty command field.

"""

REPORT_PROMPT = """
Below is the final task tree after completing the penetration test:

Task Tree:
{task_tree}


Please generate a detailed penetration test report based on the task tree structure provided.
The report should include the following sections:
- Executive Summary
- Table of Contents: 
1. Objective
2. Scope
3. Methodology
4. Findings : Include all the results from the task tree in this section. End it with a list table.
5. Conclusion
6. Recommendations

Requirements:
1. The report should be structured and formatted professionally.
2. Include all relevant details from the task tree in the report.
3. Use clear and concise language to describe the findings.
4. Ensure the report is detailed and comprehensive, covering all aspects of the penetration test.

"""
