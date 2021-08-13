    public static String dumpQueue(Queue q) {
        StringBuilder sb=new StringBuilder();
        LinkedList values=q.values();
        if(values.isEmpty()) {
            sb.append("empty");
        }
        else {
            for(Object o: values) {
                String s=null;
                if(o instanceof Event) {
                    Event event=(Event)o;
                    int type=event.getType();
                    s=Event.type2String(type);
                    if(type == Event.VIEW_CHANGE)
                        s+=" " + event.getArg();
                    if(type == Event.MSG)
                        s+=" " + event.getArg();

                    if(type == Event.MSG) {
                        s+="[";
                        Message m=(Message)event.getArg();
                        Map<Short,Header> headers=new HashMap<Short,Header>(m.getHeaders());
                        for(Map.Entry<Short,Header> entry: headers.entrySet()) {
                            short id=entry.getKey();
                            Header value=entry.getValue();
                            String headerToString=null;
                            if(value instanceof FD.FdHeader) {
                                headerToString=value.toString();
                            }
                            else
                                if(value instanceof PingHeader) {
                                    headerToString=ClassConfigurator.getProtocol(id) + "-";
                                    if(((PingHeader)value).type == PingHeader.GET_MBRS_REQ) {
                                        headerToString+="GMREQ";
                                    }
                                    else
                                        if(((PingHeader)value).type == PingHeader.GET_MBRS_RSP) {
                                            headerToString+="GMRSP";
                                        }
                                        else {
                                            headerToString+="UNKNOWN";
                                        }
                                }
                                else {
                                    headerToString=ClassConfigurator.getProtocol(id) + "-" + (value == null ? "null" : value.toString());
                                }
                            s+=headerToString;
                            s+=" ";
                        }
                        s+="]";
                    }
                }
                else {
                    s=o.toString();
                }
                sb.append(s).append("\n");
            }
        }
        return sb.toString();
    }