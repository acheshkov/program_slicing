void genConstructor(int out) throws IOException {
        select(out);
        String thrownExceptions = null;
        if (this.beanElement.isRoot && shouldThrowException()) {
            thrownExceptions = "org.netbeans.modules.schema2beans.Schema2BeansException";
        }
        jw.beginConstructor(className, "", thrownExceptions, jw.PUBLIC);
	gen("this(");
	if (this.beanElement.isRoot)
	    gen("null, ");
	gen("Common.USE_DEFAULT_VALUES)");
	eol();
	end(); cr();
	
	if (this.beanElement.isRoot) {
        jw.beginConstructor(className, "org.w3c.dom.Node doc, int options",
                            thrownExceptions, jw.PUBLIC);
        //
        // This call should never pass anything but NO_DEFAULT_VALUES, since
        // initFromNode will get the options that are specified.
        //
        jw.writeEol("this(Common.NO_DEFAULT_VALUES)");
        if (!shouldThrowException()) {
            gen("try ");
            begin();
        }
	    gen("initFromNode(doc, options)"); eol();
        if (!shouldThrowException()) {
            end();
            gen("catch (Schema2BeansException e) ");
            begin();
            gen("throw new RuntimeException(e)");
            eol();
            end();
        }
	    end();
	    // Make it so that initFromNode can be called from other
	    // methods in this class (like ones used for deserializing
	    // from a DOM tree).
	    gen(PROTECTED, VOID, "initFromNode(org.w3c.dom.Node doc, int options) throws Schema2BeansException"); cr();
	    begin();
	    gencr("if (doc == null)");
	    begin();
	    gen("doc = GraphManager.createRootElementNode(\"",
	    this.beanElement.node.getName(), "\")");
        eolNoI18N();
	    gencr("if (doc == null)");
	    
	    if (this.config.isStandalone()) {
            tabIn();
            gencrNoI18N("throw new Schema2BeansException(\"Cannot create DOM root\");");
	    } else {
            tabIn();
            gencr("throw new Schema2BeansException(Common.getMessage(");
            tabIn(); tabIn();
            gencr("\"CantCreateDOMRoot_msg\", \""+beanElement.node.getName()+"\"));");
	    }
	    end();
	    
	    gen("Node n = GraphManager.getElementNode(\"");
	    gen(this.beanElement.node.getName(), "\", doc)");
	    eolNoI18N();
	    gencr("if (n == null)");
	    if (this.config.isStandalone()) {
            tabIn();
            gen("throw new Schema2BeansException(\"Doc root not in the DOM graph\")");
            eolNoI18N();
	    } else {
            tabIn();
            gencr("throw new Schema2BeansException(Common.getMessage(");
            tabIn(); tabIn();
            gen("\"DocRootNotInDOMGraph_msg\", \""+beanElement.node.getName()+"\", doc.getFirstChild().getNodeName()))");
	    }
        eol();
        
	    cr();
	    gen("this.graphManager.setXmlDocument(doc)"); eol(); cr();
	    comment("Entry point of the createBeans() recursive calls");
	    gen("this.createBean(n, this.graphManager())"); eol();
	    gen("this.initialize(options)"); eol();
	    end();
	}
	
        if (this.beanElement.isExtended()) {
            gen(PROTECTED, this.className+"(Vector comparators, Version runtimeVersion)");
            begin();
            cr();
            jw.writeEol("super(comparators, runtimeVersion)");
            end();
        }
	gen(PUBLIC, this.className+"(int options)");
    /*
    if (this.beanElement.isRoot && shouldThrowException()) {
        gen(" throws Schema2BeansException ");
    }
    */
    cr();
	begin();
	//gen("super(", this.className, ".comparators");
	jw.writeEol("super(comparators, runtimeVersion)");
	if (this.beanElement.isRoot) {
	    gen("initOptions(options)"); eol();
	    end();
	    
	    gen(PROTECTED, VOID, "initOptions(int options)"); cr();
	    begin();
	    comment("The graph manager is allocated in the bean root");
	    gen("this.graphManager = new GraphManager(this)"); eol();
	    gen("this.createRoot(\"", this.beanElement.node.getName(), "\", \"");
	    gen(this.className, "\",");
        noI18N();  tabIn();
	    gen("Common.TYPE_1 | Common.TYPE_BEAN, ");
	    gen(this.className, ".class)"); eol(); cr();
	}
    }