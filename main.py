from flask import Flask, request, jsonify, render_template
import llm_gemini

app = Flask(__name__)

import re

def is_safe_code(code):
    # Basic check for dangerous patterns
    unsafe_patterns = ["import", "exec", "eval", "subprocess", "os.", "open(", "system(", "socket"]
    return not any(re.search(pattern, code.lower()) for pattern in unsafe_patterns)

@app.route("/ask", methods=["POST"])
def ask():
    user_prompt = request.json.get("prompt")
    try:
        code = llm_gemini.generate_response(user_prompt)

        if not is_safe_code(code):
            return jsonify({
                "error": "Unsafe code detected. Execution blocked."
            }), 400
        safe_globals = {"__builtins__": {"print": print, "range": range, "len": len}}
        output = {}
        exec(code, safe_globals, output)
        result = output.get("result", "No result found - store output in variable 'result'")
        return jsonify({
            "generated_code": code,
            "output": result
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


    code = llm_gemini.generate_response(user_prompt)

    try:
        output = {}
        exec(code, {"__builtins__": __builtins__}, output)
        result = output.get("result")
        if result is None:
            result = "No result found - you need to store the output in a variable called result"
        else:
            result = result + '\n' + code
    except Exception as e:
        error = str(e)
        result = f"Error executing code: {error} \n\nResponse:\n{code}"


    return jsonify({
        "generated_code": code,
        "output": result
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
