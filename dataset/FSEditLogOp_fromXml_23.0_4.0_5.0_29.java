@Override 
    void fromXml(Stanza st) throws InvalidXmlException {
      this.length = Integer.parseInt(st.getValue("LENGTH"));
      this.inodeId = Long.parseLong(st.getValue("INODEID"));
      this.path = st.getValue("PATH");
      this.replication = Short.parseShort(st.getValue("REPLICATION"));
      this.mtime = Long.parseLong(st.getValue("MTIME"));
      this.atime = Long.parseLong(st.getValue("ATIME"));
      this.blockSize = Long.parseLong(st.getValue("BLOCKSIZE"));

      this.clientName = st.getValue("CLIENT_NAME");
      this.clientMachine = st.getValue("CLIENT_MACHINE");
      this.overwrite = Boolean.parseBoolean(st.getValueOrNull("OVERWRITE"));
      if (st.hasChildren("BLOCK")) {
        List<Stanza> blocks = st.getChildren("BLOCK");
        this.blocks = new Block[blocks.size()];
        for (int i = 0; i < blocks.size(); i++) {
          this.blocks[i] = FSEditLogOp.blockFromXml(blocks.get(i));
        }
      } else {
        this.blocks = new Block[0];
      }
      this.permissions = permissionStatusFromXml(st);
      aclEntries = readAclEntriesFromXml(st);
      if (st.hasChildren("ERASURE_CODING_POLICY_ID")) {
        this.erasureCodingPolicyId = Byte.parseByte(st.getValue(
            "ERASURE_CODING_POLICY_ID"));
      }
      readRpcIdsFromXml(st);
    }