@Override
	protected void parseInternal() throws MDException {
		cvmod.parse();
		boolean first = true;
		StringBuilder modNameBuilder = new StringBuilder();
		while ((dmang.peek() != '@') && (dmang.peek() != MDMang.DONE)) {
			MDQualification qualification = new MDQualification(dmang);
			qualification.parse();
			StringBuilder qnameBuilder = new StringBuilder();
			qualification.insert(qnameBuilder);
			if (first) {
				dmang.appendString(modNameBuilder, qnameBuilder.toString());
				first = false;
			}
			else {
				dmang.appendString(modNameBuilder, "'s `");
				dmang.appendString(modNameBuilder, qnameBuilder.toString());
			}
		}
		// The first @ terminates the qualifier, the second terminates the qualified name
		// (which is a list of qualifiers).  If there is a third, it likely terminates the
		// list of qualified names outside of the MDVxTable.
		if (dmang.peek() == '@') {
			dmang.increment();
			if (!first) {
				dmang.insertString(modNameBuilder, "{for `");
				dmang.appendString(modNameBuilder, "'}");
			}
		}
		else {
			dmang.insertString(modNameBuilder, "{for ??}");
		}
		nameModifier = modNameBuilder.toString();
	}