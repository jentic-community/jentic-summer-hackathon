.PHONY: setup test load-extension validate-manifest help

# Setup development environment
setup:
	@echo "🚀 Setting up Chrome Extension development environment..."
	@echo "Creating required directories..."
	mkdir -p icons/
	mkdir -p popup/
	mkdir -p background/
	mkdir -p content/
	mkdir -p lib/
	@echo "✅ Directory structure created"
	@echo ""
	@echo "Next steps:"
	@echo "1. Add extension icons to icons/ directory"
	@echo "2. Implement popup interface in popup/"
	@echo "3. Create background script in background/"
	@echo "4. Build content script in content/"
	@echo "5. Load extension in Chrome developer mode"

# Validate manifest.json
validate-manifest:
	@echo "🔍 Validating manifest.json..."
	@if [ ! -f manifest.json ]; then \
		echo "❌ manifest.json not found"; \
		exit 1; \
	fi
	@node -e "JSON.parse(require('fs').readFileSync('manifest.json', 'utf8'))" && echo "✅ manifest.json is valid JSON" || echo "❌ manifest.json has syntax errors"

# Load extension in Chrome (instructions)
load-extension:
	@echo "🌐 To load your extension in Chrome:"
	@echo "1. Open Chrome and go to chrome://extensions/"
	@echo "2. Enable 'Developer mode' in the top right"
	@echo "3. Click 'Load unpacked' and select this directory"
	@echo "4. Your extension should appear in the list"
	@echo "5. Click the extension icon in the toolbar to test popup"

# Test extension components
test:
	@echo "🧪 Extension component checklist:"
	@echo "Testing manifest.json..."
	@$(MAKE) validate-manifest
	@echo ""
	@echo "Checking required files:"
	@[ -f popup/popup.html ] && echo "✅ popup.html exists" || echo "⚠️  popup.html missing"
	@[ -f popup/popup.js ] && echo "✅ popup.js exists" || echo "⚠️  popup.js missing"
	@[ -f background/background.js ] && echo "✅ background.js exists" || echo "⚠️  background.js missing"
	@[ -f content/content.js ] && echo "✅ content.js exists" || echo "⚠️  content.js missing"
	@[ -f icons/icon16.png ] && echo "✅ icon16.png exists" || echo "⚠️  icon16.png missing"
	@echo ""
	@echo "💡 Tip: Use browser DevTools to debug each component"

# Create placeholder icons
create-icons:
	@echo "🎨 Creating placeholder icons..."
	@echo "<!-- Replace with actual icons -->" > icons/README.md
	@echo "Icon sizes needed:" >> icons/README.md
	@echo "- icon16.png (16x16px)" >> icons/README.md
	@echo "- icon48.png (48x48px)" >> icons/README.md
	@echo "- icon128.png (128x128px)" >> icons/README.md
	@echo "✅ Icon README created"

# Development tips
tips:
	@echo "💡 Chrome Extension Development Tips:"
	@echo ""
	@echo "Debugging:"
	@echo "- Right-click extension icon → 'Inspect popup' for popup debugging"
	@echo "- Go to chrome://extensions → 'background page' for background script"
	@echo "- Use F12 on web pages to debug content scripts"
	@echo ""
	@echo "Testing API Discovery:"
	@echo "- Test on sites with AJAX calls (GitHub, Reddit, news sites)"
	@echo "- Watch Network tab in DevTools to see what APIs exist"
	@echo "- Try user actions: search, click buttons, submit forms"
	@echo ""
	@echo "Common Issues:"
	@echo "- Check manifest permissions if requests are blocked"
	@echo "- Reload extension after code changes"
	@echo "- Check console for error messages"

# Help
help:
	@echo "Available commands:"
	@echo "  make setup           - Create directory structure"
	@echo "  make validate-manifest - Check manifest.json syntax"
	@echo "  make load-extension  - Instructions for loading in Chrome"
	@echo "  make test           - Test extension components"
	@echo "  make create-icons   - Create icon placeholder files"
	@echo "  make tips           - Development tips and debugging help"