import anthropic
import sys
import subprocess

PROMPT = """You are helping a student debug their code.
Explain the error below in plain text. Do not use markdown: no asterisks, no backticks, no headings.

Reply in exactly this format:
Meaning: what the error means, in one or two sentences.
Likely cause: the single most likely reason, based only on the error text. Quote the line from the error that shows it.
Next steps: one or two specific things to check or try.

Keep the whole reply under 120 words.

Command: {cmd}

Error output:
{err}

Normal output (may be empty):
{out}"""

def main():
    command = sys.argv[1:]
    
    if not command:
        print("Usage: python explain.py <command>")
        sys.exit()

    try: 
        result = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
            print(f"Command not found: \"{command[0]}\"")
            sys.exit(1)
    try:        
        if result.returncode != 0:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-5-5",
                max_tokens=800,
                messages=[
                    {
                        "role": "user",
                        "content": PROMPT.format(cmd=" ".join(command), err=result.stderr, out=result.stdout),
                    }
                ],
            )
            print(result.stderr)
            for block in response.content:
                if block.type == "text":
                    print(block.text)
        else:
            print(result.stdout)
    except anthropic.AuthenticationError:
        print("API key missing or invalid")
    except anthropic.APIError as e:
        print(f"The API request failed: {e}")
    
if __name__ == '__main__':
    main()