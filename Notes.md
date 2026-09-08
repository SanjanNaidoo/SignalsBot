I like the idea established by pewdiepie of taking a small/open source model and training it aggressively such that it performs significantly better in a narrow domain. 

Before we get started on any of this it would be prudent to get bench marks of all the LLMs out there including the one we aim to train.

"Pasting into the chat" via ChatGPT/Gemini/Grok's web UI is not unprompted: every web UI wraps your question in the vendor's own hidden system prompt, and several will silently use web search or tools. You'd be benchmarking their product, not their model, and you couldn't record what was actually sent. Through the API with no system prompt you get the raw model, and the run manifest records exactly what went in. That's what I'm building; it's also the only version that's reproducible.