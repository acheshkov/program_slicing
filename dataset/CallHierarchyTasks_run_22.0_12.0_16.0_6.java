@Override
                        public void run(CompilationController parameter) throws Exception {
                            synchronized (callback) {
                                rr.run(parameter);
                                callback.run(rr.getRoot());
                            }
                        }