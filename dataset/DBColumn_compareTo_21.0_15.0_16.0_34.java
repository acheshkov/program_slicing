@Override
    public int compareTo(DBColumn refColumn) {
        if (refColumn == null) {
            return -1;
        }

        if (refColumn == this) {
            return 0;
        }

        String myName = getDisplayName();
        myName = (myName == null) ? columnName : myName;

        if (!(refColumn instanceof DBColumn)) {
            return -1;
        }

        String refName = refColumn.getName();

        // compare primary keys
        if (this.isPrimaryKey() && !refColumn.isPrimaryKey()) {
            return -1;
        } else if (!this.isPrimaryKey() && refColumn.isPrimaryKey()) {
            return 1;
        }

        // compare foreign keys
        if (this.isForeignKey() && !refColumn.isForeignKey()) {
            return -1;
        } else if (!this.isForeignKey() && refColumn.isForeignKey()) {
            return 1;
        }

        return (myName != null) ? myName.compareTo(refName) : (refName != null) ? 1 : -1;
    }