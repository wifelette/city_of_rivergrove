// Custom markdownlint rule to validate {{filled:}} form field syntax
// This will show errors directly in VSCode as you type

module.exports = {
  names: ["RIVERGROVE001", "form-field-validation"],
  description: "Validate {{filled:}} form field syntax",
  tags: ["rivergrove", "form-fields"],
  function: function rule(params, onError) {
    const lines = params.lines;
    
    lines.forEach((line, lineIndex) => {
      const lineNumber = lineIndex + 1;
      
      // Check for unclosed {{filled: tags
      if (line.includes("{{filled:")) {
        let tempLine = line;
        let columnStart = 0;
        
        while (tempLine.includes("{{filled:")) {
          const startIndex = tempLine.indexOf("{{filled:");
          const afterStart = tempLine.substring(startIndex);
          const closeIndex = afterStart.indexOf("}}");
          
          if (closeIndex === -1) {
            // Found unclosed tag
            onError({
              lineNumber: lineNumber,
              detail: "Unclosed {{filled:}} tag - missing closing }}",
              context: line.substring(Math.max(0, columnStart + startIndex - 10), 
                                      Math.min(line.length, columnStart + startIndex + 40)),
              range: [columnStart + startIndex + 1, 9] // Highlight {{filled:
            });
            break;
          }
          
          // Move past this complete tag
          columnStart += startIndex + closeIndex + 2;
          tempLine = tempLine.substring(startIndex + closeIndex + 2);
        }
      }
      
      // Check for orphaned closing brackets (warning only)
      if (line.includes("}}") && !line.includes("{{")) {
        const column = line.indexOf("}}") + 1;
        onError({
          lineNumber: lineNumber,
          detail: "Orphaned closing brackets }} without opening {{",
          context: line.substring(Math.max(0, column - 20), 
                                  Math.min(line.length, column + 20)),
          range: [column, 2]
        });
      }
      
      // Check for malformed tags (missing colon)
      if (line.includes("{{filled") && !line.includes("{{filled:")) {
        const column = line.indexOf("{{filled") + 1;
        onError({
          lineNumber: lineNumber,
          detail: "Malformed tag - should be {{filled: not {{filled",
          context: line.substring(Math.max(0, column - 10), 
                                  Math.min(line.length, column + 30)),
          range: [column, 8]
        });
      }
      
      // Check for nested tags (not supported)
      if (line.includes("{{filled:")) {
        const matches = line.match(/\{\{filled:/g);
        if (matches && matches.length > 1) {
          // Check if they're actually nested
          let openCount = 0;
          let i = 0;
          while (i < line.length) {
            if (line.substring(i, i + 9) === "{{filled:") {
              openCount++;
              if (openCount > 1) {
                onError({
                  lineNumber: lineNumber,
                  detail: "Nested {{filled:}} tags are not supported",
                  context: line,
                  range: [i + 1, 9]
                });
                break;
              }
              i += 9;
            } else if (line.substring(i, i + 2) === "}}") {
              openCount--;
              i += 2;
            } else {
              i++;
            }
          }
        }
      }
    });
  }
};