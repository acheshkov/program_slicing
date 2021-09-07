static String parseFieldsInGeneralPurpose(String rawInformation) throws NotFoundException {
    if (rawInformation.isEmpty()) {
      return null;
    }

    // Processing 2-digit AIs

    if (rawInformation.length() < 2) {
      throw NotFoundException.getNotFoundInstance();
    }

    String firstTwoDigits = rawInformation.substring(0, 2);

    for (Object[] dataLength : TWO_DIGIT_DATA_LENGTH) {
      if (dataLength[0].equals(firstTwoDigits)) {
        if (dataLength[1] == VARIABLE_LENGTH) {
          return processVariableAI(2, (Integer) dataLength[2], rawInformation);
        }
        return processFixedAI(2, (Integer) dataLength[1], rawInformation);
      }
    }

    if (rawInformation.length() < 3) {
      throw NotFoundException.getNotFoundInstance();
    }

    String firstThreeDigits = rawInformation.substring(0, 3);

    for (Object[] dataLength : THREE_DIGIT_DATA_LENGTH) {
      if (dataLength[0].equals(firstThreeDigits)) {
        if (dataLength[1] == VARIABLE_LENGTH) {
          return processVariableAI(3, (Integer) dataLength[2], rawInformation);
        }
        return processFixedAI(3, (Integer) dataLength[1], rawInformation);
      }
    }


    for (Object[] dataLength : THREE_DIGIT_PLUS_DIGIT_DATA_LENGTH) {
      if (dataLength[0].equals(firstThreeDigits)) {
        if (dataLength[1] == VARIABLE_LENGTH) {
          return processVariableAI(4, (Integer) dataLength[2], rawInformation);
        }
        return processFixedAI(4, (Integer) dataLength[1], rawInformation);
      }
    }

    if (rawInformation.length() < 4) {
      throw NotFoundException.getNotFoundInstance();
    }

    String firstFourDigits = rawInformation.substring(0, 4);

    for (Object[] dataLength : FOUR_DIGIT_DATA_LENGTH) {
      if (dataLength[0].equals(firstFourDigits)) {
        if (dataLength[1] == VARIABLE_LENGTH) {
          return processVariableAI(4, (Integer) dataLength[2], rawInformation);
        }
        return processFixedAI(4, (Integer) dataLength[1], rawInformation);
      }
    }

    throw NotFoundException.getNotFoundInstance();
  }