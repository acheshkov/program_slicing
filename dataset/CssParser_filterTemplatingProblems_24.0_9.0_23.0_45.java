private static void filterTemplatingProblems(Snapshot snapshot, List<ProblemDescription> problems) {
        MimePath mimePath = snapshot.getMimePath();
        if (mimePath.size() > 1) {
            //once the css code is embedde, we need to assume there might be sg. generated.
            //now also for plain html code as there are the html extenstions like Angular or Knockout,
            //which might contain expressions like <div style="width: {{model.getWidth()}}%">...</div>
            CharSequence text = snapshot.getText();
            ListIterator<ProblemDescription> listIterator = problems.listIterator();
            while (listIterator.hasNext()) {
                ProblemDescription p = listIterator.next();
                //XXX Idealy the filtering context should be dependent on the enclosing node
                //sg. like if there's a templating error in an declaration - search the whole
                //declaration for the templating mark. 
                //
                //Using some simplification - line context, though some nodes may span multiple
                //lines and the templating mark may not necessarily be at the line with the error.
                //
                //so find line bounds...

                //the "premature end of file" error has position pointing after the last char (=text.length())!
                if (p.getFrom() == text.length()) {
                    listIterator.remove(); //consider this as hidden error
                    continue;
                }

                int from, to;
                for (from = p.getFrom(); from > 0; from--) {
                    char c = text.charAt(from);
                    if (c == '\n') {
                        break;
                    }
                }
                for (to = p.getTo(); to < text.length(); to++) {
                    char c = text.charAt(to);
                    if (c == '\n') {
                        break;
                    }
                }
                //check if there's the templating mark (@@@) in the context
                CharSequence img = snapshot.getText().subSequence(from, to);
                if (CharSequences.indexOf(img, Constants.LANGUAGE_SNIPPET_SEPARATOR) != -1) {
                    listIterator.remove();
                }
            }
        }
    }