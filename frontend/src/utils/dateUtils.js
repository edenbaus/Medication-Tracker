/**
 * Utilities for date/time formatting with US East timezone
 */

/**
 * Format a date string or Date object to ISO format in US East timezone
 * @param {string|Date} date - Date to format
 * @returns {string} ISO formatted string in US East timezone
 */
export const formatToEasternISO = (date) => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  // Convert to US East timezone
  const options = {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }

  const formatter = new Intl.DateTimeFormat('en-US', options)
  const parts = formatter.formatToParts(dateObj)

  const partValues = {}
  parts.forEach(({ type, value }) => {
    partValues[type] = value
  })

  // ISO 8601 format: YYYY-MM-DDTHH:MM:SS
  return `${partValues.year}-${partValues.month}-${partValues.day}T${partValues.hour}:${partValues.minute}:${partValues.second}`
}

/**
 * Format a date to display format with US East timezone
 * @param {string|Date} date - Date to format
 * @param {Object} options - Additional formatting options
 * @returns {string} Formatted date string
 */
export const formatEasternDate = (date, options = {}) => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  const defaultOptions = {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  }

  return new Intl.DateTimeFormat('en-US', defaultOptions).format(dateObj)
}

/**
 * Format a date/time to display format with US East timezone
 * @param {string|Date} date - Date to format
 * @param {Object} options - Additional formatting options
 * @returns {string} Formatted date/time string
 */
export const formatEasternDateTime = (date, options = {}) => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  const defaultOptions = {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  }

  return new Intl.DateTimeFormat('en-US', defaultOptions).format(dateObj)
}

/**
 * Get current date/time in US East timezone as ISO string
 * @returns {string} ISO formatted string
 */
export const nowEasternISO = () => {
  return formatToEasternISO(new Date())
}

/**
 * Format date for input field (YYYY-MM-DD)
 * @param {string|Date} date - Date to format
 * @returns {string} Date in YYYY-MM-DD format
 */
export const formatDateForInput = (date) => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  const options = {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }

  const formatter = new Intl.DateTimeFormat('en-US', options)
  const parts = formatter.formatToParts(dateObj)

  const partValues = {}
  parts.forEach(({ type, value }) => {
    partValues[type] = value
  })

  return `${partValues.year}-${partValues.month}-${partValues.day}`
}

/**
 * Format datetime for input field (YYYY-MM-DDTHH:MM)
 * @param {string|Date} date - Date to format
 * @returns {string} Datetime in YYYY-MM-DDTHH:MM format
 */
export const formatDateTimeForInput = (date) => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  const options = {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }

  const formatter = new Intl.DateTimeFormat('en-US', options)
  const parts = formatter.formatToParts(dateObj)

  const partValues = {}
  parts.forEach(({ type, value }) => {
    partValues[type] = value
  })

  return `${partValues.year}-${partValues.month}-${partValues.day}T${partValues.hour}:${partValues.minute}`
}
