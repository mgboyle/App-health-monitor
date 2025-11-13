# App Health Monitor Documentation

Welcome to the comprehensive documentation for App Health Monitor!

## 📚 Documentation Overview

This documentation is built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## 🚀 Quick Links

- **[Home](index.md)** - Documentation home
- **[Quick Start](user-guide/quick-start.md)** - Get up and running quickly
- **[API Reference](api/rest-api.md)** - Complete API documentation
- **[Contributing](developer-guide/contributing.md)** - Contribution guidelines

## 📖 Documentation Structure

### User Documentation
- **[Quick Start Guide](user-guide/quick-start.md)** - Get started in minutes
- **[Installation Guide](user-guide/installation.md)** - Detailed installation instructions
- **[Configuration Guide](user-guide/configuration.md)** - All configuration options
- **[Using the Dashboard](user-guide/dashboard.md)** - Dashboard features and navigation
- **[Managing Endpoints](user-guide/managing-endpoints.md)** - Endpoint configuration
- **[Viewing Logs](user-guide/logs.md)** - Health check history and logs
- **[Troubleshooting Guide](user-guide/troubleshooting.md)** - Common issues and solutions

### Developer Documentation
- **[Architecture Overview](developer-guide/architecture.md)** - System architecture and design
- **[Database Schema](developer-guide/database-schema.md)** - Database design and ERD
- **[Development Setup](developer-guide/development-setup.md)** - Set up dev environment
- **[Contributing Guide](developer-guide/contributing.md)** - How to contribute
- **[Testing Guide](developer-guide/testing.md)** - Testing practices and guidelines

### API Reference
- **[API Overview](api/overview.md)** - High-level API introduction
- **[REST API Reference](api/rest-api.md)** - Detailed endpoint documentation
- **[OpenAPI Specification](api/openapi.md)** - OpenAPI/Swagger specification

### Deployment Guides
- **[Production Best Practices](deployment/production.md)** - Production deployment guide
- **[Docker Deployment](deployment/docker.md)** - Container deployment
- **[Security Hardening](deployment/security.md)** - Security best practices
- **[Backup & Recovery](deployment/backup.md)** - Data protection strategies

### Roadmap
- **[Product Roadmap](roadmap.md)** - Planned features and improvements

## 🛠️ Building the Documentation

### Prerequisites

```bash
# Install documentation dependencies
pip install -r requirements-dev.txt
```

### Local Development

Serve the documentation locally with live reload:

```bash
# Start development server
mkdocs serve

# Open browser
open http://localhost:8000
```

The documentation will automatically reload when you make changes.

### Building Static Site

Generate static HTML files:

```bash
# Build documentation
mkdocs build

# Output is in site/ directory
ls site/
```

### Deploying to GitHub Pages

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy
```

This will build the documentation and push it to the `gh-pages` branch.

## 📝 Contributing to Documentation

We welcome documentation improvements! Here's how to contribute:

### 1. Find or Create an Issue

- Check existing [documentation issues](https://github.com/mgboyle/App-health-monitor/labels/documentation)
- Create a new issue for significant changes

### 2. Make Your Changes

Documentation is written in Markdown and located in the `docs/` directory:

```
docs/
├── index.md                    # Home page
├── user-guide/
│   ├── quick-start.md
│   ├── installation.md
│   └── ...
├── developer-guide/
│   ├── architecture.md
│   └── ...
├── api/
│   └── rest-api.md
└── deployment/
    └── docker.md
```

### 3. Preview Your Changes

```bash
mkdocs serve
```

### 4. Submit a Pull Request

Follow the [Contributing Guide](developer-guide/contributing.md) for the PR process.

## 📚 Documentation Standards

### Markdown Style

- Use headers hierarchically (# for title, ## for sections, ### for subsections)
- Use code blocks with language hints: ` ```python ` 
- Use admonitions for important notes:
  ```markdown
  !!! note "Note Title"
      Note content here
  ```

### Writing Style

- **Clear and concise** - Get to the point quickly
- **Step-by-step** - Break complex tasks into steps
- **Examples** - Include practical examples
- **Screenshots** - Add screenshots for UI changes
- **Links** - Link to related documentation

### Code Examples

Always include:
- Language specification in code blocks
- Comments for complex code
- Expected output where relevant
- Error handling

Example:
````markdown
```bash
# Start the application
python run.py

# Expected output:
# * Running on http://127.0.0.1:5000
```
````

## 🎨 MkDocs Features

### Admonitions

```markdown
!!! note "This is a note"
    Note content

!!! warning "Important"
    Warning content

!!! tip "Pro Tip"
    Tip content

!!! danger "Critical"
    Danger content
```

### Code Highlighting

```markdown
```python
def hello_world():
    """Example function"""
    print("Hello, World!")
```
```

### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

### Tabs

```markdown
=== "Python"
    ```python
    print("Hello")
    ```

=== "JavaScript"
    ```javascript
    console.log("Hello");
    ```
```

### Task Lists

```markdown
- [x] Completed task
- [ ] Pending task
```

## 🔍 Search

The documentation includes full-text search powered by MkDocs. Use the search bar in the header to find content quickly.

## 📱 Mobile Support

The documentation is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

## 🌙 Dark Mode

Click the theme toggle in the header to switch between light and dark modes.

## 📄 License

This documentation is part of the App Health Monitor project and is licensed under the MIT License.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/mgboyle/App-health-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mgboyle/App-health-monitor/discussions)
- **Email**: See repository for contact information

## 🙏 Acknowledgments

Documentation built with:
- [MkDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)

---

**Happy documenting!** 📚✨
