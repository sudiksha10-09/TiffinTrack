# 🤝 Contributing to TiffinTrack

Thank you for your interest in contributing to TiffinTrack! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- Basic knowledge of Flask, SQLAlchemy, and HTML/CSS/JavaScript

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/TiffinTrack.git
   cd TiffinTrack
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.create_all(); seed_initial_data()"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

### Project Structure
```
TiffinTrack/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── migrations/        # Database migrations
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── README.md         # Project documentation
```

### Database Changes
- Use Flask-Migrate for schema changes
- Test migrations thoroughly
- Include both upgrade and downgrade paths

### Frontend Guidelines
- Use responsive design principles
- Follow existing CSS patterns in `static/css/main.css`
- Test on multiple screen sizes
- Ensure accessibility compliance

## 🐛 Bug Reports

When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, browser
- **Screenshots**: If applicable

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
Add screenshots if applicable.

**Environment**
- OS: [e.g., Windows 10]
- Python: [e.g., 3.9.0]
- Browser: [e.g., Chrome 91]
```

## ✨ Feature Requests

For new features, please:
- Check existing issues first
- Provide clear use case
- Explain the benefit
- Consider implementation complexity

### Feature Request Template
```markdown
**Feature Description**
Clear description of the feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives**
Any alternative solutions considered?
```

## 🔄 Pull Requests

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Descriptive commit messages

### PR Process
1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write clean, documented code
   - Test your changes thoroughly

3. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push to fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use descriptive title
   - Explain changes made
   - Reference related issues

### Commit Message Format
```
type(scope): description

feat: add new feature
fix: resolve bug
docs: update documentation
style: formatting changes
refactor: code restructuring
test: add tests
chore: maintenance tasks
```

## 🧪 Testing

### Manual Testing
- Test all user flows
- Check responsive design
- Verify database operations
- Test error handling

### Areas to Test
- User registration/login
- Plan selection and management
- Meal pausing functionality
- Admin dashboard features
- Billing calculations
- Mobile responsiveness

## 📚 Documentation

When contributing:
- Update README.md if needed
- Document new features
- Add inline code comments
- Update API documentation

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested

## 🎯 Priority Areas

We especially welcome contributions in:
- **Mobile UI improvements**
- **Performance optimizations**
- **Additional payment integrations**
- **Advanced reporting features**
- **API development**
- **Testing framework**
- **Documentation improvements**

## 💬 Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Email**: For security issues or private matters

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

---

Thank you for contributing to TiffinTrack! 🍱✨