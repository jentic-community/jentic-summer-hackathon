# Agent Behavior Modification System - Web Frontend

A modern, responsive web interface for the Agent Behavior Modification System that provides an intuitive way to manage AI agent behavior policies through a beautiful UI.

## Features

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Beautiful Interface**: Modern gradient backgrounds, smooth animations, and intuitive navigation
- **Real-time Updates**: Live dashboard with instant policy and audit log updates

### 📊 **Dashboard Overview**
- **Statistics Cards**: Active policies, recent actions, blocked/allowed actions
- **Quick Actions**: Easy access to common tasks
- **Tabbed Interface**: Organized sections for policies, audit logs, agent status, and analytics

### 🛡️ **Policy Management**
- **Visual Policy Cards**: Clear display of all active policies with type indicators
- **Easy Creation**: Intuitive forms for different policy types
- **Natural Language**: Create policies using plain English descriptions
- **Real-time Editing**: Modify or remove policies instantly

### 🔍 **Audit & Monitoring**
- **Comprehensive Audit Log**: Track all agent actions and policy decisions
- **Filtering Options**: View blocked, allowed, or all actions
- **Agent Status**: Monitor agent health and recent activity
- **Analytics**: Visual charts showing action distribution and policy effectiveness

### 🚀 **Demo Scenarios**
- **Pre-built Demos**: Test different policy configurations
- **Conflict Resolution**: See how the system handles conflicting policies
- **Security Levels**: Understand different security configurations

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
python server.py
```

### 3. Open Your Browser
Navigate to: `http://localhost:5000`

## Usage Guide

### Creating Policies

#### Method 1: Form-based Creation
1. Click **"Add Policy"** button
2. Select policy type (Time-based, User-based, Action-based, Content-based)
3. Fill in the required fields
4. Click **"Add Policy"**

#### Method 2: Natural Language
1. Click **"Natural Language"** button
2. Describe your policy in plain English
3. Examples:
   - "Block all email sending operations"
   - "Only allow operations during business hours"
   - "Prevent deletion of important files"

### Testing Agent Goals
1. Click **"Test Agent Goal"** button
2. Enter a goal for the agent
3. See real-time policy evaluation results
4. View the decision in the audit log

### Running Demos
1. Click **"Run Demos"** button
2. Choose a demo scenario:
   - **Basic**: Time and action restrictions
   - **Security**: High-security configurations
   - **Conflicts**: Conflicting policy scenarios
   - **Content**: Pattern-based filtering

### Monitoring System
- **Policies Tab**: View and manage all active policies
- **Audit Log Tab**: Monitor all agent actions and decisions
- **Agent Status Tab**: Check agent health and recent activity
- **Analytics Tab**: View system performance metrics

## API Endpoints

The frontend includes a REST API for programmatic access:

### System Status
- `GET /api/status` - Get system overview

### Policy Management
- `GET /api/policies` - List all policies
- `POST /api/policies` - Create new policy
- `DELETE /api/policies/<id>` - Remove policy

### Goal Testing
- `POST /api/test-goal` - Test agent goal against policies

### Natural Language
- `POST /api/natural-language` - Create policy from text

### Demo Scenarios
- `POST /api/demo/<type>` - Run demo scenarios

## Technical Details

### Frontend Technologies
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Flexbox and Grid
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Font Awesome**: Beautiful icons
- **Google Fonts**: Inter font family

### Backend Technologies
- **Flask**: Lightweight web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Python**: Integration with behavior modification system

### Key Features
- **No Framework Dependencies**: Pure HTML/CSS/JS for maximum compatibility
- **Progressive Enhancement**: Works without JavaScript (basic functionality)
- **Accessibility**: ARIA labels and keyboard navigation
- **Mobile-First**: Responsive design from the ground up

## Customization

### Styling
- Modify `styles.css` to change colors, fonts, and layout
- CSS variables for easy theming
- Modular CSS structure for easy maintenance

### Functionality
- Extend `script.js` for additional features
- Add new API endpoints in `server.py`
- Integrate with external systems via API

### Integration
- Connect to your existing behavior modification system
- Add authentication and user management
- Integrate with monitoring and logging systems

## Troubleshooting

### Common Issues

**Server won't start**
- Check if port 5000 is available
- Ensure all dependencies are installed
- Verify Python version (3.7+ required)

**Policies not working**
- Check browser console for JavaScript errors
- Verify API endpoints are responding
- Ensure behavior modification system is properly imported

**Styling issues**
- Clear browser cache
- Check CSS file is loading correctly
- Verify Font Awesome CDN is accessible

### Debug Mode
Run the server with debug mode for detailed error messages:
```bash
export FLASK_ENV=development
python server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This frontend is part of the Agent Behavior Modification System and follows the same license as the main project.
