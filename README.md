# Conversational LangGraph Patterns

Educational repository showcasing conversational patterns built with LangGraph. Each pattern demonstrates core concepts for building agentic conversational systems.

## 📚 Available Patterns

### 1. Booking Pattern
A conversational agent that guides users through the process of booking an appointment. The agent asks for missing information, validates availability, and confirms bookings.

- **Video Tutorial**: [Coming soon on YouTube]
- **Detailed Article**: [Coming soon on Medium]
- **Code**: `patterns/booking/src/`

**Key Concepts:**
- Incremental information gathering
- Conditional routing based on state
- Availability validation
- Confirmation handling

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/langgraph-conversational-patterns.git
cd langgraph-conversational-patterns
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running a Pattern

Each pattern can be run with LangGraph Studio or locally:

```bash
# With LangGraph Studio
langgraph up patterns/booking/src/graph.py

# Local testing
python -m patterns.booking.src.graph
```

## 🤝 Contributing

We welcome contributions! Whether you want to:
- Add new conversational patterns
- Improve existing patterns
- Fix bugs
- Enhance documentation

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## 📖 Learning Path

1. **Video**: Watch the tutorial to understand the pattern
2. **Code**: Explore the implementation in `src/`
3. **Article**: Read the detailed explanation on Medium
4. **Experiment**: Modify and extend the pattern

## 📁 Repository Structure

```
langgraph-conversational-patterns/
├── README.md                    # This file
├── CONTRIBUTING.md              # How to contribute
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
└── patterns/
    └── booking/                 # First pattern
        └── src/                 # Source code
            ├── __init__.py
            ├── state.py         # State schema
            ├── nodes.py         # Graph nodes
            └── graph.py         # Graph definition
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Questions?

If you have questions or suggestions, please open an issue on GitHub.

---

**Happy learning!** 🚀
