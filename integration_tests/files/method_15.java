    public static PdfPageLabelFormat[] getPageLabelFormats(PdfReader reader) {
        PdfDictionary dict = reader.getCatalog();
        PdfDictionary labels = (PdfDictionary)PdfReader.getPdfObjectRelease(dict.get(PdfName.PAGELABELS));
        if (labels == null)
            return null;
        HashMap<Integer, PdfObject> numberTree = PdfNumberTree.readTree(labels);
        Integer numbers[] = new Integer[numberTree.size()];
        numbers = numberTree.keySet().toArray(numbers);
        Arrays.sort(numbers);
        PdfPageLabelFormat[] formats = new PdfPageLabelFormat[numberTree.size()];
        String prefix;
        int numberStyle;
        int pagecount;
        for (int k = 0; k < numbers.length; ++k) {
            Integer key = numbers[k];
            PdfDictionary d = (PdfDictionary)PdfReader.getPdfObjectRelease(numberTree.get(key));
            if (d.contains(PdfName.ST)) {
                pagecount = ((PdfNumber)d.get(PdfName.ST)).intValue();
            } else {
                pagecount = 1;
            }
            if (d.contains(PdfName.P)) {
                prefix = ((PdfString)d.get(PdfName.P)).toUnicodeString();
            } else {
                prefix = "";
            }
            if (d.contains(PdfName.S)) {
                char type = ((PdfName)d.get(PdfName.S)).toString().charAt(1);
                switch(type) {
                    case 'R': numberStyle = UPPERCASE_ROMAN_NUMERALS; break;
                    case 'r': numberStyle = LOWERCASE_ROMAN_NUMERALS; break;
                    case 'A': numberStyle = UPPERCASE_LETTERS; break;
                    case 'a': numberStyle = LOWERCASE_LETTERS; break;
                    default: numberStyle = DECIMAL_ARABIC_NUMERALS; break;
                }
            } else {
                numberStyle = EMPTY;
            }
            formats[k] = new PdfPageLabelFormat(key.intValue()+1, numberStyle, prefix, pagecount);
        }
        return formats;
    }