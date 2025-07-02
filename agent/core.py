 from .introspection import Introspection
 from fastapi.responses import JSONResponse
 from utils.feelings_loader import load_feelings, LOG_PATH

 @app.get("/reflect")
 async def reflect(trigger: str):
-    agent.react(trigger)
-    rationale = introspector.log_rationale(trigger)
+    # process the trigger through the emotion engine
+    agent.react(trigger)
+    # generate introspective rationale with intensity & felt text
+    rationale = introspector.log_rationale(trigger)
     # append to persistent log
     LOG_PATH.parent.mkdir(exist_ok=True)
-    logs = json.load(open(LOG_PATH, encoding="utf-8")) if LOG_PATH.exists() else []
+    if LOG_PATH.exists():
+        logs = json.load(open(LOG_PATH, encoding="utf-8"))
+    else:
+        logs = []
     logs.append(rationale)
-    json.dump(logs, open(LOG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
+    with open(LOG_PATH, "w", encoding="utf-8") as f:
+        json.dump(logs, f, ensure_ascii=False, indent=2)
     return rationale
