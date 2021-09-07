private void generateResponseLine(MetaData.Response response, ByteBuffer header)
    {
        // Look for prepared response line
        int status = response.getStatus();
        PreparedResponse preprepared = status < __preprepared.length ? __preprepared[status] : null;
        String reason = response.getReason();
        if (preprepared != null)
        {
            if (reason == null)
                header.put(preprepared._responseLine);
            else
            {
                header.put(preprepared._schemeCode);
                header.put(getReasonBytes(reason));
                header.put(HttpTokens.CRLF);
            }
        }
        else // generate response line
        {
            header.put(HTTP_1_1_SPACE);
            header.put((byte)('0' + status / 100));
            header.put((byte)('0' + (status % 100) / 10));
            header.put((byte)('0' + (status % 10)));
            header.put((byte)' ');
            if (reason == null)
            {
                header.put((byte)('0' + status / 100));
                header.put((byte)('0' + (status % 100) / 10));
                header.put((byte)('0' + (status % 10)));
            }
            else
                header.put(getReasonBytes(reason));
            header.put(HttpTokens.CRLF);
        }
    }