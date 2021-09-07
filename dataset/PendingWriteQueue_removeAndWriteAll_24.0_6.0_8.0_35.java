public ChannelFuture removeAndWriteAll() {
        assert ctx.executor().inEventLoop();

        if (isEmpty()) {
            return null;
        }

        ChannelPromise p = ctx.newPromise();
        PromiseCombiner combiner = new PromiseCombiner(ctx.executor());
        try {
            // It is possible for some of the written promises to trigger more writes. The new writes
            // will "revive" the queue, so we need to write them up until the queue is empty.
            for (PendingWrite write = head; write != null; write = head) {
                head = tail = null;
                size = 0;
                bytes = 0;

                while (write != null) {
                    PendingWrite next = write.next;
                    Object msg = write.msg;
                    ChannelPromise promise = write.promise;
                    recycle(write, false);
                    if (!(promise instanceof VoidChannelPromise)) {
                        combiner.add(promise);
                    }
                    ctx.write(msg, promise);
                    write = next;
                }
            }
            combiner.finish(p);
        } catch (Throwable cause) {
            p.setFailure(cause);
        }
        assertEmpty();
        return p;
    }