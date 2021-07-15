    public void setOption(Token key, Token value) {
        if (key.getText().equals("combineChars")) {
            if (value.getText().equals("true")) {
                if (Tool.agressive) {
                    combineChars = true;
                }
            }
            else if (value.getText().equals("false")) {
                combineChars = false;
            }
            else {
                grammar.antlrTool.error("Value for combineChars must be true or false", grammar.getFilename(), key.getLine(), key.getColumn());
            }
        } else 
        if (key.getText().equals("warnWhenFollowAmbig")) {
            if (value.getText().equals("true")) {
                warnWhenFollowAmbig = true;
            }
            else if (value.getText().equals("false")) {
                warnWhenFollowAmbig = false;
            }
            else {
                grammar.antlrTool.error("Value for warnWhenFollowAmbig must be true or false", grammar.getFilename(), key.getLine(), key.getColumn());
            }
        }
        else if (key.getText().equals("generateAmbigWarnings")) {
            if (value.getText().equals("true")) {
                generateAmbigWarnings = true;
            }
            else if (value.getText().equals("false")) {
                generateAmbigWarnings = false;
            }
            else {
                grammar.antlrTool.error("Value for generateAmbigWarnings must be true or false", grammar.getFilename(), key.getLine(), key.getColumn());
            }
        }
        else if (key.getText().equals("greedy")) {
            if (value.getText().equals("true")) {
                greedy = true;
                greedySet = true;
            }
            else if (value.getText().equals("false")) {
                greedy = false;
                greedySet = true;
            }
            else {
                grammar.antlrTool.error("Value for greedy must be true or false", grammar.getFilename(), key.getLine(), key.getColumn());
            }
        }
        else {
            grammar.antlrTool.error("Invalid subrule option: " + key.getText(), grammar.getFilename(), key.getLine(), key.getColumn());
        }
    }