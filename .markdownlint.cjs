// Markdownlint configuration with custom rules for City of Rivergrove
const formFieldRule = require('./.markdownlint/rules/form-fields.js');

module.exports = {
  "default": true,
  "MD013": false,  // Line length
  "MD022": false,  // Headers should be surrounded by blank lines
  "MD025": false,  // Multiple top level headers
  "MD026": false,  // Trailing punctuation in header
  "MD029": false,  // Ordered list item prefix
  "MD030": false,  // Spaces after list markers
  "MD031": false,  // Fenced code blocks should be surrounded by blank lines
  "MD032": false,  // Lists should be surrounded by blank lines
  "MD036": false,  // Emphasis used instead of a header
  "MD040": false,  // Fenced code blocks should have a language specified
  "MD047": false,  // Files should end with a single newline character
  
  // Enable our custom form field validation rule
  "customRules": [formFieldRule]
};