class Mlxmate < Formula
  desc "🤖 Your MLX-powered coding companion for Mac - AI assistant with Mistral"
  homepage "https://github.com/eshangulati/mlxmate"
  url "https://github.com/eshangulati/mlxmate.git", branch: "main"
  version "1.0.3"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Install Python dependencies
    system "pip3", "install", "-r", "requirements.txt"
    
    # Install Python modules
    libexec.install Dir["*.py"]
    libexec.install "core"
    libexec.install "ui"
    libexec.install "utils"
    libexec.install "scripts"
    
    # Create the main executable
    (bin/"mlxmate").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{libexec}:$PYTHONPATH"
      cd "#{libexec}"
      exec "#{Formula["python@3.11"].opt_bin}/python3" "#{libexec}/bin/mlxmate" "$@"
    EOS
    
    # Make the wrapper executable
    chmod 0755, bin/"mlxmate"
  end

  test do
    system "#{bin}/mlxmate", "help"
  end
end
