# Local LLM Skill - Ollama & vLLM

Run LLMs locally with no API costs.

```python
from skills.local_llm import OllamaClient, VLLMClient

client = OllamaClient()
response = client.generate("Hello world", model="llama3")
models = client.list_models()
```
