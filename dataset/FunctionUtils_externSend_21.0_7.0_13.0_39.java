public static Object externSend(ObjectValue endpointClient, Object responseValue,
                                    Object headerValues) {
        StreamObserver responseObserver = MessageUtils.getResponseObserver(endpointClient);
        Descriptors.Descriptor outputType = (Descriptors.Descriptor) endpointClient.getNativeData(GrpcConstants
                .RESPONSE_MESSAGE_DEFINITION);
        Optional<ObserverContext> observerContext =
                ObserveUtils.getObserverContextOfCurrentFrame(Scheduler.getStrand());

        if (responseObserver == null) {
            return MessageUtils.getConnectorError(new StatusRuntimeException(Status
                    .fromCode(Status.Code.INTERNAL.toStatus().getCode()).withDescription("Error while initializing " +
                            "connector. Response sender does not exist")));
        } else {
            try {
                // If there is no response message like conn -> send(), system doesn't send the message.
                if (!MessageUtils.isEmptyResponse(outputType)) {
                    //Message responseMessage = MessageUtils.generateProtoMessage(responseValue, outputType);
                    Message responseMessage = new Message(outputType.getName(), responseValue);
                    // Update response headers when request headers exists in the context.
                    HttpHeaders headers = null;
                    if (headerValues != null &&
                            (TypeChecker.getType(headerValues).getTag() == TypeTags.OBJECT_TYPE_TAG)) {
                        headers = (HttpHeaders) ((ObjectValue) headerValues).getNativeData(MESSAGE_HEADERS);
                    }
                    if (headers != null) {
                        responseMessage.setHeaders(headers);
                        headers.entries().forEach(
                                x -> observerContext.ifPresent(ctx -> ctx.addTag(x.getKey(), x.getValue())));
                    }
                    responseObserver.onNext(responseMessage);
                    observerContext.ifPresent(ctx -> ctx.addTag(TAG_KEY_GRPC_MESSAGE_CONTENT,
                            responseValue.toString()));
                }
            } catch (Exception e) {
                LOG.error("Error while sending client response.", e);
                return MessageUtils.getConnectorError(e);
            }
        }
        return null;
    }