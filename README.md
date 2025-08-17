# MLXMate 🤖

**Your MLX-powered coding companion for Mac**

A terminal-based AI coding assistant that runs locally on Apple Silicon using MLX and Mistral. No API keys, no cloud dependencies - just pure local AI power.

## ✨ Features

- 🤖 **Local AI**: Runs completely on your Mac using Apple's MLX framework
- 🚀 **Apple Silicon Optimized**: Native performance on M1/M2/M3 chips
- 🔍 **Agentic Search**: Understands your entire codebase automatically
- 💻 **Interactive Chat**: Continuous conversation with your AI assistant
- 🎯 **Code Generation**: Generate, review, and refactor code
- 🔧 **Smart Analysis**: Analyze files and suggest improvements
- 📦 **One-Command Install**: Simple npm installation

## 🚀 Quick Start

### Installation

```bash
# Install MLXMate
npm install -g mlxmate

# Install Python dependencies (required)
pip3 install --user -r requirements.txt
```

### Usage

```bash
# Start interactive chat
mlxmate

# Or use the short alias
mate

# Show all commands
mlxmate help
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `mlxmate` | Start interactive chat |
| `mlxmate interactive` | Interactive mode |
| `mlxmate test` | Test MLX integration |
| `mlxmate setup` | Initial setup |
| `mlxmate search <query>` | Search codebase |
| `mlxmate analyze <file>` | Analyze a file |
| `mlxmate generate <prompt>` | Generate code |
| `mlxmate review <file>` | Review code |
| `mlxmate refactor <file>` | Refactor code |

## 🎯 Example Usage

### Interactive Chat
```bash
$ mlxmate
🤖 Loading MLX model...
✅ Model loaded successfully!
🔍 Building codebase index...
✅ Indexed 20 files

You: What is this project about?
🤖 Thinking...

╭─ MLX Assistant ─╮
│ Based on the codebase analysis, this appears to be a Python web application... │
╰──────────────────╯

You: Generate a function to parse JSON data
🤖 Thinking...

╭─ MLX Assistant ─╮
│ Here's a robust JSON parsing function:                    │
│                                                          │
│ def parse_json_data(json_string):                        │
│     try:                                                 │
│         return json.loads(json_string)                   │
│     except json.JSONDecodeError as e:                    │
│         raise ValueError(f"Invalid JSON: {e}")           │
╰─────────────────────────╯
```

### Code Generation
```bash
mlxmate generate "Create a Python function to calculate fibonacci numbers"
```

### Code Review
```bash
mlxmate review myfile.py
```

## 🔧 Requirements

- **macOS** with Apple Silicon (M1/M2/M3)
- **Python 3.8+**
- **Node.js 14+** (for npm installation)

## 📦 What's Included

- **MLX Framework**: Apple's machine learning framework
- **Mistral Model**: High-quality 7B parameter model
- **Codebase Analyzer**: Intelligent code understanding
- **Rich Terminal UI**: Beautiful, responsive interface
- **Agentic Search**: Semantic codebase search

## 🎉 Why MLXMate?

- **🔒 Privacy**: Everything runs locally on your machine
- **⚡ Speed**: Native Apple Silicon performance
- **💰 Free**: No API costs or subscriptions
- **🎯 Accurate**: Context-aware responses about your codebase
- **🛠️ Powerful**: Full coding assistant capabilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

---

**Made with ❤️ for Mac developers**
