# Contributing to Conversational LangGraph Patterns

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 🤔 How to Contribute

### Reporting Issues
- Use the GitHub Issues tracker
- Provide clear descriptions of the issue
- Include steps to reproduce for bugs
- Mention your environment (OS, Python version, etc.)

### Adding New Patterns
1. Create a new directory under `patterns/`
2. Follow the structure of existing patterns:
   ```
   patterns/your-pattern/
   ├── __init__.py
   ├── state.py      # Define your state schema
   ├── nodes.py      # Implement your nodes
   └── graph.py      # Create your graph
   ```
3. Ensure your pattern is well-documented with comments
4. Add a diagram (optional) to the `img/` folder
5. Update `langgraph.json` to register your pattern:
   ```json
   {
     "graphs": {
       "your-pattern": "patterns.your_pattern.graph:app"
     }
   }
   ```
6. Test your code thoroughly with `uv run langgraph dev`
7. Update the main README.md with information about your pattern

### Improving Existing Patterns
- Fix bugs or improve code clarity
- Enhance documentation
- Add edge cases handling
- Improve performance

## 📋 Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-pattern`)
3. Make your changes
4. Test your code
5. Commit with clear messages (`git commit -m "Add amazing pattern"`)
6. Push to your fork
7. Create a Pull Request with a clear description

## ✅ Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Use meaningful variable names
- Keep functions focused and small
- Add comments for complex logic

## 🧪 Testing

Before submitting a PR:
- Test your code locally
- Ensure it works with LangGraph Studio
- Test edge cases
- Verify the pattern solves the intended problem

## 📚 Documentation

Each pattern should include:
- Clear docstrings in the code
- Comments explaining the flow
- A README in the pattern directory (if applicable)
- References to learning materials

## 🙏 Code of Conduct

- Be respectful and inclusive
- Welcome different perspectives
- Provide constructive feedback
- Focus on the idea, not the person

Thank you for contributing! 🎉
