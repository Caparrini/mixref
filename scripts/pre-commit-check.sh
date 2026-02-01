#!/bin/bash
# Pre-commit quality checks for mixref
# Run this before every commit to catch issues that GitHub Actions will fail on

set -e  # Exit on first error

echo "🔍 Running pre-commit quality checks..."
echo ""

# 1. Format code
echo "1️⃣  Formatting code with ruff..."
uv run ruff format src/ tests/
echo "   ✅ Code formatted"
echo ""

# 2. Verify formatting
echo "2️⃣  Verifying formatting..."
uv run ruff format --check src/ tests/
echo "   ✅ Formatting verified"
echo ""

# 3. Lint code
echo "3️⃣  Linting with ruff..."
uv run ruff check src/ tests/
echo "   ✅ Linting passed"
echo ""

# 4. Type check
echo "4️⃣  Type checking with mypy..."
uv run mypy src/
echo "   ✅ Type checking passed"
echo ""

# 5. Run tests
echo "5️⃣  Running tests..."
uv run pytest --tb=short -q
echo "   ✅ All tests passed"
echo ""

echo "🎉 All checks passed! Safe to commit and push."
echo ""
echo "Next steps:"
echo "  git add -A"
echo "  git commit -m 'your message'"
echo "  git push origin main"
