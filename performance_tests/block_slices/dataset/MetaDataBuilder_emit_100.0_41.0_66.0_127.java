public void emit(HttpField field) throws HpackException.SessionException
    {
        HttpHeader header = field.getHeader();
        String name = field.getName();
        if (name == null || name.length() == 0)
            throw new HpackException.SessionException("Header size 0");
        String value = field.getValue();
        int fieldSize = name.length() + (value == null ? 0 : value.length());
        _size += fieldSize + 32;
        if (_size > _maxSize)
            throw new HpackException.SessionException("Header size %d > %d", _size, _maxSize);

        if (field instanceof StaticTableHttpField)
        {
            StaticTableHttpField staticField = (StaticTableHttpField)field;
            switch (header)
            {
                case C_STATUS:
                    if (checkPseudoHeader(header, _status))
                        _status = staticField.getIntValue();
                    _response = true;
                    break;

                case C_METHOD:
                    if (checkPseudoHeader(header, _method))
                        _method = value;
                    _request = true;
                    break;

                case C_SCHEME:
                    if (checkPseudoHeader(header, _scheme))
                        _scheme = (HttpScheme)staticField.getStaticValue();
                    _request = true;
                    break;

                default:
                    throw new IllegalArgumentException(name);
            }
        }
        else if (header != null)
        {
            switch (header)
            {
                case C_STATUS:
                    if (checkPseudoHeader(header, _status))
                        _status = field.getIntValue();
                    _response = true;
                    break;

                case C_METHOD:
                    if (checkPseudoHeader(header, _method))
                        _method = value;
                    _request = true;
                    break;

                case C_SCHEME:
                    if (checkPseudoHeader(header, _scheme) && value != null)
                        _scheme = HttpScheme.CACHE.get(value);
                    _request = true;
                    break;

                case C_AUTHORITY:
                    if (checkPseudoHeader(header, _authority))
                    {
                        if (field instanceof HostPortHttpField)
                            _authority = (HostPortHttpField)field;
                        else if (value != null)
                            _authority = new AuthorityHttpField(value);
                    }
                    _request = true;
                    break;

                case C_PATH:
                    if (checkPseudoHeader(header, _path))
                    {
                        if (value != null && value.length() > 0)
                            _path = value;
                        else
                            streamException("No Path");
                    }
                    _request = true;
                    break;

                case C_PROTOCOL:
                    if (checkPseudoHeader(header, _protocol))
                        _protocol = value;
                    _request = true;
                    break;

                case HOST:
                    _fields.add(field);
                    break;

                case CONTENT_LENGTH:
                    _contentLength = field.getLongValue();
                    _fields.add(field);
                    break;

                case TE:
                    if ("trailers".equalsIgnoreCase(value))
                        _fields.add(field);
                    else
                        streamException("Unsupported TE value '%s'", value);
                    break;

                case CONNECTION:
                    if ("TE".equalsIgnoreCase(value))
                        _fields.add(field);
                    else
                        streamException("Connection specific field '%s'", header);
                    break;

                default:
                    if (name.charAt(0) == ':')
                        streamException("Unknown pseudo header '%s'", name);
                    else
                        _fields.add(field);
                    break;
            }
        }
        else
        {
            if (name.charAt(0) == ':')
                streamException("Unknown pseudo header '%s'", name);
            else
                _fields.add(field);
        }
    }