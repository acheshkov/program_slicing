@Override
  protected void doDecode(ByteArrayDecodingState decodingState) {
    int dataLen = decodingState.decodeLength;
    CoderUtil.resetOutputBuffers(decodingState.outputs,
        decodingState.outputOffsets, dataLen);

    /**
     * As passed parameters are friendly to callers but not to the underlying
     * implementations, so we have to adjust them before calling doDecodeImpl.
     */

    byte[][] bytesArrayBuffers = new byte[getNumParityUnits()][];
    byte[][] adjustedByteArrayOutputsParameter =
        new byte[getNumParityUnits()][];
    int[] adjustedOutputOffsets = new int[getNumParityUnits()];

    int[] erasedOrNotToReadIndexes =
        CoderUtil.getNullIndexes(decodingState.inputs);

    // Use the caller passed buffers in erasedIndexes positions
    for (int outputIdx = 0, i = 0;
         i < decodingState.erasedIndexes.length; i++) {
      boolean found = false;
      for (int j = 0; j < erasedOrNotToReadIndexes.length; j++) {
        // If this index is one requested by the caller via erasedIndexes, then
        // we use the passed output buffer to avoid copying data thereafter.
        if (decodingState.erasedIndexes[i] == erasedOrNotToReadIndexes[j]) {
          found = true;
          adjustedByteArrayOutputsParameter[j] = CoderUtil.resetBuffer(
              decodingState.outputs[outputIdx],
              decodingState.outputOffsets[outputIdx], dataLen);
          adjustedOutputOffsets[j] = decodingState.outputOffsets[outputIdx];
          outputIdx++;
        }
      }
      if (!found) {
        throw new HadoopIllegalArgumentException(
            "Inputs not fully corresponding to erasedIndexes in null places");
      }
    }
    // Use shared buffers for other positions (not set yet)
    for (int bufferIdx = 0, i = 0; i < erasedOrNotToReadIndexes.length; i++) {
      if (adjustedByteArrayOutputsParameter[i] == null) {
        adjustedByteArrayOutputsParameter[i] = CoderUtil.resetBuffer(
            checkGetBytesArrayBuffer(bytesArrayBuffers, bufferIdx, dataLen),
            0, dataLen);
        adjustedOutputOffsets[i] = 0; // Always 0 for such temp output
        bufferIdx++;
      }
    }

    doDecodeImpl(decodingState.inputs, decodingState.inputOffsets,
        dataLen, erasedOrNotToReadIndexes,
        adjustedByteArrayOutputsParameter, adjustedOutputOffsets);
  }