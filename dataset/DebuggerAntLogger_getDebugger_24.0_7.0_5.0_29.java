private AntDebugger getDebugger (AntSession s, AntEvent antEvent) {
        AntDebugger d = (AntDebugger) runningDebuggers.get (s);
        if (d != null) return d;
        
        if (!filesToDebug.contains (s.getOriginatingScript ())) 
            return null;
        filesToDebug.remove (s.getOriginatingScript ());
        Reference execRef = (Reference) fileExecutors.remove(s.getOriginatingScript());
        ExecutorTask execTask = null;
        if (execRef != null) {
            execTask = (ExecutorTask) execRef.get();
        }
        
        // start debugging othervise
        FileObject fo = FileUtil.toFileObject (s.getOriginatingScript ());
        DataObject dob;
        try {
            dob = DataObject.find (fo);
        } catch (DataObjectNotFoundException ex) {
            Logger.getLogger(DebuggerAntLogger.class.getName()).log(Level.CONFIG, "No DataObject from "+fo, ex);
            return null;
        }
        AntProjectCookie antCookie = dob.getLookup().lookup(AntProjectCookie.class);
        if (antCookie == null)
            throw new NullPointerException ("No AntProjectCookie provided by "+dob);
        d = startDebugging (antCookie, antEvent, execTask);
        runningDebuggers.put (s, d);
        runningDebuggers2.put (d, s);
        return d;
    }