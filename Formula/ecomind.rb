class Ecomind < Formula
  desc "EcoMind - AI E-commerce Expert Dialogue System"
  homepage "https://github.com/ghostGDR/gsd_test"
  url "https://github.com/ghostGDR/gsd_test/archive/refs/tags/v1.0.0.tar.gz"
  # sha256 "actual_sha256_here"
  license "MIT"

  depends_on "node"
  depends_on "python@3.10"

  def install
    # Install all files to libexec
    libexec.install Dir["*"]
    
    # Install npm dependencies
    cd libexec do
      system "npm", "install", *Language::Node.local_npm_install_args
    end

    # Create the executable wrapper
    (bin/"ecomind").write_env_script libexec/"bin/cli.js", :PATH => "#{Formula["node"].opt_bin}:#{Formula["python@3.10"].opt_bin}:$PATH"
  end

  def caveats
    <<~EOS
      EcoMind requires a Python environment to run its RAG engine.
      On first run, it will attempt to create a virtual environment and install dependencies.
      Make sure you have access to the internet.
    EOS
  end

  test do
    # Simple test to see if the command exists
    assert_match "ecomind", shell_output("#{bin}/ecomind --help")
  end
end
