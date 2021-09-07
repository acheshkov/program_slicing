public Runnable onRequest(HeadersFrame frame)
    {
        try
        {
            MetaData.Request request = (MetaData.Request)frame.getMetaData();
            HttpFields fields = request.getFields();

            _expect100Continue = fields.contains(HttpHeader.EXPECT, HttpHeaderValue.CONTINUE.asString());

            HttpFields.Mutable response = getResponse().getHttpFields();
            if (getHttpConfiguration().getSendServerVersion())
                response.add(SERVER_VERSION);
            if (getHttpConfiguration().getSendXPoweredBy())
                response.add(POWERED_BY);

            onRequest(request);

            boolean endStream = frame.isEndStream();
            if (endStream)
            {
                onContentComplete();
                onRequestComplete();
            }

            boolean connect = request instanceof MetaData.ConnectRequest;
            _delayedUntilContent = getHttpConfiguration().isDelayDispatchUntilContent() &&
                    !endStream && !_expect100Continue && !connect;

            // Delay the demand of DATA frames for CONNECT with :protocol.
            if (!connect || request.getProtocol() == null)
                getStream().demand(1);

            if (LOG.isDebugEnabled())
            {
                Stream stream = getStream();
                LOG.debug("HTTP2 Request #{}/{}, delayed={}:{}{} {} {}{}{}",
                        stream.getId(), Integer.toHexString(stream.getSession().hashCode()),
                        _delayedUntilContent, System.lineSeparator(),
                        request.getMethod(), request.getURI(), request.getHttpVersion(),
                        System.lineSeparator(), fields);
            }

            return _delayedUntilContent ? null : this;
        }
        catch (BadMessageException x)
        {
            if (LOG.isDebugEnabled())
                LOG.debug("onRequest", x);
            onBadMessage(x);
            return null;
        }
        catch (Throwable x)
        {
            onBadMessage(new BadMessageException(HttpStatus.INTERNAL_SERVER_ERROR_500, null, x));
            return null;
        }
    }