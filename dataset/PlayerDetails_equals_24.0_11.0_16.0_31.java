@Override
  public boolean equals(Object obj) {
    if (this == obj) {
      return true;
    }
    if (obj == null) {
      return false;
    }
    if (getClass() != obj.getClass()) {
      return false;
    }
    var other = (PlayerDetails) obj;
    if (bankAccountNumber == null) {
      if (other.bankAccountNumber != null) {
        return false;
      }
    } else if (!bankAccountNumber.equals(other.bankAccountNumber)) {
      return false;
    }
    if (emailAddress == null) {
      if (other.emailAddress != null) {
        return false;
      }
    } else if (!emailAddress.equals(other.emailAddress)) {
      return false;
    }
    if (phoneNumber == null) {
      return other.phoneNumber == null;
    } else {
      return phoneNumber.equals(other.phoneNumber);
    }
  }