import azure.functions as func
import json
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger", methods=["POST", "GET"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Simple import test for the three libraries the user asked to verify.
    libs = ["matplotlib", "psychrolib", "psychrochart"]
    results = {}
    for lib in libs:
        try:
            __import__(lib)
            results[lib] = "OK"
        except Exception as e:
            results[lib] = f"ERROR: {type(e).__name__}: {e}"

    return func.HttpResponse(json.dumps(results), mimetype="application/json", status_code=200)