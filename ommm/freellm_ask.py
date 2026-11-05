"""Answer one question with the FreeLLMAPI router (127.0.0.1:31415); key read from the user env var FREELLM_KEY."""
import json, os, sys, urllib.request, winreg
key = os.environ.get("FREELLM_KEY")
if not key:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        key = winreg.QueryValueEx(k, "FREELLM_KEY")[0]
for model in ("qwen3.8-max", "glm-5.3", "auto"):
    try:
        body = json.dumps({"model": model, "messages": [{"role": "user", "content": "Answer briefly for a phone call: " + " ".join(sys.argv[1:])}]}).encode()
        req = urllib.request.Request("http://127.0.0.1:31415/v1/chat/completions", body, {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        print(json.loads(urllib.request.urlopen(req, timeout=100).read())["choices"][0]["message"]["content"])
        break
    except Exception as e:  # rate limit / model down: next model
        err = e
else:
    print("The free model is not available right now.")
