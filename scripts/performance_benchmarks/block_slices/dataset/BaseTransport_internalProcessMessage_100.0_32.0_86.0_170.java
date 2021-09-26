protected void internalProcessMessage(VoidMessage message) {
        val m = message instanceof INDArrayMessage;
        /**
         * TODO: we need better isolation here
         */
        if (message instanceof PingMessage) {

            val msg = new PongMessage();
            msg.setRequestId(((PingMessage) message).getRequestId());
            sendMessage(msg, message.getOriginatorId());
            return;
        } if (message instanceof PongMessage) {

            // do nothing
        }  else if (message instanceof VoidChunk) {
            // we merge chunks to get full INDArrayMessage
            Optional<INDArrayMessage> opt = splitter.merge((VoidChunk) message, voidConfiguration.getChunksBufferSize());

            // if this chunk was the last message, we'll forward it to parameter server for actual use
            if (opt.isPresent())
                this.internalProcessMessage(opt.get());
        } else if (message instanceof INDArrayMessage) {
            // just forward message, but ONLY if it's not a Response message, since it's probably processed separately
            if (!(message instanceof ResponseMessage)) {
                // we're not applying the same message twice
                if (!historyHolder.isKnownMessageId(message.getMessageId())) {
                    forwardToParameterServer((INDArrayMessage) message);
                }
            } else {
                // in this case we store message to the map, to be fetched later
                val reply = (ResponseMessage) message;
                replies.putIfAbsent(reply.getRequestId(), reply);
            }
        } else if (message instanceof HandshakeRequest) {
            synchronized (mesh) {
                if (!mesh.get().isKnownNode(this.id())) {
                    mesh.get().getRootNode().setId(this.id);
                }
            }

            // our response
            val response = HandshakeResponse.builder()
                    .build();

            synchronized (mesh) {
                if (mesh.get().isKnownNode(message.getOriginatorId())) {
                    log.warn("Got request from known node [{}]. Remapping.", message.getOriginatorId());

                    // notifying transport implementation about node reconnect
                    onRemap(message.getOriginatorId());

                    mesh.get().remapNodeAndDownstreams(message.getOriginatorId());
                    // we say that this model has restarted
                    response.setRestart(true);
                } else {
                    // first we add new node to the mesh
                    mesh.get().addNode(message.getOriginatorId());
                    numerOfNodes.incrementAndGet();
                }

                response.setMesh(mesh.get().clone());
            }

            response.setRequestId(((HandshakeRequest) message).getRequestId());
            sendMessage(response, message.getOriginatorId());

            // update all other nodes with new mesh
            // this message is called only from  spark driver context probably
            try {
                propagateMessageDirect(new MeshUpdateMessage(mesh.get()));
            } catch (Exception e) {
                log.error("Wasn't able to propagate message from [{}]", id());
                log.error("MeshUpdateMessage propagation failed:", e);
                throw new RuntimeException(e);
            }
        } else if (message instanceof HandshakeResponse) {
            val response = (HandshakeResponse) message;
            val newMesh = response.getMesh();

            mesh.cas(null, response.getMesh());

            synchronized (mesh) {
                val v1 = mesh.get().getVersion();
                val v2 = newMesh.getVersion();

                //log.info("Starting update A on [{}]; version: [{}/{}]; size: [{}]", this.id(), v1, v2, newMesh.totalNodes());
                // we update only if new mesh is older that existing one
                if (v1 < v2)
                    mesh.set(newMesh);
            }

            // optionally calling out callback, which will happen approximately 100% of time
            if (response.isRestart()) {
                log.info("Processing restart response...");
                if (restartCallback != null) {
                    restartCallback.call(response);
                } else
                    log.warn("Got restart message from master, but there's no defined RestartCallback");
            }

            // at last step we're updating handshake flag, so we're aware of finished handshake process
            handshakeFlag.set(true);

            // in any way we're putting this message back to replies
            val reply = (ResponseMessage) message;
            replies.putIfAbsent(reply.getRequestId(), reply);

            // this is default handler for message pairs
        } else if (message instanceof ResponseMessage) {
            // in this case we store message to the map, to be fetched later
            val reply = (ResponseMessage) message;
            replies.putIfAbsent(reply.getRequestId(), reply);

        } else if (message instanceof MeshUpdateMessage) {
            val newMesh = ((MeshUpdateMessage) message).getMesh();

            mesh.cas(null, newMesh);

            synchronized (mesh) {
                val v1 = mesh.get().getVersion();
                val v2 = newMesh.getVersion();

                //log.info("Starting update B on [{}]; version: [{}/{}]; size: [{}]", this.id(), v1, v2, newMesh.totalNodes());
                // we update only if new mesh is older that existing one
                if (v1 < v2) {
                    mesh.set(newMesh);
                }
            }

            // should be out of locked block
            onMeshUpdate(newMesh);
        } else {
            if (message instanceof RequestMessage) {
                val name = message.getClass().getCanonicalName();
                val consumer = consumers.get(name);
                if (consumer == null)
                    throw new ND4JIllegalStateException("Not supported RequestMessage received: [" + message.getClass().getCanonicalName() + "]");
            } else
                throw new ND4JIllegalStateException("Unknown message received: [" + message.getClass().getCanonicalName() + "]");
        }


        if (message instanceof BroadcastableMessage) {
            // here we should propagate message down
            try {
                // we propagate message ONLY if we've already received Mesh from master
                if (numerOfNodes.get() > 0) {
                    propagateBroadcastableMessage((BroadcastableMessage) message, PropagationMode.BOTH_WAYS);
                } else {
                    log.info("Skipping broadcast due to absence of nodes in mesh");
                }
            } catch (Exception e) {
                log.error("Wasn't able to propagate message [{}] from [{}]", message.getClass().getSimpleName(), message.getOriginatorId());
                log.error("BroadcastableMessage propagation exception:", e);
                throw new RuntimeException(e);
            }
        }

        // Request messages might be sent back to ParameterServer, which will take care of processing
        if (message instanceof RequestMessage) {
            // looks for callback for a given message type
            val consumer = consumers.get(message.getClass().getCanonicalName());
            if (consumer != null) {
                try {
                    consumer.accept(message);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }