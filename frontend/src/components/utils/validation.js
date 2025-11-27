/**
 * Validation utility functions for form inputs
 * Provides reusable validation logic for common field types
 */

/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidEmail = (email) => {
  if (!email) return false;
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email.trim());
};

/**
 * Validate phone number format
 * Accepts various formats: 123-456-7890, (123) 456-7890, 123.456.7890, 1234567890
 * @param {string} phone - Phone number to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidPhoneNumber = (phone) => {
  if (!phone) return false;
  // Remove all non-digit characters for validation
  const digitsOnly = phone.replace(/\D/g, '');
  // Check if it has 10 or 11 digits (with or without country code)
  return digitsOnly.length >= 10 && digitsOnly.length <= 11;
};

/**
 * Validate numeric value
 * @param {string|number} value - Value to validate
 * @returns {boolean} - True if valid number, false otherwise
 */
export const isValidNumber = (value) => {
  if (value === '' || value === null || value === undefined) return false;
  return !isNaN(parseFloat(value)) && isFinite(value);
};

/**
 * Validate positive number
 * @param {string|number} value - Value to validate
 * @returns {boolean} - True if valid positive number, false otherwise
 */
export const isValidPositiveNumber = (value) => {
  if (!isValidNumber(value)) return false;
  return parseFloat(value) > 0;
};

/**
 * Validate decimal places
 * @param {string|number} value - Value to validate
 * @param {number} maxDecimals - Maximum number of decimal places allowed
 * @returns {boolean} - True if valid, false otherwise
 */
export const hasValidDecimals = (value, maxDecimals = 2) => {
  if (!isValidNumber(value)) return false;
  const valueStr = value.toString();
  const decimalIndex = valueStr.indexOf('.');
  if (decimalIndex === -1) return true; // No decimals
  const decimals = valueStr.substring(decimalIndex + 1);
  return decimals.length <= maxDecimals;
};

/**
 * Validate year
 * @param {string|number} year - Year to validate
 * @param {number} minYear - Minimum valid year (default: 1900)
 * @param {number} maxYear - Maximum valid year (default: current year + 1)
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidYear = (year, minYear = 1900, maxYear = new Date().getFullYear() + 1) => {
  if (!isValidNumber(year)) return false;
  const yearNum = parseInt(year);
  return yearNum >= minYear && yearNum <= maxYear;
};

/**
 * Validate rating (1-5 scale)
 * @param {string|number} rating - Rating to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidRating = (rating) => {
  if (!isValidNumber(rating)) return false;
  const ratingNum = parseInt(rating);
  return ratingNum >= 1 && ratingNum <= 5;
};

/**
 * Validate required field
 * @param {string} value - Value to validate
 * @returns {boolean} - True if not empty, false otherwise
 */
export const isRequired = (value) => {
  if (value === null || value === undefined) return false;
  return value.toString().trim().length > 0;
};

/**
 * Validate datetime is in the past
 * @param {string} datetime - Datetime string to validate
 * @returns {boolean} - True if in the past, false otherwise
 */
export const isInPast = (datetime) => {
  if (!datetime) return false;
  const date = new Date(datetime);
  return date < new Date();
};

/**
 * Validate datetime is in the future
 * @param {string} datetime - Datetime string to validate
 * @returns {boolean} - True if in the future, false otherwise
 */
export const isInFuture = (datetime) => {
  if (!datetime) return false;
  const date = new Date(datetime);
  return date > new Date();
};

/**
 * Validate that end datetime is after start datetime
 * @param {string} startDatetime - Start datetime string
 * @param {string} endDatetime - End datetime string
 * @returns {boolean} - True if end is after start, false otherwise
 */
export const isAfter = (startDatetime, endDatetime) => {
  if (!startDatetime || !endDatetime) return false;
  const start = new Date(startDatetime);
  const end = new Date(endDatetime);
  return end > start;
};

/**
 * Format error message for foreign key constraint violations
 * @param {string} errorMessage - Raw error message from backend
 * @returns {string} - User-friendly error message
 */
export const formatForeignKeyError = (errorMessage) => {
  if (!errorMessage) return 'An error occurred';
  
  const lowerMsg = errorMessage.toLowerCase();
  
  if (lowerMsg.includes('foreign key') || lowerMsg.includes('constraint')) {
    if (lowerMsg.includes('customer')) {
      return 'Cannot delete this customer because they have associated rides. Please delete the rides first.';
    } else if (lowerMsg.includes('driver')) {
      return 'Cannot delete this driver because they have associated vehicles or rides. Please delete those records first.';
    } else if (lowerMsg.includes('vehicle')) {
      return 'Cannot delete this vehicle because it has associated rides. Please delete the rides first.';
    } else if (lowerMsg.includes('location')) {
      return 'Cannot delete this location because it is used in existing rides. Please delete those rides first.';
    } else if (lowerMsg.includes('ride')) {
      return 'Cannot delete this ride because it has associated payments or ratings. Please delete those records first.';
    }
    return 'Cannot delete this record because it is referenced by other records. Please delete the dependent records first.';
  }
  
  if (lowerMsg.includes('unique') || lowerMsg.includes('duplicate')) {
    return 'This value already exists in the database. Please use a different value.';
  }
  
  return errorMessage;
};

/**
 * Get user-friendly error message
 * @param {object} error - Error object from API call
 * @returns {string} - User-friendly error message
 */
export const getErrorMessage = (error) => {
  if (!error) return 'An unexpected error occurred';
  
  // If error has a message property
  if (error.message) {
    return formatForeignKeyError(error.message);
  }
  
  // If error is a string
  if (typeof error === 'string') {
    return formatForeignKeyError(error);
  }
  
  // If error has response data
  if (error.response && error.response.data) {
    if (error.response.data.error) {
      return formatForeignKeyError(error.response.data.error);
    }
    if (error.response.data.message) {
      return formatForeignKeyError(error.response.data.message);
    }
  }
  
  return 'An unexpected error occurred';
};
