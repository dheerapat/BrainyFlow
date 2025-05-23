import asyncio
from brainyflow import Node, Flow, Memory # Import Memory
from utils import call_llm
import yaml

class ResumeParserNode(Node):
    async def prep(self, memory: Memory): # Use memory and add type hint
        """Return resume text from memory"""
        return memory.resume_text if hasattr(memory, 'resume_text') else "" # Use property access
    
    async def exec(self, resume_text):
        """Extract structured data from resume using prompt engineering"""
        prompt = f"""
Please extract the following information from this resume and format it as YAML:
- name
- email
- experience (list of positions with title and company)
- skills (list of skills)

{resume_text}

Now, output:
```yaml
name: John Doe
email: john@example.com
experience:
  - title: Software Engineer
    company: Tech Company
  - title: Developer
    company: Another Company
skills:
  - Python
  - JavaScript
  - HTML/CSS
```"""
        
        response = call_llm(prompt)
        
        # Extract YAML content from markdown code blocks
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        structured_result = yaml.safe_load(yaml_str)
        
        # Validate structure
        assert "name" in structured_result
        assert "experience" in structured_result
        assert isinstance(structured_result["experience"], list)
        assert "skills" in structured_result
        assert isinstance(structured_result["skills"], list)
        
        return structured_result
    
    async def post(self, memory: Memory, prep_res, exec_res): # Use memory and add type hint
        """Store and display structured resume data in YAML"""
        memory.structured_data = exec_res # Use property access
        
        # Print structured data in YAML format
        print("\n=== STRUCTURED RESUME DATA ===\n")
        print(yaml.dump(exec_res, sort_keys=False))
        print("\n============================\n")
        
        print("✅ Extracted basic resume information")
        
# Create and run the flow
if __name__ == "__main__":
    print("=== Simple Resume Parser - YAML Output ===\n")
    
    # Read resume text from file
    memory = {}
    with open('data.txt', 'r') as file:
        resume_text = file.read()
    memory.resume_text = resume_text # Use property access

    
    flow = Flow(start=ResumeParserNode())
    asyncio.run(flow.run(memory))
