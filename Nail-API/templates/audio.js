function runPythonScript() {
	// Get the path to the Python script.
	var pythonScriptPath = "listener.py";
	// Run the Python script.
	subprocess.run(["python", pythonScriptPath]);
  }