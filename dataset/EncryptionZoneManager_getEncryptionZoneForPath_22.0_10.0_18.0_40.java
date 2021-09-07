private EncryptionZoneInt getEncryptionZoneForPath(INodesInPath iip)
      throws  IOException{
    assert dir.hasReadLock();
    Preconditions.checkNotNull(iip);
    if (!hasCreatedEncryptionZone()) {
      return null;
    }

    int snapshotID = iip.getPathSnapshotId();
    for (int i = iip.length() - 1; i >= 0; i--) {
      final INode inode = iip.getINode(i);
      if (inode == null || !inode.isDirectory()) {
        //not found or not a directory, encryption zone is supported on
        //directory only.
        continue;
      }
      if (snapshotID == Snapshot.CURRENT_STATE_ID) {
        final EncryptionZoneInt ezi = encryptionZones.get(inode.getId());
        if (ezi != null) {
          return ezi;
        }
      } else {
        XAttr xAttr = FSDirXAttrOp.unprotectedGetXAttrByPrefixedName(
            inode, snapshotID, CRYPTO_XATTR_ENCRYPTION_ZONE);
        if (xAttr != null) {
          try {
            final HdfsProtos.ZoneEncryptionInfoProto ezProto =
                HdfsProtos.ZoneEncryptionInfoProto.parseFrom(xAttr.getValue());
            return new EncryptionZoneInt(
                inode.getId(), PBHelperClient.convert(ezProto.getSuite()),
                PBHelperClient.convert(ezProto.getCryptoProtocolVersion()),
                ezProto.getKeyName());
          } catch (InvalidProtocolBufferException e) {
            throw new IOException("Could not parse encryption zone for inode "
                + iip.getPath(), e);
          }
        }
      }
    }
    return null;
  }