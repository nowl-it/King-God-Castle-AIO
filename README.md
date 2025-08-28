# Ki## ✨ Features

- 🎨 **Modern UI**: Beautiful, dark/light theme with CustomTkinter
- 🪟 **Floating Window**: Default floating mode for easy access
- 🌐 **Cross-Platform**: Runs on Windows, macOS, and Linux
- 📦 **XAPK Installer**: Main feature for installing XAPK/APK files (Default screen, no sidebar)
- 🔧 **Multiple Tools**: System tools, network utilities, security features
- ⚙️ **Configurable**: JSON-based configuration system
- 🌍 **Multi-language**: Vietnamese interface with English support
- 📱 **Responsive**: Adaptive layout for different screen sizes
- 🎛️ **Smart Layout**: Automatic sidebar hiding for focused screenstle AIO

A modern, cross-platform GUI application built with CustomTkinter. This all-in-one tool provides various utilities and features in a beautiful, floating window interface.

## ✨ Features

- 🎨 **Modern UI**: Beautiful, dark/light theme with CustomTkinter
- 🪟 **Floating Window**: Default floating mode for easy access
- 🌐 **Cross-Platform**: Runs on Windows, macOS, and Linux
- � **XAPK Installer**: Main feature for installing XAPK/APK files (Default screen)
- �🔧 **Multiple Tools**: System tools, network utilities, security features
- ⚙️ **Configurable**: JSON-based configuration system
- 🌍 **Multi-language**: Vietnamese interface with English support
- 📱 **Responsive**: Adaptive layout for different screen sizes

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)
- tkinter (usually included with Python)

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### 2. Run Application

```bash
# Using launcher script
./run.sh

# Or manually
source venv/bin/activate
python main.py
```

### 3. Build Executable (Optional)

```bash
chmod +x build.sh
./build.sh
```

## 📁 Project Structure

```
app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.sh               # Environment setup script
├── build.sh               # Build executable script
├── run.sh                 # Launcher script
├── run.bat                # Windows launcher
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── gui/               # GUI components
│   │   ├── __init__.py
│   │   └── main_window.py # Main application window
│   ├── screens/           # Application screens
│   │   ├── __init__.py
│   │   ├── base_screen.py # Base screen class
│   │   ├── home_screen.py # Home/dashboard screen
│   │   ├── tools_screen.py # Tools and utilities
│   │   └── settings_screen.py # Settings and preferences
│   └── utils/             # Utility modules
│       ├── __init__.py
│       └── config.py      # Configuration manager
├── config/                # Configuration files
│   ├── app_config.json    # Application settings
│   └── theme_config.json  # UI theme settings
└── assets/                # Resources
    ├── images/            # Images and graphics
    └── icons/             # Application icons
```

## ⚙️ Configuration

The application uses JSON configuration files for easy customization:

### `config/app_config.json`

- Application metadata
- Window settings
- Screen definitions
- Default behaviors

### `config/theme_config.json`

- Color schemes
- Font settings
- Spacing and layout
- Animation properties

## 🎯 Main Features

### 📦 XAPK Installer (Default Screen)

- **King God Castle Download**: One-click download directly from APKPure
- **Integrated apkeep Tool**: Uses powerful APK downloader for reliable downloads
- **Smart Progress Tracking**: Real-time download progress with status updates
- **Auto-folder Opening**: Downloads folder opens automatically when complete
- **Simplified Interface**: Clean 2-button design - Select XAPK and Install XAPK
- **Error Handling**: Comprehensive error messages and recovery options
- **Clean Design**: Full-width layout without sidebar for focused workflow
- **Batch Installation**: Install multiple XAPK files at once
- **Progress Tracking**: Real-time installation progress and status
- **Install Options**: Auto-install, backup APK, keep data settings

### 🔧 Tools Screen

- **System Tools**: System info, performance monitor, file manager
- **Network Tools**: Network scanner, port scanner, DNS lookup
- **Security Tools**: Password generator, hash calculator, encryption
- **Advanced Tools**: Log analyzer, database tools, API tester

### ⚙️ Settings Screen

- **Appearance**: Theme, colors, transparency, fonts
- **General**: Startup options, language selection
- **Advanced**: Performance, security, cache settings
- **About**: Version info, license, updates

## 🖥️ Platform Support

### Windows

- Tested on Windows 10/11
- Executable build with PyInstaller
- Native Windows look and feel

### macOS

- Compatible with macOS 10.14+
- App bundle creation supported
- Native macOS integration

### Linux

- Works on major distributions
- GTK/X11 compatibility
- Floating window support

## 🛠️ Development

### Adding New Screens

1. Create new screen class inheriting from `BaseScreen`
2. Implement `setup_ui()` method
3. Add screen to `MainWindow.setup_screens()`
4. Update navigation in sidebar

### Customizing Themes

- Edit `config/theme_config.json`
- Colors support hex values
- Font families can be system fonts
- Spacing uses pixel values

### Configuration Management

```python
from utils.config import config

# Get application setting
width = config.get_app_setting("window.default_width", 1200)

# Get theme setting
primary_color = config.get_theme_setting("colors.primary", "#1f538d")
```

## 📦 Dependencies

- **customtkinter**: Modern tkinter themes and widgets
- **pillow**: Image processing and display
- **packaging**: Version handling and utilities

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Make sure virtual environment is activated
2. **tkinter Missing**: Install python3-tk on Linux
3. **Build Fails**: Check PyInstaller version and dependencies
4. **Window Not Floating**: Check window manager compatibility

### Debug Mode

Run with debug output:

```bash
python main.py --debug
```

## 📄 License

MIT License - see LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test on multiple platforms
5. Submit pull request

## 🔄 Updates

Check for updates in the Settings → About section or visit the repository for the latest version.

---

**King God Castle AIO** - A powerful, beautiful, and cross-platform GUI application. 👑
