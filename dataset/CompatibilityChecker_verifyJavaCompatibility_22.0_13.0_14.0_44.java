public static void verifyJavaCompatibility(String compiledVersion) {
        String runtimeVersion = System.getProperty(JAVA_VERSION);
        if (compiledVersion == null || runtimeVersion == null || compiledVersion.equals(runtimeVersion)) {
            return;
        }

        String[] compiledVersionParts = compiledVersion.split("\\.|_");
        String[] runtimeVersionParts = runtimeVersion.split("\\.|_");

        // check the major version.
        if (!compiledVersionParts[0].equals(runtimeVersionParts[0])) {
            String compiledMajorVersion = compiledVersionParts.length > 1 ? compiledVersionParts[1] : VERSION_ZERO;
            logJavaVersionMismatchError(runtimeVersion, compiledVersionParts[0], compiledMajorVersion);
            return;
        }

        // if both have only major versions, then stop checking further.
        if (compiledVersionParts.length == 1 && compiledVersionParts.length == 1) {
            return;
        }

        // if only one of them have a minor version, check whether the other one has
        // minor version as zero.
        // eg: v9 Vs v9.0.x
        if (compiledVersionParts.length == 1) {
            if (!runtimeVersionParts[1].equals(VERSION_ZERO)) {
                logJavaVersionMismatchError(runtimeVersion, compiledVersionParts[0], VERSION_ZERO);
            }
            return;
        }

        if (runtimeVersionParts.length == 1) {
            if (!compiledVersionParts[1].equals(VERSION_ZERO)) {
                logJavaVersionMismatchError(runtimeVersion, compiledVersionParts[0], compiledVersionParts[1]);
            }
            return;
        }

        // if both have minor versions, check for their equality.
        if (!compiledVersionParts[1].equals(runtimeVersionParts[1])) {
            logJavaVersionMismatchError(runtimeVersion, compiledVersionParts[0], compiledVersionParts[1]);
        }

        // ignore the patch versions.
    }