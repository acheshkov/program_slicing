protected final static org.w3c.dom.Element delegateWrite(org.w3c.dom.Document doc, Object obj) throws java.io.IOException, org.w3c.dom.DOMException {
        // first lookup a cache of already written objects to prevent
        // storing of the same instance multiple times.
        CacheRec cache = setCache(doc, obj);
        if (cache.used) {
            return writeReference(doc, cache);
        }
        
        ConvertorResolver res = ConvertorResolver.getDefault();
        Class<?> clazz = obj.getClass();
        Convertor c = res.getConvertor(clazz);
        if (c == null) {
            throw new IOException("Convertor not found for object: " + obj); // NOI18N
        }
        
        org.w3c.dom.Element el;
        if (c instanceof DOMConvertor) {
            DOMConvertor dc = (DOMConvertor) c;
            el = doc.createElement(dc.rootElement);
            dc.writeElement(doc, el, obj);
            if (el.getAttribute(ATTR_PUBLIC_ID).length() == 0) {
                el.setAttribute(ATTR_PUBLIC_ID, res.getPublicID(clazz));
            }
        } else {
            // plain convertor -> wrap content to CDATA block
            el = doc.createElement(ELM_DELEGATE);
            el.setAttribute(ATTR_PUBLIC_ID, res.getPublicID(clazz));
            el.appendChild(doc.createCDATASection(writeToString(c, obj, findContext(doc))));
        }
        
        // bind cached object with original element
        cache.elm = el;
        return el;
    }