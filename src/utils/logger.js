// Utility logger that only shows logs in development mode
export const devLog = (...args) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(...args);
  }
};

export const devError = (...args) => {
  if (process.env.NODE_ENV === 'development') {
    console.error(...args);
  }
};

export const devWarn = (...args) => {
  if (process.env.NODE_ENV === 'development') {
    console.warn(...args);
  }
};

// Production-safe logging (always shows)
export const prodLog = (...args) => {
  console.log(...args);
};

export const prodError = (...args) => {
  console.error(...args);
}; 