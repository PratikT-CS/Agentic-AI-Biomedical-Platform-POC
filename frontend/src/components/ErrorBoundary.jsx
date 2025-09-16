import React from 'react';
import styled from 'styled-components';
import { AlertTriangle, RefreshCw } from 'lucide-react';

const ErrorContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
`;

const ErrorCard = styled.div`
  background: white;
  border-radius: 20px;
  padding: 40px;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
`;

const ErrorIcon = styled.div`
  color: #dc3545;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
`;

const ErrorTitle = styled.h1`
  color: #dc3545;
  font-size: 1.8rem;
  margin-bottom: 15px;
  font-weight: 600;
`;

const ErrorMessage = styled.p`
  color: #6c757d;
  font-size: 1.1rem;
  margin-bottom: 30px;
  line-height: 1.6;
`;

const ErrorDetails = styled.details`
  text-align: left;
  margin-bottom: 30px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #e9ecef;
`;

const ErrorSummary = styled.summary`
  cursor: pointer;
  font-weight: 500;
  color: #495057;
  margin-bottom: 10px;
`;

const ErrorStack = styled.pre`
  font-size: 0.9rem;
  color: #6c757d;
  white-space: pre-wrap;
  word-break: break-word;
  background: white;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #dee2e6;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
`;

const RetryButton = styled(Button)`
  background: #007bff;
  color: white;
  
  &:hover {
    background: #0056b3;
  }
`;

const ReloadButton = styled(Button)`
  background: #28a745;
  color: white;
  
  &:hover {
    background: #1e7e34;
  }
`;

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      isMessagingError: false 
    };
  }

  static getDerivedStateFromError(error) {
    // Check if this is a messaging-related error
    const isMessagingError = error.message && (
      error.message.includes('tx_attempts_exceeded') ||
      error.message.includes('tx_ack_timeout') ||
      error.message.includes('Failed to initialize messaging') ||
      error.message.includes('chrome-extension')
    );
    
    return { 
      hasError: true, 
      isMessagingError 
    };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log the error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // If it's a messaging error, we can try to suppress it
    if (this.state.isMessagingError) {
      console.warn('Messaging initialization error detected and handled by ErrorBoundary');
    }
  }

  handleRetry = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      isMessagingError: false 
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // If it's a messaging error, show a more user-friendly message
      if (this.state.isMessagingError) {
        return (
          <ErrorContainer>
            <ErrorCard>
              <ErrorIcon>
                <AlertTriangle size={48} />
              </ErrorIcon>
              <ErrorTitle>Browser Extension Conflict Detected</ErrorTitle>
              <ErrorMessage>
                A browser extension is trying to communicate with this application but is experiencing connection issues. 
                This doesn't affect the core functionality of the Biomedical Research Platform.
              </ErrorMessage>
              <ActionButtons>
                <RetryButton onClick={this.handleRetry}>
                  <RefreshCw size={20} />
                  Continue Anyway
                </RetryButton>
                <ReloadButton onClick={this.handleReload}>
                  <RefreshCw size={20} />
                  Reload Page
                </ReloadButton>
              </ActionButtons>
            </ErrorCard>
          </ErrorContainer>
        );
      }

      // For other errors, show the full error details
      return (
        <ErrorContainer>
          <ErrorCard>
            <ErrorIcon>
              <AlertTriangle size={48} />
            </ErrorIcon>
            <ErrorTitle>Something went wrong</ErrorTitle>
            <ErrorMessage>
              An unexpected error occurred in the application. Please try refreshing the page or contact support if the problem persists.
            </ErrorMessage>
            
            {this.state.error && (
              <ErrorDetails>
                <ErrorSummary>Error Details (Click to expand)</ErrorSummary>
                <ErrorStack>
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </ErrorStack>
              </ErrorDetails>
            )}
            
            <ActionButtons>
              <RetryButton onClick={this.handleRetry}>
                <RefreshCw size={20} />
                Try Again
              </RetryButton>
              <ReloadButton onClick={this.handleReload}>
                <RefreshCw size={20} />
                Reload Page
              </ReloadButton>
            </ActionButtons>
          </ErrorCard>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
