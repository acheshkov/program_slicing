public static @NonNull ErrorDescription createErrorDescription(@NonNull Severity severity, @NonNull String description, @NonNull Document doc, int lineNumber) {
        Parameters.notNull("severity", severity);
        Parameters.notNull("description", description);
        Parameters.notNull("doc", doc);
        return createErrorDescription(severity, description, new StaticFixList(), doc, lineNumber);
    }