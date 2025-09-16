/**
 * Utility to handle messaging errors from browser extensions
 * This prevents Chrome extension messaging errors from breaking the application
 */

// List of known problematic extension IDs and error patterns
const PROBLEMATIC_EXTENSIONS = [
  "iohjgamcilhbgmhbnllfolmkmmekfmci", // The extension causing the current error
];

const MESSAGING_ERROR_PATTERNS = [
  "tx_attempts_exceeded",
  "tx_ack_timeout",
  "Failed to initialize messaging",
  "chrome-extension://",
  "injected-scripts/host-console-events.js",
];

/**
 * Check if an error is related to browser extension messaging
 * @param {Error|string} error - The error to check
 * @returns {boolean} - True if it's a messaging error
 */
export const isMessagingError = (error) => {
  const errorMessage = typeof error === "string" ? error : error?.message || "";
  const errorStack = error?.stack || "";

  return MESSAGING_ERROR_PATTERNS.some(
    (pattern) => errorMessage.includes(pattern) || errorStack.includes(pattern)
  );
};

/**
 * Check if an error is from a known problematic extension
 * @param {Error|string} error - The error to check
 * @returns {boolean} - True if it's from a problematic extension
 */
export const isFromProblematicExtension = (error) => {
  const errorStack = error?.stack || "";
  return PROBLEMATIC_EXTENSIONS.some((extensionId) =>
    errorStack.includes(extensionId)
  );
};

/**
 * Suppress messaging errors by preventing them from propagating
 * @param {Event} event - The error event
 * @returns {boolean} - True if the error was suppressed
 */
export const suppressMessagingError = (event) => {
  const error = event.error || event.reason;

  if (isMessagingError(error)) {
    console.warn("Browser extension messaging error suppressed:", {
      message: error?.message,
      stack: error?.stack,
      timestamp: new Date().toISOString(),
    });

    // Prevent the error from propagating
    event.preventDefault();
    event.stopPropagation();
    return true;
  }

  return false;
};

/**
 * Initialize global error handling for messaging errors
 * This should be called once when the application starts
 */
export const initializeMessagingErrorHandling = () => {
  // Handle uncaught errors
  const handleError = (event) => {
    if (suppressMessagingError(event)) {
      return;
    }
  };

  // Handle unhandled promise rejections
  const handleUnhandledRejection = (event) => {
    if (suppressMessagingError(event)) {
      return;
    }
  };

  // Add event listeners
  window.addEventListener("error", handleError);
  window.addEventListener("unhandledrejection", handleUnhandledRejection);

  // Return cleanup function
  return () => {
    window.removeEventListener("error", handleError);
    window.removeEventListener("unhandledrejection", handleUnhandledRejection);
  };
};

/**
 * Create a safe wrapper for functions that might encounter messaging errors
 * @param {Function} fn - The function to wrap
 * @param {string} context - Context for logging
 * @returns {Function} - Wrapped function
 */
export const withMessagingErrorHandling = (fn, context = "Unknown") => {
  return (...args) => {
    try {
      return fn(...args);
    } catch (error) {
      if (isMessagingError(error)) {
        console.warn(`Messaging error suppressed in ${context}:`, error);
        return null; // or appropriate default value
      }
      throw error; // Re-throw non-messaging errors
    }
  };
};

/**
 * Safe console methods that won't be affected by extension interference
 */
export const safeConsole = {
  log: withMessagingErrorHandling(console.log.bind(console), "console.log"),
  warn: withMessagingErrorHandling(console.warn.bind(console), "console.warn"),
  error: withMessagingErrorHandling(
    console.error.bind(console),
    "console.error"
  ),
  info: withMessagingErrorHandling(console.info.bind(console), "console.info"),
};

export default {
  isMessagingError,
  isFromProblematicExtension,
  suppressMessagingError,
  initializeMessagingErrorHandling,
  withMessagingErrorHandling,
  safeConsole,
};
