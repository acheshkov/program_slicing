public Observable<ServiceResponseWithHeaders<Void, JobAddHeaders>> addWithServiceResponseAsync(JobAddParameter job) {
        if (this.client.batchUrl() == null) {
            throw new IllegalArgumentException("Parameter this.client.batchUrl() is required and cannot be null.");
        }
        if (job == null) {
            throw new IllegalArgumentException("Parameter job is required and cannot be null.");
        }
        if (this.client.apiVersion() == null) {
            throw new IllegalArgumentException("Parameter this.client.apiVersion() is required and cannot be null.");
        }
        Validator.validate(job);
        final JobAddOptions jobAddOptions = null;
        Integer timeout = null;
        UUID clientRequestId = null;
        Boolean returnClientRequestId = null;
        DateTime ocpDate = null;
        String parameterizedHost = Joiner.on(", ").join("{batchUrl}", this.client.batchUrl());
        DateTimeRfc1123 ocpDateConverted = null;
        if (ocpDate != null) {
            ocpDateConverted = new DateTimeRfc1123(ocpDate);
        }
        return service.add(job, this.client.apiVersion(), this.client.acceptLanguage(), timeout, clientRequestId, returnClientRequestId, ocpDateConverted, parameterizedHost, this.client.userAgent())
            .flatMap(new Func1<Response<ResponseBody>, Observable<ServiceResponseWithHeaders<Void, JobAddHeaders>>>() {
                @Override
                public Observable<ServiceResponseWithHeaders<Void, JobAddHeaders>> call(Response<ResponseBody> response) {
                    try {
                        ServiceResponseWithHeaders<Void, JobAddHeaders> clientResponse = addDelegate(response);
                        return Observable.just(clientResponse);
                    } catch (Throwable t) {
                        return Observable.error(t);
                    }
                }
            });
    }