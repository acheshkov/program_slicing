public Collection<String> nearestLabels(LabelledDocument document, int topN) {
        if (document.getReferencedContent() != null) {
            return nearestLabels(document.getReferencedContent(), topN);
        } else
            return nearestLabels(document.getContent(), topN);
    }