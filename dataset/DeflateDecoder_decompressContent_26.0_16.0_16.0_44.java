private ByteBuf decompressContent(ChannelHandlerContext ctx, WebSocketFrame msg) {
        if (decoder == null) {
            if (!(msg instanceof TextWebSocketFrame) && !(msg instanceof BinaryWebSocketFrame)) {
                throw new CodecException("unexpected initial frame type: " + msg.getClass().getName());
            }
            decoder = new EmbeddedChannel(ZlibCodecFactory.newZlibDecoder(ZlibWrapper.NONE));
        }

        boolean readable = msg.content().isReadable();
        boolean emptyDeflateBlock = EMPTY_DEFLATE_BLOCK.equals(msg.content());

        decoder.writeInbound(msg.content().retain());
        if (appendFrameTail(msg)) {
            decoder.writeInbound(FRAME_TAIL.duplicate());
        }

        CompositeByteBuf compositeDecompressedContent = ctx.alloc().compositeBuffer();
        for (;;) {
            ByteBuf partUncompressedContent = decoder.readInbound();
            if (partUncompressedContent == null) {
                break;
            }
            if (!partUncompressedContent.isReadable()) {
                partUncompressedContent.release();
                continue;
            }
            compositeDecompressedContent.addComponent(true, partUncompressedContent);
        }
        // Correctly handle empty frames
        // See https://github.com/netty/netty/issues/4348
        if (!emptyDeflateBlock && readable && compositeDecompressedContent.numComponents() <= 0) {
            // Sometimes after fragmentation the last frame
            // May contain left-over data that doesn't affect decompression
            if (!(msg instanceof ContinuationWebSocketFrame)) {
                compositeDecompressedContent.release();
                throw new CodecException("cannot read uncompressed buffer");
            }
        }

        if (msg.isFinalFragment() && noContext) {
            cleanup();
        }

        return compositeDecompressedContent;
    }