#!/usr/bin/env node
/**
 * MLXMate Installation Script
 * Handles Python dependencies and setup with conda support
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Installing MLXMate...');

// Check if conda is available
function checkConda() {
    try {
        execSync('conda --version', { stdio: 'pipe' });
        console.log('✅ Conda found');
        return true;
    } catch (error) {
        console.log('🐍 Conda not found, will use pip instead');
        return false;
    }
}

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
function installDependencies(pythonCmd, useConda = false) {
    console.log('📦 Installing Python dependencies...');
    
    const requirementsPath = path.join(__dirname, '..', 'requirements.txt');
    
    if (!fs.existsSync(requirementsPath)) {
        console.error('❌ requirements.txt not found');
        process.exit(1);
    }
    
    try {
        if (useConda) {
            // Check if mlxmate environment exists
            try {
                execSync('conda env list | grep mlxmate', { stdio: 'pipe' });
                console.log('✅ Conda environment "mlxmate" already exists');
            } catch (error) {
                // Environment doesn't exist, create it
                console.log('🐍 Creating conda environment "mlxmate"...');
                execSync('conda create -n mlxmate python=3.11 -y', { stdio: 'inherit' });
                console.log('✅ Conda environment created successfully');
            }
            
            // Install dependencies in conda environment
            execSync(`conda run -n mlxmate pip install -r "${requirementsPath}"`, {
                stdio: 'inherit'
            });
            console.log('✅ Python dependencies installed successfully in conda environment');
        } else {
            execSync(`${pythonCmd} -m pip install --user -r "${requirementsPath}"`, {
                stdio: 'inherit'
            });
            console.log('✅ Python dependencies installed successfully with pip');
        }
    } catch (error) {
        console.error('❌ Failed to install Python dependencies');
        if (useConda) {
            console.log('Try running: conda run -n mlxmate pip install -r requirements.txt manually');
        } else {
            console.log('Try running: pip install --user -r requirements.txt manually');
        }
        process.exit(1);
    }
}

// Test MLX installation
function testMLX(pythonCmd, useConda = false) {
    console.log('🧪 Testing MLX installation...');
    
    try {
        if (useConda) {
            execSync('conda run -n mlxmate python -c "import mlx; import mlx_lm; print(\'✅ MLX installed successfully\')"', {
                stdio: 'inherit'
            });
        } else {
            execSync(`${pythonCmd} -c "import mlx; import mlx_lm; print('✅ MLX installed successfully')"`, {
                stdio: 'inherit'
            });
        }
    } catch (error) {
        console.error('❌ MLX installation test failed');
        if (useConda) {
            console.log('Try running: conda run -n mlxmate pip install mlx mlx-lm manually');
        } else {
            console.log('Try running: pip install mlx mlx-lm manually');
        }
        process.exit(1);
    }
}

// Main installation
function main() {
    console.log('🤖 MLXMate - Your MLX-powered coding companion');
    console.log('=============================================\n');
    
    const useConda = checkConda();
    const pythonCmd = checkPython();
    checkPip(pythonCmd);
    installDependencies(pythonCmd, useConda);
    testMLX(pythonCmd, useConda);
    
    console.log('\n🎉 Installation completed successfully!');
    console.log('\n📖 Usage:');
    console.log('  mlxmate                      # Start interactive chat');
    console.log('  mlxmate help                 # Show all commands');
    console.log('  mate                         # Short alias');
    
    if (useConda) {
        console.log('\n🐍 Conda Environment:');
        console.log('  conda activate mlxmate    # Activate the environment');
        console.log('  conda deactivate          # Deactivate the environment');
    }
    
    console.log('\n🔗 Documentation: https://github.com/eshangulati/mlxmate');
}

main();
