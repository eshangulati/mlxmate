#!/usr/bin/env node
/**
 * MLXMate Installation Script
 * Handles Python dependencies and setup
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Installing MLXMate...');

// Check if Python is available
function checkPython() {
    try {
        const pythonVersion = execSync('python3 --version', { encoding: 'utf8' });
        console.log(`✅ Python found: ${pythonVersion.trim()}`);
        return 'python3';
    } catch (error) {
        try {
            const pythonVersion = execSync('python --version', { encoding: 'utf8' });
            console.log(`✅ Python found: ${pythonVersion.trim()}`);
            return 'python';
        } catch (error) {
            console.error('❌ Python not found. Please install Python 3.8+ first.');
            console.log('Visit: https://www.python.org/downloads/');
            process.exit(1);
        }
    }
}

// Check if pip is available
function checkPip(pythonCmd) {
    try {
        execSync(`${pythonCmd} -m pip --version`, { stdio: 'ignore' });
        console.log('✅ pip found');
        return true;
    } catch (error) {
        console.error('❌ pip not found. Please install pip first.');
        process.exit(1);
    }
}

// Install Python dependencies
function installDependencies(pythonCmd) {
    console.log('📦 Installing Python dependencies...');
    
    const requirementsPath = path.join(__dirname, '..', 'requirements.txt');
    
    if (!fs.existsSync(requirementsPath)) {
        console.error('❌ requirements.txt not found');
        process.exit(1);
    }
    
    try {
        // Try installing with --user first
        try {
            execSync(`${pythonCmd} -m pip install --user -r "${requirementsPath}"`, {
                stdio: 'inherit'
            });
            console.log('✅ Python dependencies installed successfully with pip --user');
        } catch (error) {
            // If --user fails, try without it
            console.log('⚠️  --user installation failed, trying without --user...');
            execSync(`${pythonCmd} -m pip install -r "${requirementsPath}"`, {
                stdio: 'inherit'
            });
            console.log('✅ Python dependencies installed successfully with pip');
        }
    } catch (error) {
        console.error('❌ Failed to install Python dependencies');
        console.log('Try running: pip install --user -r requirements.txt manually');
        process.exit(1);
    }
}

// Test MLX installation
function testMLX(pythonCmd) {
    console.log('🧪 Testing MLX installation...');
    
    try {
        execSync(`${pythonCmd} -c "import mlx; import mlx_lm; print('✅ MLX installed successfully')"`, {
            stdio: 'inherit'
        });
    } catch (error) {
        console.error('❌ MLX installation test failed');
        console.log('Try running: pip install mlx mlx-lm manually');
        process.exit(1);
    }
}

// Main installation
function main() {
    console.log('🤖 MLXMate - Your MLX-powered coding companion');
    console.log('=============================================\n');
    
    const pythonCmd = checkPython();
    checkPip(pythonCmd);
    installDependencies(pythonCmd);
    testMLX(pythonCmd);
    
    console.log('\n🎉 Installation completed successfully!');
    console.log('\n📖 Usage:');
    console.log('  mlxmate                      # Start interactive chat');
    console.log('  mlxmate help                 # Show all commands');
    console.log('  mate                         # Short alias');
    console.log('\n🔗 Documentation: https://github.com/eshangulati/mlxmate');
}

main();
