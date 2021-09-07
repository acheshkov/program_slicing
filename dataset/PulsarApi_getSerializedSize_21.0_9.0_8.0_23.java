public int getSerializedSize() {
      int size = memoizedSerializedSize;
      if (size != -1) return size;
    
      size = 0;
      if (((bitField0_ & 0x00000001) == 0x00000001)) {
        size += org.apache.pulsar.shaded.com.google.protobuf.v241.CodedOutputStream
          .computeBytesSize(1, getNameBytes());
      }
      if (((bitField0_ & 0x00000002) == 0x00000002)) {
        size += org.apache.pulsar.shaded.com.google.protobuf.v241.CodedOutputStream
          .computeBytesSize(3, schemaData_);
      }
      if (((bitField0_ & 0x00000004) == 0x00000004)) {
        size += org.apache.pulsar.shaded.com.google.protobuf.v241.CodedOutputStream
          .computeEnumSize(4, type_.getNumber());
      }
      for (int i = 0; i < properties_.size(); i++) {
        size += org.apache.pulsar.shaded.com.google.protobuf.v241.CodedOutputStream
          .computeMessageSize(5, properties_.get(i));
      }
      memoizedSerializedSize = size;
      return size;
    }