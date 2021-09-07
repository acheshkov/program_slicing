void reverseVisitLines(BCoord begin, BCoord end, boolean newlines,
            LineVisitor visitor) {

        // very similar to visitLines

        Line l;
        if (begin.row == end.row) {
            // range is on one line
            l = lineAt(begin.row);
            visitor.visit(l, begin.row, begin.col, end.col);

        } else {
            boolean cont;

            // range spans multiple lines
            l = lineAt(end.row);
            cont = visitor.visit(l, end.row, 0, end.col);
            if (!cont) {
                return;
            }

            for (int r = end.row - 1; r > begin.row; r--) {
                l = lineAt(r);
                if (newlines && !l.isWrapped()) {
                    cont = visitor.visit(l, r, 0, totalCols());
                } else {
                    cont = visitor.visit(l, r, 0, l.length() - 1);
                }
                if (!cont) {
                    return;
                }
            }

            l = lineAt(begin.row);
            if (newlines && !l.isWrapped()) {
                cont = visitor.visit(l, begin.row, begin.col, totalCols());
            } else {
                cont = visitor.visit(l, begin.row, begin.col, l.length() - 1);
            }
            if (!cont) {
                return;
            }
        }
    }