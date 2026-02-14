"""
Tests for the shell command execution functionality.
"""
import pytest
from tools.sh_tool import run_sh_command_impl, RunShResult


class TestRunShCommandImpl:
    """Test suite for run_sh_command_impl function."""

    def test_echo_command_success(self):
        """Test that echo command executes successfully."""
        result = run_sh_command_impl("echo 'Hello, World!'")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert "Hello, World!" in result.stdout
        assert result.stderr == ""

    def test_echo_command_with_newline(self):
        """Test echo command with newline handling."""
        result = run_sh_command_impl("echo 'Test line'")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert "Test line" in result.stdout
        assert result.stderr == ""

    def test_false_command_failure(self):
        """Test that false command fails with appropriate error."""
        result = run_sh_command_impl("false")
        
        assert isinstance(result, RunShResult)
        assert result.success is False
        assert result.return_code != 0
        assert result.return_code == 1  # false typically returns 1
        assert "Error executing command" not in result.stderr

    def test_ls_command_success(self):
        """Test that ls command executes successfully."""
        result = run_sh_command_impl("ls")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert len(result.stdout) > 0  # Should have some output
        assert result.stderr == ""

    def test_pwd_command_success(self):
        """Test that pwd command executes successfully."""
        result = run_sh_command_impl("pwd")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert len(result.stdout) > 0  # Should have output
        assert result.stderr == ""

    def test_command_with_output_to_stderr(self):
        """Test command that outputs to stderr."""
        result = run_sh_command_impl("echo 'Error message' >&2")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert "Error message" in result.stderr
        assert "Error message" not in result.stdout

    def test_command_with_exit_code_nonzero(self):
        """Test command that returns non-zero exit code."""
        result = run_sh_command_impl("exit 42")
        
        assert isinstance(result, RunShResult)
        assert result.success is False
        assert result.return_code == 42

    def test_command_with_special_characters(self):
        """Test command with special characters."""
        result = run_sh_command_impl("echo 'Special: @#$%^&*()'")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert "Special: @#$%^&*()" in result.stdout

    def test_empty_command(self):
        """Test empty command string."""
        result = run_sh_command_impl("")
        
        assert isinstance(result, RunShResult)
        # Empty command with shell=True executes the shell itself, which succeeds
        assert result.success is True
        assert result.return_code == 0

    def test_complex_command_with_pipes(self):
        """Test complex command with pipes."""
        result = run_sh_command_impl("echo 'test' | grep test")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert "test" in result.stdout
        assert result.stderr == ""

    def test_command_with_multiple_outputs(self):
        """Test command that produces both stdout and stderr."""
        result = run_sh_command_impl("echo 'stdout output' 2>&1")
        
        assert isinstance(result, RunShResult)
        assert result.success is True
        assert result.return_code == 0
        assert "stdout output" in result.stdout
        # 2>&1 redirects stderr to stdout, so output is only in stdout

    def test_run_sh_result_model(self):
        """Test the RunShResult model structure."""
        result = RunShResult(
            stdout="test output",
            stderr="test error",
            return_code=0,
            success=True
        )
        
        assert result.stdout == "test output"
        assert result.stderr == "test error"
        assert result.return_code == 0
        assert result.success is True

    def test_run_sh_result_failure(self):
        """Test RunShResult with failure status."""
        result = RunShResult(
            stdout="",
            stderr="Command failed",
            return_code=1,
            success=False
        )
        
        assert result.stdout == ""
        assert result.stderr == "Command failed"
        assert result.return_code == 1
        assert result.success is False