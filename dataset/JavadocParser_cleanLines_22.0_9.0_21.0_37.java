private static List<String> cleanLines(String content) {
        String[] lines = content.split(EOL);
        if (lines.length == 0) {
            return Collections.emptyList();
        }

        List<String> cleanedLines = Arrays.stream(lines).map(l -> {
            int asteriskIndex = startsWithAsterisk(l);
            if (asteriskIndex == -1) {
                return l;
            } else {
                // if a line starts with space followed by an asterisk drop to the asterisk
                // if there is a space immediately after the asterisk drop it also
                if (l.length() > (asteriskIndex + 1)) {

                    char c = l.charAt(asteriskIndex + 1);
                    if (c == ' ' || c == '\t') {
                        return l.substring(asteriskIndex + 2);
                    }
                }
                return l.substring(asteriskIndex + 1);
            }
        }).collect(Collectors.toList());
        // lines containing only whitespace are normalized to empty lines
        cleanedLines = cleanedLines.stream().map(l -> l.trim().isEmpty() ? "" : l).collect(Collectors.toList());
        // if the first starts with a space, remove it
        if (!cleanedLines.get(0).isEmpty() && (cleanedLines.get(0).charAt(0) == ' ' || cleanedLines.get(0).charAt(0) == '\t')) {
            cleanedLines.set(0, cleanedLines.get(0).substring(1));
        }
        // drop empty lines at the beginning and at the end
        while (cleanedLines.size() > 0 && cleanedLines.get(0).trim().isEmpty()) {
            cleanedLines = cleanedLines.subList(1, cleanedLines.size());
        }
        while (cleanedLines.size() > 0 && cleanedLines.get(cleanedLines.size() - 1).trim().isEmpty()) {
            cleanedLines = cleanedLines.subList(0, cleanedLines.size() - 1);
        }
        return cleanedLines;
    }