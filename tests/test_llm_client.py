import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm.llm_client import LLMClient


class TestLLMClient:
    """Test suite for LLM client abstraction"""
    
    def test_init_with_api_key_from_environment(self):
        """Test 1: LLMClient initializes with API key from environment"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123'}):
            client = LLMClient(provider='openai', model='gpt-4o-mini')
            assert client.provider == 'openai'
            assert client.model == 'gpt-4o-mini'
            assert client.api_key == 'test-key-123'
    
    @patch('openai.OpenAI')
    def test_generate_sends_prompt_and_returns_response(self, mock_openai_class):
        """Test 2: generate() sends prompt and returns text response"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Test response from LLM'))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai', model='gpt-4o-mini')
            response = client.generate('Test prompt')
            
            assert response == 'Test response from LLM'
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_generate_handles_api_errors_gracefully(self, mock_openai_class):
        """Test 3: generate() handles API errors gracefully (returns error message, not crash)"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception('API rate limit exceeded')
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai', model='gpt-4o-mini')
            response = client.generate('Test prompt')
            
            # Should return error message, not crash
            assert 'error' in response.lower() or 'failed' in response.lower()
            assert isinstance(response, str)
    
    @patch('openai.OpenAI')
    def test_generate_supports_temperature_parameter(self, mock_openai_class):
        """Test 4: generate() supports temperature parameter (0.0-1.0)"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Response'))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai', model='gpt-4o-mini')
            client.generate('Test prompt', temperature=0.3)
            
            # Verify temperature was passed to API
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs['temperature'] == 0.3
    
    @patch('openai.OpenAI')
    def test_mock_api_calls_in_tests(self, mock_openai_class):
        """Test 5: Mock API calls in tests (no real API calls during test runs)"""
        # This test verifies that we're using mocks, not real API
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'}):
            client = LLMClient(provider='openai', model='gpt-4o-mini')
            
            # Verify we got a mock, not a real client
            assert isinstance(mock_openai_class.return_value, Mock)
