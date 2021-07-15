    static AttributeDescriptor createAttribute(String typeSpec) throws SchemaException {
        int split = typeSpec.indexOf(":");

        String name;
        String type;
        String hint = null;

        if (split == -1) {
            name = typeSpec;
            type = "String";
        } else {
            name = typeSpec.substring(0, split);

            int split2 = typeSpec.indexOf(":", split + 1);

            if (split2 == -1) {
                type = typeSpec.substring(split + 1);
            } else {
                type = typeSpec.substring(split + 1, split2);
                hint = typeSpec.substring(split2 + 1);
            }
        }

        try {
            boolean nillable = true;
            CoordinateReferenceSystem crs = null;

            if (hint != null) {
                StringTokenizer st = new StringTokenizer(hint, ";");
                while (st.hasMoreTokens()) {
                    String h = st.nextToken();
                    h = h.trim();

                    // nillable?
                    // JD: i am pretty sure this hint is useless since the
                    // default is to make attributes nillable
                    if (h.equals("nillable")) {
                        nillable = true;
                    }
                    // spatial reference identieger?
                    if (h.startsWith("srid=")) {
                        String srid = h.split("=")[1];
                        Integer.parseInt(srid);
                        try {
                            crs = CRS.decode("EPSG:" + srid);
                        } catch (Exception e) {
                            String msg = "Error decoding srs: " + srid;
                            throw new SchemaException(msg, e);
                        }
                    }
                }
            }

            Class clazz = type(type);
            if (Geometry.class.isAssignableFrom(clazz)) {
                GeometryType at = new GeometryTypeImpl(new NameImpl(name), clazz, crs, false,
                        false, Collections.EMPTY_LIST, null, null);
                return new GeometryDescriptorImpl(at, new NameImpl(name), 0, 1, nillable, null);
            } else {
                AttributeType at = new AttributeTypeImpl(new NameImpl(name), clazz, false, false,
                        Collections.EMPTY_LIST, null, null);
                return new AttributeDescriptorImpl(at, new NameImpl(name), 0, 1, nillable, null);
            }
        } catch (ClassNotFoundException e) {
            throw new SchemaException("Could not type " + name + " as:" + type, e);
        }
    }