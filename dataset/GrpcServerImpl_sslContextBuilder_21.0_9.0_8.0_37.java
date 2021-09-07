protected SslContextBuilder sslContextBuilder(GrpcTlsDescriptor tlsConfig) {
        Resource certResource = tlsConfig.tlsCert();
        Resource keyResource = tlsConfig.tlsKey();
        Resource caCertResource = tlsConfig.tlsCaCert();

        if (certResource == null) {
            throw new IllegalStateException("gRPC server is configured to use TLS but cert file is not set");
        }

        if (keyResource == null) {
            throw new IllegalStateException("gRPC server is configured to use TLS but key file is not set");
        }

        X509Certificate[] aX509Certificates;

        if (caCertResource != null) {
            try {
                aX509Certificates = loadX509Cert(caCertResource.stream());
            } catch (Exception e) {
                throw new IllegalStateException("gRPC server is configured to use TLS but failed to load trusted CA files");
            }

        } else {
            aX509Certificates = new X509Certificate[0];
        }

        SslContextBuilder sslContextBuilder = SslContextBuilder.forServer(certResource.stream(), keyResource.stream())
                .sslProvider(SslProvider.OPENSSL);

        if (aX509Certificates.length > 0) {
            sslContextBuilder.trustManager(aX509Certificates)
                    .clientAuth(ClientAuth.REQUIRE);
        } else {
            sslContextBuilder.clientAuth(ClientAuth.OPTIONAL);
        }

        return GrpcSslContexts.configure(sslContextBuilder);
    }