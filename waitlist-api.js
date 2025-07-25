// Waitlist API utility functions

const API_BASE_URL = 'http://localhost:8000'; // Change this to your production URL

/**
 * Submit an email to the waitlist
 * @param {string} email - The email address to add to the waitlist
 * @returns {Promise<Object>} - Response from the API
 */
export const submitToWaitlist = async (email) => {
  try {
    const response = await fetch(`${API_BASE_URL}/waitlist/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to submit to waitlist');
    }

    return data;
  } catch (error) {
    console.error('Error submitting to waitlist:', error);
    throw error;
  }
};

/**
 * Validate email format
 * @param {string} email - The email to validate
 * @returns {boolean} - True if email is valid
 */
export const validateEmail = (email) => {
  // Check if email is empty
  if (!email || email.trim() === '') {
    return false;
  }
  
  // Check if email contains @ symbol
  if (!email.includes('@')) {
    return false;
  }
  
  // Check if email contains . symbol
  if (!email.includes('.')) {
    return false;
  }
  
  // Check if email is 'noemail' or contains 'noemail'
  if (email.toLowerCase() === 'noemail' || email.toLowerCase().includes('noemail')) {
    return false;
  }
  
  // Basic email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Handle waitlist form submission with validation
 * @param {string} email - The email to submit
 * @param {Function} onSuccess - Callback for successful submission
 * @param {Function} onError - Callback for errors
 */
export const handleWaitlistSubmission = async (email, onSuccess, onError) => {
  // Validate email
  if (!email || !validateEmail(email)) {
    onError('Please enter a valid email address');
    return;
  }

  try {
    const result = await submitToWaitlist(email);
    onSuccess(result.message);
  } catch (error) {
    onError(error.message || 'Failed to submit to waitlist. Please try again.');
  }
}; 