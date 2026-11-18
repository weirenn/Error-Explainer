# Error Explainer

A command-line tool that runs your program and, if it fails, explains the error in plain English using Claude through the Anthropic API.

## How it works

1. You run your program through `explain.py`, for example `python explain.py python my_script.py`.
2. The tool runs the command with `subprocess` and captures its output.
3. If the program exits with code 0, it prints the normal output. No API call is made.
4. If it fails, it prints the original error, then sends the error text and the command to Claude (Haiku). The prompt asks for a fixed three-part reply: Meaning, Likely cause, Next steps.

It works with any language that writes its errors to stderr, such as Python and Java.

## Setup

1. Install the dependency:
   ```
   pip install -r requirements.txt
   ```
2. Set your API key as an environment variable. On Windows:
   ```
   setx ANTHROPIC_API_KEY "your-key-here"
   ```
   Then restart your terminal. The key is never stored in the code.

## Usage

```
python explain.py <command>
```

Examples:

```
python explain.py python "Example scripts/crash.py"
python explain.py java PasswordGen.java
```

## Example

Running a Java file that calls a method with the wrong arguments:

```
.\PasswordGen.java:23: error: cannot find symbol
    System.out.println(generate());
                       ^
  symbol:   method generate()
  location: class PasswordGen
1 error

Meaning: The Java compiler could not find a method named generate() that takes no arguments inside the PasswordGen class, so it cannot compile the file.

Likely cause: The error shows "symbol: method generate()" and "location: class PasswordGen", meaning no method with that exact name and parameter list is defined in that class.

Next steps: Search PasswordGen.java for the method definition and confirm the call on line 23 matches its name and parameters.
```

## Error handling

- No command given: prints a usage message.
- Command not found (for example a typo like `pyhton`): prints which command was missing.
- Invalid or missing API key, or any other API failure: prints a short message instead of a traceback.

## What I learned

- When trying to read the first index of `response.content`, the script worked when asking it to just say hello, but crashed on the first real test, which I found was due to Haiku sometimes adding a thinking block right before its actual response. This would error because the thinking block didn't have a `.text` attribute, so to account for this I looped through the blocks in `response.content` that were of type `"text"` and printed it. The code would also keep running and crash on a missing result variable, so I added `sys.exit(1)`.
- While trying to execute the script, I mistyped python, and the terminal spit out a `FileNotFoundError`, so I implemented a try/except block to pick up `FileNotFoundError`, `anthropic.AuthenticationError`, and `anthropic.APIError` errors and print a one-line message instead of a traceback.
- Haiku gave responses with markdown which only showed as asterisks and gave vague advice with a large list of possible issues, most of which weren’t the real cause, so I changed the prompt to respond in an exact three-line format with the single most likely cause and gave Haiku the command that was executed, which resulted in Haiku naming the correct cause in a much more clear and structured way.

## Limitations and next steps

- Claude only sees the error text, not the source code, so its suggested fix can point the wrong way. Next step: send the source file along with the error.
- Programs that wait for keyboard input don't work well, because the tool captures their output.
- It could run automatically when tests fail in CI.
- Test it on more real errors, such as a Python `AttributeError` from a linked list, an `IndexError`, and more Java compile errors, and check each explanation against the real cause. Tighten the prompt wherever the format drifts or the cause is wrong.
